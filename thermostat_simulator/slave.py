#!/usr/bin/env python

from random import randint

from thermostat_gui import ThermostatGui, ThermostatGuiMessage

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

# initial_message = ThermostatGuiMessage(0, 50, 0)
# thermostat_gui = ThermostatGui(initial_message)
# thermostat_gui.start()

def updating_writer(a):
    """ A worker process to update the registers holding the temperature and humidity readings

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    context = a[0]
    therm = context[UNIT].getValues(HOLDINGREG, THERMADDR)[0]
    # temp = context[UNIT].getValues(INPUTREG, TEMPADDR)[0]
    temp = therm + randint(-5, 5)
    # hum = 50 + randint(-6, 6)
    # log.debug("Set Temperature to: " + str(temp) + " and Humidity to " + str(hum))
    hum = randint(0, 100)
    context[UNIT].setValues(INPUTREG, TEMPADDR, [temp])
    context[UNIT].setValues(INPUTREG, HUMADDR, [hum])
    
    #thermostat_gui.update(ThermostatGuiMessage(temp, hum, therm))

def run_thermostat_server():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100))
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