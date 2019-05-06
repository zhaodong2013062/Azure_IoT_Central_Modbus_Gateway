import logging

# These are the values to configure the behavior of the modbus gateway

# Logging format
LOGGING_FORMAT = '%(asctime)s:[%(module)s.%(funcName)s()]: %(message)s'
# Logging Level 
GLOBAL_LOG_LEVEL = logging.INFO

"""
IoT Central parameters
"""
# IoT Central App Scope ID
CENTRAL_SCOPE_ID = '0ne0004E04A'
# IoT Central App Key
CENTRAL_APP_KEY = '9Vd33uKdJLyf2IDk1AW6ckBD5alM9osQeJ8+k2F4AqmzJGITmM3pDy57sfFYuzMTlWQVefBjXiFiTwuS8D3XXA=='
# Master Device ModelId
MASTER_MODEL_ID = 'd3grte/1.1.0'
# Master DeviceId
MASTER_DEVICE_ID = 'modbusmastertests'

"""
Modbus parameters
"""
# Modbus mode: 
#   0: Simulated
#   1: Serial
#   2: TCP/IP
MODBUS_MODE = 0
# Modbus baud rate
BAUD_RATE = 4800
# Modbus timeout in ms
MODBUS_CLIENT_TIMEOUT = 1
# Modbus serial port for Master
#SERIAL_PORT = '/dev/ttyAP1'
SERIAL_PORT = 'COM5'
# ms to wait on modbus retries
MODBUS_RETRY_WAIT = 20
# Max number of retry attempts
MODBUS_RETRY_ATTEMPTS = 3

"""
JSON Keys
"""
# Model Data keys
KEY_MODEL_ID = 'iotcModelId'
KEY_GATEWAY = 'iotcGateway'
KEY_GATEWAY_ID = 'iotcGatewayId'
KEY_IS_GATEWAY = 'iotcIsGateway'

# Payload key s
KEY_VERSION = '$version'
KEY_VERSION = 'value'
KEY_CONFIG = 'slavesconfig'

# Slave config keys
CONFIG_KEY_SLAVES = "slaves"
CONFIG_KEY_SCOPE_ID = 'scopeId'
CONFIG_KEY_APP_KEY = 'appKey'
CONFIG_KEY_DEVICE_ID = 'deviceId'
CONFIG_KEY_MODEL_ID = 'modelId'
CONFIG_KEY_UPDATE_INTERVAL = 'updateInterval'
CONFIG_KEY_SLAVE_ID = 'slaveId'
CONFIG_KEY_ACTIVE_REGISTERS = 'activeRegisters'

# Active Registers
ACTIVE_REGISTERS_KEY_REGISTER_NAME = 'registerName'
ACTIVE_REGISTERS_KEY_ADDRESS = 'address'
ACTIVE_REGISTERS_KEY_TYPE = 'type'
ACTIVE_REGISTERS_TYPE_COIL = 'co'
ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT = 'di'
ACTIVE_REGISTERS_TYPE_INPUT_REGISTER = 'ir'
ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER = 'hr'
ACTIVE_REGISTERS_BIT_TYPES = [ACTIVE_REGISTERS_TYPE_COIL, ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT]
ACTIVE_REGISTERS_REGISTER_TYPES = [ACTIVE_REGISTERS_TYPE_INPUT_REGISTER, ACTIVE_REGISTERS_TYPE_HOLDING_REGISTER]
ACTIVE_REGISTERS_READONLY_TYPES = [ACTIVE_REGISTERS_TYPE_DISCRETE_INPUT, ACTIVE_REGISTERS_TYPE_INPUT_REGISTER]

"""
Config json structure:
{
    config:
    {
        value:
        {
            modelId: ?????, 
            updateInterval: 1,
            activeRegisters:
            [
                    {
                        registerName: tempSensor,
                        address: 0x00,
                        type: ir
                    },
                    {
                        registerName: humiditySensor,
                        address: 0x01,
                        type: ir
                    },
                    {
                        registerName: thermostat,
                        address: 0x00
                        type: hr
                    }
            ],
            slaves: 
            [
                {
                    deviceName: slave1,
                    deviceId: ??????,
                    slaveId
                },
                {
                    deviceName: slave2,
                    deviceId: ??????,
                    slaveId
                }
            ]
        }
    }
}
"""