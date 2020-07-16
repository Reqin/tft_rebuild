from modules.engine.engine import worker
from threading import Thread
import time
from modules.log.log import log


def overseer():
    task = Thread(target=worker,)
    task.setDaemon(True)
    task.start()
    while True:
        time.sleep(1)
        if not task.is_alive():
            log(" worker sleeping ,wake it up")
            task = Thread(target=worker,)
            task.setDaemon(True)
            task.start()
