import logging
from devices.slave_device import SlaveDevice
from devices.master_device import MasterDevice
from modbus import FakeModbusDeviceClient
import time

activeregisters = [ { "registerName": "temp", "address": 0, "type": "ir" }, {"registerName": "humidity", "address": 0, "type": "ir"} ]
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

master = MasterDevice("0ne0004E04A", "9Vd33uKdJLyf2IDk1AW6ckBD5alM9osQeJ8+k2F4AqmzJGITmM3pDy57sfFYuzMTlWQVefBjXiFiTwuS8D3XXA==", "50b17c39-9ac1-4139-b6e8-2f8adf94c61d", "mastertest", logger, '')

last_telemetry_sent = time.time()
while True:
    if int(time.time()) - last_telemetry_sent >= 5:
        master.report_all_slaves()
        last_telemetry_sent = time.time()
    master.client.loop()
    
