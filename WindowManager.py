import win32gui
import win32con
import re
import win32clipboard as w
import win32api
import window
import time



class WindowManager(object):
    def getWindows(clzName='.*', title='.*'):
        wList = []
        ret = []
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), wList)
        for whand in wList:
            wind = window.Window(whand)
            if re.fullmatch(clzName, wind.clz) and re.fullmatch(title, wind.title):
                ret.append(whand)
        return ret

    def getFocus(win):
        if isinstance(win, window.Window):
            win = win.whand
        return win32gui.SetForegroundWindow(win)


    def show_window_info(whand):
        if isinstance(whand, int):
            w = window.Window(whand)

        print("handle(dec): " + str(whand))
        print("handle(hex): " + str(hex(whand)))
        print("title: " + w.title)
        print("class: " + w.clz)
        print("start: " + str(w.startPoint))
        print("width: " + str(w.width))
        print("height: " + str(w.height))


    def getClipboardText(args = None):
        w.OpenClipboard()
        text = w.GetClipboardData(win32con.CF_UNICODETEXT)
        w.CloseClipboard()
        return text


    def setClipboardText(aString):
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(win32con.CF_UNICODETEXT, aString)
        w.CloseClipboard()


    def setCursorPos(pos):
        win32api.SetCursorPos((pos[0], pos[1]))


    def mouselClick(args=None, sleep=0.0):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(sleep)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def mouselClickPos(pos, times=1, sleep=0):
        WindowManager.setCursorPos(pos)
        time.sleep(sleep)
        for x in range(times):
            WindowManager.mouselClick()
            time.sleep(sleep)

    def mouserClickPos(pos, times=1, sleep=0):
        WindowManager.setCursorPos(pos)
        time.sleep(sleep)
        for x in range(times):
            WindowManager.mouserClick()
            time.sleep(sleep)


    def nextPage(whand):
        win32gui.SendMessage(whand, win32con.WM_KEYDOWN, win32con.SB_PAGEDOWN, 0)
        win32gui.SendMessage(whand, win32con.WM_KEYUP, win32con.SB_PAGEDOWN, 0)

    def mouserClick(args=None):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    def mouseMove(method):
        win32api.mouse_event(win32con.MOUSE_MOVED, method[0], method[1])

    def scrollToTop(args=None):
        win32api.keybd_event(17, 0, 0, 0)
        win32api.keybd_event(36, 0, 0, 0)
        win32api.keybd_event(36, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)


# wList = WindowManager.getWindows('.*GuiFoundation', "")
#
# count = 1
# while count < 1000:
#     for whand in wList:
#         WindowManager.show_window_info(whand)
#         WindowManager.getFocus(whand)
#
#         WindowManager.setClipboardText(str())
#         count += 1
#
#
#
#
#
#
#
#     # time.sleep(0.001)

# print(WindowManager.getWindows('WeChatMainWndForPC', '微信'))
# [591182, 852118]



