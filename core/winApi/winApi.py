import win32api
import win32con
import win32gui
from modules.image.image import cutWin
import time


def getWinHandle(target):
    # # 获取窗口句柄
    return win32gui.FindWindow(0, target)

def setWindowPos(handle, pos):
    win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, pos[0],pos[1],pos[2],pos[3], win32con.SWP_SHOWWINDOW)

def getWinLoc(handle):
    try:
        return win32gui.GetWindowRect(handle)
    except:
        return None


def mouseLeftClick(x, y):
    print("geted")
    win32api.SetCursorPos([x, y])
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)
    # nasty PyMouse
    # m = PyMouse()
    # m.click(x, y, 1)


def getWinCap(handle):
    loc = getWinLoc(handle)
    if loc == None:
        return None
    return cutWin(loc)
