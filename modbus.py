#!/usr/bin/env python
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

UNIT = 0x00
TEMPADDR = 0x00
HUMADDR = 0x01
THERMADDR = 0x00

class ModbusDeviceClient:
    """ Class to get/set sensor/actuator values to/from slaves of the Modbus gateway
    """
    def __init__(self, method, port, timeout, baudrate):
        self.client = ModbusClient(method=method, port=port, timeout=timeout, 
            baudrate=baudrate)
        self.client.connect()

    def getTemperature(self, slaveId):
        return self.__readInputRegister(TEMPADDR, slaveId)
    
    def getHumidity(self, slaveId):
        return self.__readInputRegister(HUMADDR, slaveId)

    def getThermostat(self, slaveId):
        return self.__readInputRegister(THERMADDR, slaveId)

    def setThermostat(self, slaveId, thermostatValue):
        self.__setHoldingRegister(THERMADDR, slaveId, thermostatValue)

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