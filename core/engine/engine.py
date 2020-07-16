from modules.winApi.winApi import getWinCap, getWinHandle, getWinLoc, mouseLeftClick
from modules.config.config import default_config as config
from modules.image.image import imgCompare
from modules.creations.Character import loadCharacterHandle
import time
from modules.state.state import getState
from modules.log.log import log
from modules.filePipe.pipe import pkl_load


def getCandidates(handle):
    winCap = getWinCap(handle)
    if winCap is None:
        return None
    num = config[config["engine.default"]]["num"]
    x_align = config[config["engine.default"]]['x_align']
    y_align = config[config["engine.default"]]['y_align']
    x_max = x_align[num - 1][1]
    y_max = y_align[num - 1][1]
    if winCap.shape[0] < y_max or winCap.shape[1] < x_max:
        return None
    caps = []
    for i in range(num):
        cap = winCap[
              y_align[i][0]:y_align[i][1],
              x_align[i][0]:x_align[i][1]
              ]
        caps.append(cap)
    return caps


def getTargets():
    try:
        return pkl_load(config["engine.path_selected"])
    except:
        return []


def shot(i, handle):
    loc = getWinLoc(handle)
    if loc == None:
        return None
    x = config[config["engine.default"]]["nw_relative_center"][0][i] + loc[0]
    y = config[config["engine.default"]]["nw_relative_center"][1][i] + loc[1]
    mouseLeftClick(x, y)


from modules.image.image import PIL2cv


def doIt(handle, characterHandle):
    candidates = getCandidates(handle)
    if candidates is None:
        return None
    targets = getTargets()
    if targets is None:
        return None
    if not targets:
        log(" 文件或许正在被占用,等待... ")
        time.sleep(0.01)
        return True
    for i in range(len(candidates)):
        for target in targets:
            targetImage = characterHandle.resource[target].characterImg
            if imgCompare(targetImage, candidates[i]) == True:
                shot(i, handle)
    return True


def adjustWindow(handle):
    return None
    # TODO
    # (x1, y1, x2, y2) = getWinLoc(handle)
    # w = x2 - x1
    # h = y2 - y1
    # if w > 1600 or h > 900:
    #     return
    # setWindowPos(handle, (300, 250, w, h))


def worker():
    characterHandle = loadCharacterHandle(config["resource.path_characters"])
    handle = getWinHandle(config["engine.target_window"])
    print(666)
    while True:
        time.sleep(0.01)
        if getState() == 0:
            continue
        if not handle:
            log(" 没有检测到目标窗口 ")
            time.sleep(3)
            handle = getWinHandle(config["engine.target_window"])
        else:
            flag = doIt(handle, characterHandle)
            if not flag:
                handle = None
