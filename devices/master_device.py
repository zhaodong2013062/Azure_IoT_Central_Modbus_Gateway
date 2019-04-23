# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import json
import time

import config
from device import Device, ProcessDesiredTwinResponse
from modbus import SimulatedModbusDeviceClient, SerialModbusDeviceClient, TCPModbusDeviceClient
from slave_device import SlaveDevice


class MasterDevice(Device):

    slaves = []

    def __init__(self, scope_id, app_key, model_id, device_id, logger):
        model_data = Device._create_model_data(model_id, None, True)
        super(MasterDevice, self).__init__(scope_id, app_key, device_id, model_data, logger)
        self.modbus_client = SerialModbusDeviceClient(method='rtu', port=config.SERIAL_PORT, 
            timeout=config.MODBUS_CLIENT_TIMEOUT, baudrate=config.BAUD_RATE)

    def kill_slaves(self):
        """ Disconnect and stop threads for all slave devices
        """
        self.logger.info('Killing slaves of %s: %s', self.device_id, [s.device_id for s in self.slaves])
        for slave in self.slaves:
            slave.stop()
        self.slaves = []

    def _process_setting(self, key, value):
        """ Process provided config file
        """
        # Create slave devices if config file is sent
        if key == config.KEY_CONFIG:
            self.logger.info('Received config file: \n%s', value)
            try:
                config_json = json.loads(value)
                self._init_slaves(config_json)
                self.logger.info('Initialized slaves: %s', [s.device_id for s in self.slaves])
                return ProcessDesiredTwinResponse()
            except (ValueError, KeyError) as e:
                status_text = 'ValueError or KeyError has occured while parsing JSON: {}'.format(e)
                self.logger.error(status_text)
                return ProcessDesiredTwinResponse(400, status_text)
            except Exception as e:
                status_text = 'Error has occured in processing config file: {}.'.format(e)
                self.logger.error(status_text)
                return ProcessDesiredTwinResponse(500, status_text)
        else:
            return ProcessDesiredTwinResponse()

    def _init_slaves(self, config_json):
        """ Kills old slaves and replaces them with new slaves specified in the config 
        """
        new_slaves = []
        # TODO: validate config for address collisions
        for slave in config_json[config.CONFIG_KEY_SLAVES]:
            self.logger.info('Initializing slave %s', slave[config.CONFIG_KEY_DEVICE_ID])
            slave = SlaveDevice(
                self.scope_id,
                self.app_key,
                config_json.get(config.CONFIG_KEY_MODEL_ID, ''),
                slave[config.CONFIG_KEY_DEVICE_ID],
                self.device_id,
                slave[config.CONFIG_KEY_SLAVE_ID],
                config_json[config.CONFIG_KEY_ACTIVE_REGISTERS],
                config_json.get(config.CONFIG_KEY_UPDATE_INTERVAL),
                self.modbus_client,
                self.logger)
            new_slaves.append(slave)

        self.kill_slaves()
        self.slaves = new_slaves
        [s.start() for s in new_slaves]

    def _cleanup(self):
        self.kill_slaves()
