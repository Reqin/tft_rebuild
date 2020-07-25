import logging
import json
import logging.config

with open("conf/log.json", "r") as f:
    conf = json.load(f)
logging.config.dictConfig(conf)
logger = logging.getLogger("my_logger")
logging.disable(logging.DEBUG)
logging.disable(logging.INFO)