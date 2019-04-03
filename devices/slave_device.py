# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json
import time
import threading

from device import Device
import config

class ActiveRegister:
    def __init__(self, address, type):
        self.address = address
        self.type = type

class SlaveDevice(Device):
    
    active_registers = None
    read_registers = None
    slave_id = None

    _last_telemetry_sent = None

    def __init__(self, scope_id, app_key, device_id, device_name, slave_id, active_registers, modbus_client, logger, model_id=''):
        super(SlaveDevice, self).__init__(scope_id, app_key, device_id, device_name, logger, model_id)
        
        self.slave_id = slave_id
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

    def report_all_read_registers(self):
        """ Reports the value of all read registers to IoT Central
        """
        self.report_registers(self.read_registers)

    def report_registers(self, register_names):
        """ Reports the value of specified registers to IoT Central
        """
        payload_components = [""]*len(register_names)
        for index, name in enumerate(register_names):
            payload_components[index] = self._get_register_payload_component(name)
        payload = '{{{0}}}'.format(",".join(payload_components))
        self._send_telemetry(self.device_id, payload)

    def write_register(self, register_name, value):
        """ Writes to a coil or holding register
        """
        address = self.active_registers[register_name].address
        type = self.active_registers[register_name].type
        self.modbus_client.write_register(type, self.slave_id, address, value)

    def _desired_ack(self, json_data, status_code, status_text):
        """ Perform actions and send acknowledgement on receipt of a desired property
        """
        # respond with IoT Central confirmation
        key_index = json_data.keys().index(config.VERSION_KEY)
        if key_index == 0:
            key_index = 1
        else:
            key_index = 0

        key = json_data.keys()[key_index]

        value = json_data[key][config.VALUE_KEY]
        if type(value) is bool:
            if value:
                value = "true"
            else:
                value = "false" 

        if key in self.active_registers.keys():
            self.write_register(key, value)

        reported_payload = '{{"{}":{{"value":{},"statusCode":{},"status":"{}","desiredVersion":{}}}}}'.format(json_data.keys()[key_index], value, status_code, status_text, json_data['$version'])
        self.send_reported_property(reported_payload)
 
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
            if int(time.time()) - _last_telemetry_sent >= 5:
                self.report_all_read_registers()
                _last_telemetry_sent = time.time()
            self.client.loop()
