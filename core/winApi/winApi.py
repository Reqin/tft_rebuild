import win32api
import win32con
import win32gui
import time
from PIL.ImageGrab import grab

_POS = (0, 0, 0, 0)


def get_win_handle(target):
    # 获取窗口句柄
    return win32gui.FindWindow(0, target)


# def set_win_pos(handle, pos: _POS):
#     win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, *pos, win32con.SWP_SHOWWINDOW)


def get_win_pos(handle):
    try:
        return win32gui.GetWindowRect(handle)
    except:
        return None


def get_win_cap(handle):
    loc = get_win_pos(handle)
    if loc is None:
        return None
    return grab(loc)


def get_cursor_pos():
    return win32api.GetCursorPos()


def mouse_left_click(x, y):
    win32api.SetCursorPos([x, y])
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)
