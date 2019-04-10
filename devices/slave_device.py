# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json
import time
import threading
from pymodbus.exceptions import ModbusException

from modbus import InvalidRegisterTypeException
from device import Device, ProcessDesiredTwinResponse
import config

class ActiveRegister:
    def __init__(self, address, type):
        self.address = address
        self.type = type

class SlaveDevice(Device):
    
    active_registers = None
    read_registers = None
    slave_id = None
    update_interval = None

    _last_telemetry_sent = None

    def __init__(self, scope_id, app_key, model_id, device_id, device_name, slave_id, active_registers, update_interval, modbus_client, logger):
        super(SlaveDevice, self).__init__(scope_id, app_key, device_id, model_id, device_name, logger)
        
        self.slave_id = slave_id
        self.update_interval = 1 if update_interval == None else update_interval
        self.active_registers = {}
        self.read_registers = []
        self.modbus_client = modbus_client

        for active_register in active_registers:
            name = active_register[config.ACTIVE_REGISTERS_KEY_REGISTER_NAME]
            address = active_register[config.ACTIVE_REGISTERS_KEY_ADDRESS]
            type = active_register[config.ACTIVE_REGISTERS_KEY_TYPE]
            self.active_registers[name] = ActiveRegister(address, type)

            if type == config.ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT or \
               type == config.ACTIVE_REGISTERS_TYPE_INPUT_REGISTER:
                self.read_registers.append(name)

    def report_all_registers(self):
        """ Reports the value of all active registers to IoT Central
        """
        self.report_registers(self.active_registers.keys())

    def report_all_read_registers(self):
        """ Reports the value of all read registers to IoT Central
        """
        self.report_registers(self.read_registers)

    def report_registers(self, register_names):
        """ Reports the value of specified registers to IoT Central
        """
        payload_components = [""]*len(register_names)
        for index, name in enumerate(register_names):
            try:
                payload_components[index] = self._get_register_payload_component(name)
            except ModbusException as e:
                self.logger.error('Modbus device read failed with %s', e)
        payload = '{{{0}}}'.format(",".join(payload_components))
        self.send_telemetry(self.device_id, payload)

    def write_register(self, register_name, value):
        """ Writes to a coil or holding register
        """
        address = self.active_registers[register_name].address
        type = self.active_registers[register_name].type
        self.modbus_client.write_register(type, self.slave_id, address, value)

    def _process_desired_twin(self, json_data):
        """ Writes the provided value to the specified register
        """
        try:
            for key in json_data.keys():
                if key in self.active_registers:
                    value = json_data[key][config.VALUE_KEY]
                    self.write_register(key, value)
            return ProcessDesiredTwinResponse()
        except InvalidRegisterTypeException as e:
            self.logger.error(e.message)
            return ProcessDesiredTwinResponse(400, e.message)
        except Exception as e:
            status_text = "Error has occured in processing settings: {}.".format(e)
            self.logger.error(status_text)
            return ProcessDesiredTwinResponse(500, status_text)
 
    def _get_register_payload_component(self, register_name):
        """ Gets a payload component of the form: "register_name" : <value>
        """
        address = self.active_registers[register_name].address
        type = self.active_registers[register_name].type
        value = self.modbus_client.read_register(type, self.slave_id, address)
        return '"{0}":{1}'.format(register_name, value)

    def _loop(self):
        _last_telemetry_sent = time.time()
        while self._active:
            if int(time.time()) - _last_telemetry_sent >= self.update_interval:
                self.report_all_registers()
                _last_telemetry_sent = time.time()
            self.client.loop()
