# coding:utf8
import os
from core.win.MainGui import start_main_window
from core.engine.overseer import overseer
from threading import Thread
import time
import sys
from lib import logger


def start():

    main_gui = Thread(target=start_main_window)
    main_gui.setDaemon(True)
    main_gui.start()

    count = 0
    while True:
        count = count + 1
        if count > 100:
            logger.critical("启动失败，主窗口无法启动，等待时间:{}".format(count))
            sys.exit(0)
        time.sleep(0.1)
        if main_gui.is_alive():
            break

    my_overseer = Thread(target=overseer)
    my_overseer.setDaemon(True)
    my_overseer.start()

    while True:
        time.sleep(1)
        if not main_gui.is_alive():
            sys.exit(0)
