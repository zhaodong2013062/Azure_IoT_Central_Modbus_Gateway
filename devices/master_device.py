# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json

from device import Device
from slave_device import SlaveDevice
from modbus import ModbusDeviceClient, FakeModbusDeviceClient
import config

class MasterDevice(Device):

    slaves = []
    modbus_client = None

    def __init__(self, scope_id, app_key, device_id, device_name, logger, model_id=''):
        super(MasterDevice, self).__init__(scope_id, app_key, device_id, device_name, logger, model_id)
        self.modbus_client = FakeModbusDeviceClient(method='rtu', port=config.SERIAL_PORT, 
            timeout=1, baudrate=config.BAUD_RATE)

    def report_all_slaves(self):
        for slave in self.slaves:
            slave.report_all_read_registers(self.modbus_client)

    def desired_ack(self, json_data, status_code, status_text):
        """ Process the incoming config file for slave devices 
        """
        # respond with IoT Central confirmation
        key_index = json_data.keys().index('$version')
        if key_index == 0:
            key_index = 1
        else:
            key_index = 0

        key = json_data.keys()[key_index]
        value = json_data[key]['value']
        if type(value) is bool:
            if value:
                value = "true"
            else:
                value = "false"

        if key == "echo":
            self.logger.info("Recieved echo %s", value)

        # Create slave devices if config file is sent
        if key == config.CONFIG_KEY:
            self.logger.info('Received config file: \n%s', value)
            config_json = json.loads(value)
            self.slaves = []
            for slave in config_json:
                self._add_slave(slave)
            value = '"' + str(value) + '"'

        reported_payload = '{{"{}":{{"value":{},"statusCode":{},"status":"{}","desiredVersion":{}}}}}'.format(json_data.keys()[key_index], value, status_code, status_text, json_data['$version'])
        self.send_reported_property(reported_payload)

    def _add_slave(self, slave):
        """ Adds a slave to the list of slaves
        """
        self.slaves.append(SlaveDevice(
            slave[config.CONFIG_KEY_SCOPE_ID],
            slave[config.CONFIG_KEY_APP_KEY], 
            slave[config.CONFIG_KEY_DEVICE_ID],
            slave[config.CONFIG_KEY_DEVICE_NAME],
            slave[config.CONFIG_KEY_SLAVE_ID],
            slave[config.CONFIG_KEY_ACTIVE_REGISTERS],
            self.logger,
            slave[config.CONFIG_KEY_MODEL_ID])) 
