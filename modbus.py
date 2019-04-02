#!/usr/bin/env python
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from random import randint

import config

class FakeModbusDeviceClient:
    def __init__(self, method, port, timeout, baudrate):
        pass
    
    def read_register(self, register_type, slave_id, address):
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return randint(0, 1)
        else:
            return randint(0, 100)

    def write_register(self, register_type, slave_id, address, value):
        print 'writing {} to slave {} address {}'.format(value, slave_id, address)

class ModbusDeviceClient:
    """ Class to get/set sensor/actuator values to/from slaves of the Modbus gateway
    """
    def __init__(self, method, port, timeout, baudrate):
        self.client = ModbusClient(method=method, port=port, timeout=timeout, 
            baudrate=baudrate)
        self.client.connect()

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
            raise Exception("Invalid register type {}.", register_type)

        if result.isError():
            raise result
        
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return result.bits[0]
        else:
            return result.registers[0]

    def __readInputRegister(self, address, slaveId):
        result = self.client.read_input_registers(address, 1, unit=slaveId)
        if result.isError():
            raise result
        return result.registers[0]

    def __setHoldingRegister(self, address, slaveId, value):
        result = self.client.write_register(address, value, unit=slaveId)
        if result.isError():
            raise result
        return result
