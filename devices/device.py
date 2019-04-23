# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import base64
import hashlib
import hmac
import json
import threading
import time
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from time import sleep

import iotc
from iotc import IOTConnectType, IOTLogLevel

import config
from modbus import ModbusDeviceClient

ProcessDesiredTwinResponse = namedtuple('ProcessDesiredTwinResponse', 'status_code status_text')
ProcessDesiredTwinResponse.__new__.__defaults__ = (200, 'completed')

class Device(object):
    logger = None
    client = None
    modbus_client = None    
    device_thread = None

    scope_id = None
    appKey = None
    device_id = None
    model_data = None

    _active = False
    _last_updated_sas_token = None

    def __init__(self, scope_id, app_key, device_id, model_data, logger):
        self.scope_id = scope_id
        self.app_key = app_key
        self.device_id = device_id
        self.logger = logger

        device_key = Device._compute_derived_symmetric_key(self.app_key, self.device_id)
        self.client = iotc.Device(self.scope_id, device_key, self.device_id, IOTConnectType.IOTC_CONNECT_SYMM_KEY)
        self.client.setLogLevel(IOTLogLevel.IOTC_LOGGING_API_ONLY)
        self.client.setModelData(model_data)

        # set callbacks
        self.client.on('ConnectionStatus', self._on_connect)
        self.client.on('MessageSent', self._on_message_sent)
        self.client.on('Command', self._on_command)
        self.client.on('SettingsUpdated', self._on_settings_updated)

    def start(self):
        """ Starts the loop thread
        """
        self.logger.info('Starting loop for device %s', self.device_id)
        self.client.connect()
        thread = threading.Thread(target=self._loop)
        self._active = True
        thread.start()
        self.device_thread = thread
        self.logger.info('Started loop for device %s', self.device_id)

    def stop(self):
        """ Stops the loop thread
        """
        self.logger.info('Stopping loop for device %s', self.device_id)
        self._cleanup()
        self._active = False
        if self.device_thread != None:
            self.device_thread.join(1)
            self.device_thread = None
        self.client.disconnect()
        self.logger.info('Stopped loop for device %s', self.device_id)

    #region Callback Handlers
    def _on_connect(self, info):
        if not info.getStatusCode():
            self.logger.info('Connected/Disconnected %s successfully', self.device_id)
        else:
            self.logger.error('Failed to connect %s with error %s: %s', self.device_id, info.getStatusCode(),
                info.getPayload())
        
    def _on_message_sent(self, info):
        if not info.getStatusCode():
            self.logger.info('Sent message for %s successfully %s', self.device_id, info.getPayload())
        else:
            self.logger.error('Failed to send message for %s with error %s: %s', self.device_id, info.getStatusCode(),
                info.getPayload())
    
    def _on_command(self, info):
        self.logger.info('Received command for %s: %s', self.device_id, info.getPayload())

    def _on_settings_updated(self, info):
        key = info.getTag()
        setting = json.loads(info.getPayload())
        
        if config.KEY_VERSION not in setting:
            self.logger.debug('Ignoring reported property for %s. %s: %s', self.device_id, key, setting)
            return

        self.logger.info('Settings updated for %s. %s: %s', self.device_id, key, setting)
        value = setting[config.KEY_VERSION]
        self._process_setting(key, value)
   #endregion

    def _process_setting(self, key, setting):
        """ Process a json object representing the desired twin
        """
        return ProcessDesiredTwinResponse()
        
    def _do_loop_actions(self):
        pass

    def _loop(self):
        """ Background loop for the device
        """
        while self._active:
            if self.client.isConnected():
                self.client.doNext()
                self._do_loop_actions()
            else:
                self.logger.info('Connection was lost for %s. Reconnecting...', self.device_id)
                self.client.connect()
                time.sleep(3)

    def _cleanup(self):
        """ Clean up on exit
        """
        pass

    @staticmethod
    def _compute_derived_symmetric_key(app_key, deviceId):
        """ Compute a device key using the application key and the device identity
        """
        app_key = base64.b64decode(app_key)
        return base64.b64encode(hmac.new(app_key, msg=deviceId.encode('utf8'), digestmod=hashlib.sha256).digest())

    @staticmethod
    def _is_json(string):
        if not isinstance(string, str):
            return False
        try:
            json.loads(string)
        except ValueError:
            return False
        return True

    @staticmethod
    def _create_model_data(model_id, gateway_id, is_gateway):
        """ Creates the model data payload (in string format) for provisioning the master or slave device
        """
        if is_gateway:
            assert(gateway_id == None)
        else:
            assert(gateway_id != None)

        model_data = {
            config.KEY_MODEL_ID: model_id, 
            config.KEY_GATEWAY: {
                config.KEY_GATEWAY_ID: gateway_id,
                config.KEY_IS_GATEWAY: 'true' if is_gateway else 'false'
            }
        }
        return str(model_data)
