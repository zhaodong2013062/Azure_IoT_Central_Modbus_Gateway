# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json

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

    def __init__(self, scope_id, app_key, device_id, device_name, slave_id, active_registers, logger, model_id=''):
        super(SlaveDevice, self).__init__(scope_id, app_key, device_id, device_name, logger, model_id)
        
        self.slave_id = slave_id
        self.active_registers = {}
        self.read_registers = []

        for active_register in active_registers:
            name = active_register[config.ACTIVE_REGISTERS_KEY_REGISTER_NAME]
            address = active_register[config.ACTIVE_REGISTERS_KEY_ADDRESS]
            type = active_register[config.ACTIVE_REGISTERS_KEY_TYPE]
            self.active_registers[name] = ActiveRegister(address, type)

            if type == config.ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT or \
               type == config.ACTIVE_REGISTERS_TYPE_INPUT_REGISTER:
                self.read_registers.append(name)

    def report_all_read_registers(self, modbus_client):
        """ Reports the value of all read registers to IoT Central
        """
        self.report_registers(modbus_client, self.read_registers)

    def report_registers(self, modbus_client, register_names):
        """ Reports the value of specified registers to IoT Central
        """
        payload_components = [""]*len(register_names)
        for index, name in enumerate(register_names):
            payload_components[index] = self._get_register_payload_component(modbus_client, name)
        payload = '{{{0}}}'.format(",".join(payload_components))
        self.send_telemetry(self.device_id, payload)

    def desired_ack(self, json_data, status_code, status_text):
        """ Perform actions and send acknowledgement on receipt of a desired property
        """
        # respond with IoT Central confirmation
        key_index = json_data.keys().index('$version')
        if key_index == 0:
            key_index = 1
        else:
            key_index = 0

        the_value = json_data[json_data.keys()[key_index]]['value']
        if type(the_value) is bool:
            if the_value:
                the_value = "true"
            else:
                the_value = "false" 

        reported_payload = '{{"{}":{{"value":{},"statusCode":{},"status":"{}","desiredVersion":{}}}}}'.format(json_data.keys()[key_index], the_value, status_code, status_text, json_data['$version'])
        self.send_reported_property(reported_payload)

 
    def _get_register_payload_component(self, modbus_client, register_name):
        """ Gets a payload component of the form: "register_name" : <value>
        """
        address = self.active_registers[register_name].address
        type = self.active_registers[register_name].type
        value = modbus_client.read_register(type, self.slave_id, address)
        return '"{0}":{1}'.format(register_name, value)