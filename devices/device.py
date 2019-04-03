# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from abc import ABCMeta, abstractmethod
import paho.mqtt.client as mqtt
from time import sleep
import ssl
import json
import base64
import hmac
import time
import binascii
import hashlib
import threading

from modbus import ModbusDeviceClient
import azure_iot_dps as dps
import config

class Device(object):
    registration_done = False
    connected = False
    iot_hub_hostname = ''
    logger = None
    client = None
    modbus_client = None
    twin = None
    token_expiry = None
    device_thread = None

    scope_id = None
    appKey = None
    device_id = None
    device_name = None
    model_id = None

    # Static constants
    qos_policy = 1
    retain_policy = False
    get_twin_rid = 20
    reported_rid = 10

    _active = False

    # TODO: Refresh SAS token
    def __init__(self, scope_id, app_key, device_id, device_name, logger, model_id=''):
        self.scope_id = scope_id
        self.app_key = app_key
        self.device_id = device_id
        self.logger = logger
        self.model_id = model_id
        self.device_name = device_name

        if model_id == '':
            dps.getConnectionString(self.device_id, self.app_key, self.scope_id, True, self._dps_registration_callback)
        else:
            dps.getConnectionString(self.device_id, self.app_key, config.SCOPE_ID, True, 
                self._dps_registration_callback, config.MODEL_ID)

        while not self.registration_done:
            sleep(0.05)

        self.logger.info('Creating new MQTT instance for device %s with id %s',  device_name, device_id)
        self.client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

        # setup Paho for secure MQTT
        if config.VALIDATE_CERT:
            self.client.tls_set(ca_certs=config.PATH_TO_ROOT_CERT, certfile=None, keyfile=None, 
                cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
        else:
            self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=None, 
                tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
        self.client.tls_insecure_set(False)

        # set callbacks
        self.client._on_connect = self._on_connect
        self.client._on_disconnect = self._on_disconnect
        self.client._on_message = self._on_message
        self.client._on_publish = self._on_publish

        # initial _connect to Azure IoT Hub
        self._connect()

        # initialize twin support
        self.client.subscribe('$iothub/twin/res/#')
        self.client.message_callback_add('$iothub/twin/res/#', self._get_twin_callback)

        # desired properties subscribe
        self.client.subscribe('$iothub/twin/PATCH/properties/desired/#')
        self.client.message_callback_add('$iothub/twin/PATCH/properties/desired/#', self._desired_twin_callback)

        # Direct method subscribe
        self.client.subscribe('$iothub/methods/POST/#')
        self.client.message_callback_add('$iothub/methods/POST/#', self._direct_method_callback)

        # Cloud to Device message subscribe
        self.client.subscribe('devices/{}/messages/devicebound/#'.format(config.DEVICE_NAME))
        self.client.message_callback_add('devices/{}/messages/devicebound/#'.format(config.DEVICE_NAME), self._c2d_callback)

        # force a twin pull
        self._get_twin()

    def start(self):
        """ Starts the loop thread
        """
        self.logger.info('Starting loop for device %s', self.device_name)
        thread = threading.Thread(target=self._loop)
        self._active = True
        thread.start()
        self.device_thread = thread
        self.logger.info('Started loop for device %s', self.device_name)

    def stop(self):
        """ Stops the loop thread
        """
        self.logger.info('Stopping loop for device %s', self.device_name)
        self._cleanup()
        self._active = False
        if self.device_thread != None:
            self.device_thread.join(1)
            self.device_thread = None
            self.client.disconnect()
        self.logger.info('Stopped loop for device %s', self.device_name)

    # Callbacks
    def _on_connect(self, client, userdata, flags, rc):
        self.logger.info('Connected rc: %s', rc)
        self.connected = True

    def _on_disconnect(self, client, userdata, flags, rc):
        self.logger.info('Disconnected rc: %s', rc)
        self.connected = False
        
    def _on_message(self, client, userdata, msg):
        if msg.retain == 1:
            self.logger.info('message retained')
        self.logger.info(' - '.join((msg.topic, str(msg.payload))))

    def _on_publish(self, client, userdata, mid):
        self.logger.info('Published - id:%s', mid)
    
    def _dps_registration_callback(self, error, hub):
        if error != None:
            raise Exception('DPS registration failed with error {}', error)
        else:
            if self.iot_hub_hostname == '':
                self.iot_hub_hostname = hub
        self.registration_done = True

    # Callback Handlers
    def _get_twin_callback(self, client, userdata, msg):
        """ Handler for Azure IoT Digital Twin responses
        """
        if msg.topic.find('res/20') > -1:
            if msg.topic.find('$rid=20') > -1: # get twin property response
                self.twin = msg.payload.decode('utf-8')
                self.logger.info('Twin: \n%s', self.twin)
            elif msg.topic.find('$rid=10') > -1: # reported property response
                self.logger.info('reported property accepted')
        else:
            self.logger.error('Error: %s - %s', msg.topic, msg.payload)

    def _desired_twin_callback(self, client, userdata, msg):
        """  Handler for Azure IoT Digital Twin desired properties (settings in IoT Central terminology)
        """
        desired = msg.payload.decode('utf-8')
        self.logger.info('Desired property: \n%s', desired)
        json_data = json.loads(desired)
        # must acknowledge the receipt of the desired property for IoT Central
        self._desired_ack(json_data, 200, 'completed')

    def _c2d_callback(self, client, userdata, msg):
        """ Handler for Azure IoT Hub Cloud to Device message - not available from IoT Central
        """
        self.logger.info('Cloud to Device message')

    def _direct_method_callback(self, client, userdata, msg):
        """ Handler for IoT Central Direct Method
        """
        start_idx = msg.topic.index('/POST/')+6
        method_name = msg.topic[start_idx:msg.topic.index('/', start_idx)]
        parameters = msg.payload
        self.logger.info('Direct method - method: %s, parameters: %s', method_name, parameters)

        # acknowledge receipt of the command
        request_id = msg.topic[msg.topic.index('?$rid=')+6:]
        client.publish('$iothub/methods/res/{}/?$rid={}'.format('200', request_id), '', qos=Device.qos_policy, retain=Device.retain_policy)

    def _get_twin(self):
        """ Force pull the digital twin for the device
        """
        self.client.publish('$iothub/twin/GET/?$rid={}'.format(Device.get_twin_rid), None, qos=Device.qos_policy, retain=Device.retain_policy)

    def _send_telemetry(self, device_id, payload):
        """ Send a telemetry to IoT Central
        """
        self.client.publish('devices/{}/messages/events/'.format(device_id), payload, qos=Device.qos_policy, retain=False)
        self.logger.info('device %s with id %s sent a message: %s', self.device_name, self.device_id, payload)

    def send_reported_property(self, payload):
        """ Send a reported property to IoT Central
        """
        self.client.publish('$iothub/twin/PATCH/properties/reported/?$rid={}'.format(Device.reported_rid), payload, qos=Device.qos_policy, retain=Device.retain_policy)
        self.logger.info('sent a reported property: %s', payload)

    def _gen_sas_token(self, hub_host, device_name, key, token_timeout):
        """ Generate an Azure SAS token for presenting as the password in MQTT _connect
        """
        self.token_expiry = int(time.time() + token_timeout)
        uri = '{}/devices/{}'.format(hub_host, device_name)
        string_to_sign = ('{}\n{}'.format(uri, self.token_expiry)).encode('utf-8')
        signed_hmac_sha256 = hmac.new(binascii.a2b_base64(key), string_to_sign, hashlib.sha256)
        signature = Device._urlencode(binascii.b2a_base64(signed_hmac_sha256.digest()).decode('utf-8'))
        if signature.endswith('\n'):  # somewhere along the crypto chain a newline is inserted
            signature = signature[:-1]
        return 'SharedAccessSignature sr={}&sig={}&se={}'.format(uri, signature, self.token_expiry)

    def _connect(self):
        """ Connect to the IoT Hub MQTT broker
        """
        # compute the device key
        device_key = Device._computeDrivedSymmetricKey(self.app_key, self.device_id)

        # set username and compute the password
        username = '{}/{}/api-version=2016-11-14'.format(self.iot_hub_hostname, self.device_id)
        password = self._gen_sas_token(self.iot_hub_hostname, self.device_id, device_key, config.SAS_TOKEN_TTL)
        self.client.username_pw_set(username=username, password=password)
        
        # connect to Azure IoT Hub via MQTT
        self.client.connect(self.iot_hub_hostname, port=8883)

    @staticmethod
    def _computeDrivedSymmetricKey(app_key, deviceId):
        """ Compute a device key using the application key and the device identity
        """
        app_key = base64.b64decode(app_key)
        return base64.b64encode(hmac.new(app_key, msg=deviceId.encode('utf8'), digestmod=hashlib.sha256).digest())

    @staticmethod
    def _urlencode(string):
        """ Simple URL Encoding routine
        """
        badChar = [';', '?', ':', '@', '&', '=', '+', '$',  ',']
        goodChar = ['%3B', '%3F', '3A', '%40', '%26', '%3D', '%2B', '%24', '%2C']
        strArray = list(string)
        i = 0
        for ch in strArray:
            if ch in badChar:
                strArray[i] = goodChar[badChar.index(ch)]
            i += 1
        return ''.join(strArray)

    def _cleanup(self):
        """ Cleanup on exit
        """
        pass

    @abstractmethod
    def _desired_ack(self, json_data, status_code, status_text):
        """ Perform actions and send acknowledgement on receipt of a desired property
        """
        pass

    @abstractmethod
    def _loop(self):
        """ Background loop for the device
        """
        pass