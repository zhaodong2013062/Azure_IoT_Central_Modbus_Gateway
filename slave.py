#!/usr/bin/env python

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.async import StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #

UNIT = 0x00
TEMPADDR = 0x00
HUMADDR = 0x01
THERMADDR = 0x00
INPUTREG = 4
HOLDINGREG = 3

from random import randint

def updating_writer(a):
    """ A worker process to update the registers holding the temperature and humidity readings

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    context = a[0]
    temp = context[UNIT].getValues(INPUTREG, TEMPADDR)[0] + randint(-10, 10)
    hum = context[UNIT].getValues(INPUTREG, HUMADDR)[0] + randint(-10, 10)
    log.debug("Set Temperature to: " + str(temp) + " and Humidity to " + str(hum))
    context[UNIT].setValues(INPUTREG, TEMPADDR, [temp])
    context[UNIT].setValues(INPUTREG, HUMADDR, [hum])

    therm = context[UNIT].getValues(HOLDINGREG, THERMADDR)[0]
    log.debug("Thermostat value is: " + str(therm))

def run_thermostat_server():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [50]*100),
        ir=ModbusSequentialDataBlock(0, [50]*100))
    context = ModbusServerContext(slaves=store, single=True)
    
    # ----------------------------------------------------------------------- # 
    # initialize the server information
    # ----------------------------------------------------------------------- # 
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Microsoft'
    identity.ProductCode = 'ZZH'
    identity.VendorUrl = 'http://github.com/zhaodong2013062/'
    identity.ProductName = 'thermostat server'
    identity.ModelName = 'thermostat server'
    identity.MajorMinorRevision = '1.0'
    
    # ----------------------------------------------------------------------- # 
    # run the server you want
    # ----------------------------------------------------------------------- # 
    time = 5  # 5 seconds delay
    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(time, now=False) # initially delay by time
    StartSerialServer(context, identity=identity, framer=ModbusRtuFramer, port='COM3', timeout=1, baudrate=9600)


if __name__ == "__main__":
    run_thermostat_server()