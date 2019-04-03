# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json
import time

from device import Device
from slave_device import SlaveDevice
from modbus import ModbusDeviceClient, FakeModbusDeviceClient
import config

class MasterDevice(Device):

    slaves = []

    def __init__(self, scope_id, app_key, device_id, device_name, logger, model_id=''):
        super(MasterDevice, self).__init__(scope_id, app_key, device_id, device_name, logger, model_id)
        self.modbus_client = FakeModbusDeviceClient(method='rtu', port=config.SERIAL_PORT, 
            timeout=1, baudrate=config.BAUD_RATE)

    def kill_slaves(self):
        for slave in self.slaves:
            slave.stop()

    def _get_twin_callback(self, client, userdata, msg):
        if super(MasterDevice, self)._get_twin_callback(client, userdata, msg) == self.get_twin_rid:
            twin_json = json.loads(self.twin)
            if config.DESIRED_TWIN_KEY in twin_json and \
            config.CONFIG_KEY in twin_json[config.DESIRED_TWIN_KEY] and \
            config.VALUE_KEY in twin_json[config.DESIRED_TWIN_KEY][config.CONFIG_KEY]:
                config_json = json.loads(twin_json[config.DESIRED_TWIN_KEY][config.CONFIG_KEY][config.VALUE_KEY])
                self._init_slaves(config_json)

    def _desired_ack(self, json_data, status_code, status_text):
        """ Process the incoming config file for slave devices 
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

        # Create slave devices if config file is sent
        if key == config.CONFIG_KEY:
            self.logger.info('Received config file: \n%s', value)
            config_json = None
            try:
                config_json = json.loads(value)
                self.slaves = []
                self._init_slaves(config_json)
            except ValueError as e:
                status_text = "Config file could not be parsed as JSON: {}".format(e)
                self.logger.error(status_text)
                status_code = 400
            value = "'" + value + "'"

        reported_payload = '{{"{}":{{"value":{},"statusCode":{},"status":"{}","desiredVersion":{}}}}}'.format(json_data.keys()[key_index], value, status_code, status_text, json_data['$version'])
        self.send_reported_property(reported_payload)

    def _init_slaves(self, config_json):
        """ Kills old slaves and replaces them with new slaves specified in the config 
        """
        self.kill_slaves()
        # TODO: validate config for address collisions
        for slave in config_json[config.CONFIG_KEY_SLAVES]:
            self.logger.info('Initializing slave %s', slave[config.CONFIG_KEY_DEVICE_NAME])
            slave = SlaveDevice(
                self.scope_id,
                self.app_key, 
                slave[config.CONFIG_KEY_DEVICE_ID],
                slave[config.CONFIG_KEY_DEVICE_NAME],
                slave[config.CONFIG_KEY_SLAVE_ID],
                config_json[config.CONFIG_KEY_ACTIVE_REGISTERS],
                self.modbus_client,
                self.logger,
                model_id=config_json[config.CONFIG_KEY_MODEL_ID])
            self.slaves.append(slave)
            slave.start()

    def _loop(self):
        time.sleep(5)
        while self._active:
            self.client.loop()

    def _cleanup(self):
        self.kill_slaves()