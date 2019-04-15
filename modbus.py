#!/usr/bin/env python
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from random import randint

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
from retrying import retry

import config


def _retry_if_modbus_exception(exception):
    return isinstance(exception, ModbusException)

class InvalidRegisterTypeException(Exception):
    pass

# Class used to simulate modbus devices
class FakeModbusDeviceClient:
    def __init__(self, method, port, timeout, baudrate):
        pass
    
    def read_register(self, register_type, slave_id, address):
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return randint(0, 1)
        else:
            return randint(0, 100)

    def write_register(self, register_type, slave_id, address, value):
        print 'fake writing {} to slave {} address {}'.format(value, slave_id, address)

class ModbusDeviceClient:
    """ Class to get/set sensor/actuator values to/from slaves of the Modbus gateway
    """
    def __init__(self, method, port, timeout, baudrate):
        self.client = ModbusClient(method=method, port=port, timeout=timeout, 
            baudrate=baudrate)
        self.client.connect()

    @retry(wait_fixed=config.MODBUS_RETRY_WAIT, retry_on_exception=_retry_if_modbus_exception, stop_max_attempt_number=config.MODBUS_RETRY_ATTEMPTS)
    def read_register(self, register_type, slave_id, address):
        """ Read a register of specified type, slave id, address
        """
        if register_type == config.ACTIVE_REGISTERS_TYPE_COIL:
            result = self.client.read_coils(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT:
            result = self.client.read_discrete_inputs(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_INPUT_REGISTER:
            result = self.client.read_input_registers(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER:
            result = self.client.read_holding_registers(address, unit=slave_id)
        else: 
            raise Exception('Invalid register type {}.', register_type)

        if result.isError():
            raise result
        
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return result.bits[0]
        else:
            return result.registers[0]

    @retry(wait_fixed=config.MODBUS_RETRY_WAIT, retry_on_exception=_retry_if_modbus_exception, stop_max_attempt_number=config.MODBUS_RETRY_ATTEMPTS)
    def write_register(self, register_type, slave_id, address, value):
        """ Write a value to a register of specified type, slave id, address
        """
        if register_type in config.ACTIVE_REGISTERS_READONLY_TYPES:
            raise Exception('Invlaid readonly register type: {}', register_type)
        
        if register_type == config.ACTIVE_REGISTERS_TYPE_COIL:
            self.client.write_coil(address, value, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER:
            self.client.write_register(address, value, unit=slave_id)
        else:
            raise InvalidRegisterTypeException('Invalid register type {}.', register_type)
