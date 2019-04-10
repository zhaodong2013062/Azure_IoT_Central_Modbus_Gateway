# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json
import time

from device import Device, ProcessDesiredTwinResponse
from slave_device import SlaveDevice
from modbus import ModbusDeviceClient, FakeModbusDeviceClient
import config

class MasterDevice(Device):

    slaves = []

    def __init__(self, scope_id, app_key, model_id, device_id, device_name, logger):
        super(MasterDevice, self).__init__(scope_id, app_key, device_id, model_id, device_name, logger)
        self.modbus_client = ModbusDeviceClient(method='rtu', port=config.SERIAL_PORT, 
            timeout=config.MODBUS_CLIENT_TIMEOUT, baudrate=config.BAUD_RATE)

    def kill_slaves(self):
        for slave in self.slaves:
            slave.stop()
        self.slaves = []

    def _process_desired_twin(self, json_data):
        """ Process provided config file
        """
        # Create slave devices if config file is sent
        if config.CONFIG_KEY in json_data:
            config_string = json_data[config.CONFIG_KEY][config.VALUE_KEY]
            self.logger.info('Received config file: \n%s', config_string)
            try:
                config_json = json.loads(config_string)
                self._init_slaves(config_json)
                return ProcessDesiredTwinResponse()
            except (ValueError, KeyError) as e:
                status_text = 'ValueError or KeyError has occured on value/key: {}'.format(e)
                self.logger.error(status_text)
                return ProcessDesiredTwinResponse(400, status_text)
            except Exception as e:
                status_text = 'Error has occured in processing config file: {}.'.format(e)
                self.logger.error(status_text)
                return ProcessDesiredTwinResponse(500, status_text)

    def _init_slaves(self, config_json):
        """ Kills old slaves and replaces them with new slaves specified in the config 
        """
        new_slaves = []
        # TODO: validate config for address collisions
        for slave in config_json[config.CONFIG_KEY_SLAVES]:
            self.logger.info('Initializing slave %s', slave[config.CONFIG_KEY_DEVICE_NAME])
            slave = SlaveDevice(
                self.scope_id,
                self.app_key,
                config_json.get(config.CONFIG_KEY_MODEL_ID, ''),
                slave[config.CONFIG_KEY_DEVICE_ID],
                slave[config.CONFIG_KEY_DEVICE_NAME],
                slave[config.CONFIG_KEY_SLAVE_ID],
                config_json[config.CONFIG_KEY_ACTIVE_REGISTERS],
                config_json.get(config.CONFIG_KEY_UPDATE_INTERVAL),
                self.modbus_client,
                self.logger)
            new_slaves.append(slave)

        self.kill_slaves()
        self.slaves = new_slaves
        [s.start() for s in new_slaves]

    def _loop(self):
        time.sleep(5)
        while self._active:
            self.client.loop()

    def _cleanup(self):
        self.kill_slaves()