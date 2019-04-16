import logging
import time

import config
from devices.master_device import MasterDevice
from devices.slave_device import SlaveDevice
from modbus import FakeModbusDeviceClient

activeregisters = [ { "registerName": "temp", "address": 0, "type": "ir" }, {"registerName": "humidity", "address": 0, "type": "ir"} ]

FORMAT = '%(asctime)s:[%(module)s.%(funcName)s()]: %(message)s'
logger = logging.getLogger()
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)

master = MasterDevice("0ne0004E04A", "9Vd33uKdJLyf2IDk1AW6ckBD5alM9osQeJ8+k2F4AqmzJGITmM3pDy57sfFYuzMTlWQVefBjXiFiTwuS8D3XXA==", 'd3grte/1.1.0', 'f0323747-8e27-46d4-bb7a-c92d059c480b', logger)

last_telemetry_sent = time.time()

master.start()

try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    master.stop()
    raise
