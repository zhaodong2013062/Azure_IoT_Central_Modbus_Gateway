# These are the values to configure the behavior of the modbus gateway

"""
Modbus parameters
"""
# Modbus baud rate
BAUD_RATE = 9600
# Modbus timeout in ms
MODBUS_CLIENT_TIMEOUT = 1
# Modbus serial port for Master
SERIAL_PORT = '/dev/ttyAP1'
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