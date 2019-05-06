import logging
import time

import config
from devices.master_device import MasterDevice

logger = logging.getLogger()
logging.basicConfig(format=config.LOGGING_FORMAT)
logger.setLevel(config.GLOBAL_LOG_LEVEL)

master = MasterDevice(
        config.CENTRAL_SCOPE_ID, 
        config.CENTRAL_APP_KEY, 
        config.MASTER_MODEL_ID,
        config.MASTER_DEVICE_ID,
        logger)

try:
    master.start()  
    while True:
        pass
except (Exception, KeyboardInterrupt) as e:
    logger.error('Error in IoT Edge runtime, exiting: %s', e)
    master.stop()
    raise e