# coding:utf8
from modules.config.config import defaultConfig
from modules.win.MainGui import MainGui
from modules.engine.overseer import overseer
from threading import Thread
from modules.win.LoginGui import login
import time
import sys
import queue


def main():

    loginState = queue.Queue(maxsize=1)
    accessState = queue.Queue(maxsize=1)
    taskLogin = Thread(target=login,args=(loginState,accessState))
    taskLogin.setDaemon(True)
    taskLogin.start()
    while True:
        time.sleep(0.1)
        # 
        if not taskLogin.is_alive():
            sys.exit(0)
        if loginState.empty():
            continue
        # 收到loginTask的答复
        state = loginState.get()
        if state is True:
            accessState.put(True)
            loginState.get()
            break
        else:
            sys.exit(0)

    mainGui = Thread(target=MainGui)
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

