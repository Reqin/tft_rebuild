# coding:utf8
import os
from core.win.MainGui import start_main_window
from core.engine.overseer import overseer
from threading import Thread
from core.win.Auth import start_auth
import time
import sys
from lib import logger


def start():
    # auth = start_auth()
    # if not auth:
    #     logger.info("未完成认证，正在退出程序...")
    #     exit()
    # logger.info("认证成功，进入主程序!")

    mainGui = Thread(target=start_main_window)
    mainGui.setDaemon(True)
    mainGui.start()

    count = 0
    while True:
        count = count + 1
        if count > 100:
            sys.exit(0)
        time.sleep(0.1)
        if mainGui.is_alive():
            break

    my_overseer = Thread(target=overseer)
    my_overseer.setDaemon(True)
    my_overseer.start()

    while True:
        time.sleep(0.5)
        if not mainGui.is_alive():
            sys.exit(0)
