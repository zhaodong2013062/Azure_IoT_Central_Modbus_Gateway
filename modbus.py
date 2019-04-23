#!/usr/bin/env python
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from random import randint
import os
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from retrying import retry
from abc import abstractmethod

import config


def _retry_if_modbus_exception(exception):
    return isinstance(exception, ModbusException)

class InvalidRegisterTypeException(Exception):
    def __init__(self, register_type):
        self.message = 'Invalid register type {}.'.format(register_type)

class SimulatedModbusDeviceClient:
    """ Simulated Modbus client for testing, returns random values on reads and prints on writes
    """
    def __init__(self, method, port, timeout, baudrate):
        pass
    
    def read_register(self, register_type, slave_id, address):
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return randint(0, 1)
        else:
            return randint(0, 100)

    def write_register(self, register_type, slave_id, address, value):
        print 'simluate writing {} to slave {} address {}'.format(value, slave_id, address)

class ModbusDeviceClient(object):
    """ Static base class for common/read write methods
    """

    @abstractmethod
    def read_register(self, register_type, slave_id, address):
        """ Read a register of specified type, slave id, address
        """
        pass
    
    @abstractmethod
    def write_register(self, registe_type, slave_id, address, value):
        """ Write a value to a register of specified type, slave id, address
        """
        pass

    @staticmethod
    @retry(wait_fixed=config.MODBUS_RETRY_WAIT, retry_on_exception=_retry_if_modbus_exception, stop_max_attempt_number=config.MODBUS_RETRY_ATTEMPTS)
    def _read_register(client, register_type, slave_id, address):
        if register_type == config.ACTIVE_REGISTERS_TYPE_COIL:
            result = client.read_coils(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT:
            result = client.read_discrete_inputs(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_INPUT_REGISTER:
            result = client.read_input_registers(address, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER:
            result = client.read_holding_registers(address, unit=slave_id)
        else: 
            raise InvalidRegisterTypeException(register_type)

        if result.isError():
            raise result
        
        if register_type in config.ACTIVE_REGISTERS_BIT_TYPES:
            return result.bits[0]
        else:
            return result.registers[0]

    @staticmethod
    @retry(wait_fixed=config.MODBUS_RETRY_WAIT, retry_on_exception=_retry_if_modbus_exception, stop_max_attempt_number=config.MODBUS_RETRY_ATTEMPTS)
    def _write_register(client, register_type, slave_id, address, value):
        if register_type in config.ACTIVE_REGISTERS_READONLY_TYPES:
            raise InvalidRegisterTypeException(register_type)
        
        if register_type == config.ACTIVE_REGISTERS_TYPE_COIL:
            result = client.write_coil(address, value, unit=slave_id)
        elif register_type == config.ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER:
            result = client.write_register(address, value, unit=slave_id)
        else:
            raise InvalidRegisterTypeException(register_type)
        
        if result.isError():
            raise result

class TCPModbusDeviceClient(ModbusDeviceClient):
    """ Client for Modbus over TCP/IP. Creates connection on the first time 
        communicating with a slave. Slave ID in this case is the IP address.
    """

    cache = None
    def __init__(self):
        self.cache = dict()
        
    def read_register(self, register_type, slave_id, address):
        if slave_id not in self.cache:
            self.cache[slave_id] = ModbusTcpClient(host=slave_id)
            if not self.cache[slave_id].connect():
                raise "Connection failed to {}".format(slave_id)

        return ModbusDeviceClient._read_register(self.cache[slave_id], register_type, slave_id, address)

    def write_register(self, register_type, address, slave_id, value):
        if slave_id not in self.cache:
            self.cache[slave_id] = ModbusTcpClient(host=slave_id)
            if not self.cache[slave_id].connect():
                raise "Connection failed to {}".format(slave_id)

        ModbusDeviceClient._write_register(self.cache[slave_id], register_type, slave_id, address, value)

class SerialModbusDeviceClient(ModbusDeviceClient):
    """ Client for Modbus over Serial
    """

    def __init__(self, method, port, timeout, baudrate):
        self.client = ModbusSerialClient(method=method, port=port, timeout=timeout, 
            baudrate=baudrate)
        self.client.connect()
        #os.system('sudo set-rs485 /dev/ttyAP1 1')

    def read_register(self, register_type, slave_id, address):
        return ModbusDeviceClient._read_register(self.client, register_type, int(slave_id), int(address))
    
    def write_register(self, register_type, slave_id, address, value):
        ModbusDeviceClient._write_register(self.client, register_type, int(slave_id), int(address), int(value))
