# These are the values that need to be configured specifically for your IoT Central application
# The values can be found in Administration -> Device Connection page

# Note:  The APP_KEY allows the device key to be computed in the code.  In a gateway scenario this allows 
# leaf devices to be added to IoT Central without having to first add them to the IoT Central application.
# the code will register the device automatically and it will be placed in the unassociated devices within the 
# Device Explorer page.

# It is also possible to use a model identifier to associate a device with a temmplate within IoT Central.  This allows 
# a device to be auto associated and auto assigned to a template if turned on within the application.  This feature requires
# a manual config change on the application to enable it, please contact IoT Central team if you wish to use this feature 

# Scope identifier for the application - found in IoT Central in the Administration -> Device Connection page
SCOPE_ID = '0ne0004E04A'

# Application key - found in IoT Central in the Administration -> Device Connection page
APP_KEY = '9Vd33uKdJLyf2IDk1AW6ckBD5alM9osQeJ8+k2F4AqmzJGITmM3pDy57sfFYuzMTlWQVefBjXiFiTwuS8D3XXA=='

# template model identifier - found in IoT Central in the Device Explorer at the top of the page
MODEL_ID = '130772c7-97dd-4a76-bbdb-9209888293f6'

# device identity, this can be pre registered in the IoT Central application or will be registered via DPS and 
# placed in the Unassociated Devices page waiting to be associated with a template
DEVICE_NAME = '04121b4d-7bcc-4c35-8596-23151ee91d97'

# how long should the SAS Token be valid for in seconds, code should be added to renew the token before expiration
SAS_TOKEN_TTL = 3600 # one hour

# path to the root cert for Azure services
PATH_TO_ROOT_CERT = 'baltimore.cer'

# validate the cert returned from Azure service
VALIDATE_CERT =  True

# Modbus baud rate
BAUD_RATE = 9600

# Modbus serial port for Master
SERIAL_PORT = 'COM4'

# Slave config file name
CONFIG_KEY = 'slavesconfig'

# Slave config keys
CONFIG_KEY_SLAVES = "slaves"
CONFIG_KEY_SCOPE_ID = 'scopeId'
CONFIG_KEY_APP_KEY = 'appKey'
CONFIG_KEY_DEVICE_ID = 'deviceId'
CONFIG_KEY_DEVICE_NAME = 'deviceName'
CONFIG_KEY_MODEL_ID = 'modelId'
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

"""
Config file structure:
{
    config:
    {
        value:
        [
            {
                deviceName: slave1,
                deviceId: ???????,
                appKey: ???????,
                scopeId: ??????,
                modelId: ?????,
                slaveId: 0x00,
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
                ]
            },
            {
                deviceName: slave2,
                deviceId: ????????,
                appKey: ???????,
                scopeId: ??????,
                modelId: ?????,
                slaveId: 0x01,
                activeRegisters:
                [
                    {
                        registerName: LED,
                        address: 0x00,
                        type: co
                    }
                ]
            },
        ]
    }
}
"""