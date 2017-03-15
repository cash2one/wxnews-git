import win32gui, win32con


class Rect(object):
    def __init__(self, p0, p1):
        self.start = p0
        self.end = p1
        self.w = p1.x - p0.x
        self.h = p1.y - p0.y

    def __str__(self):
        desc = {}
        for k, v in self.__dict__.items():
            if isinstance(v, object):
                v = str(v)
            desc[k] = v
        return str(desc)


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.__dict__)

class Window(object):
    def __init__(self, whand):
        self.whand = whand
        self.title = win32gui.GetWindowText(whand)
        self.clz = win32gui.GetClassName(whand)
        self.rect = win32gui.GetWindowRect(whand)
        self.startPoint = Point(self.rect[0], self.rect[1])
        self.endPoint = Point(self.rect[2], self.rect[3])
        self.width = self.endPoint.x - self.startPoint.x
        self.height = self.endPoint.y - self.startPoint.y


    def toTop(self):
        win32gui.BringWindowToTop(self.whand)


    def toMaximize(self):
        win32gui.ShowWindow(self.whand, win32con.SW_MAXIMIZE)


    def toMinimize(self):
        win32gui.ShowWindow(self.whand, win32con.SW_MINIMIZE)

    def toForegroundWindow(self):
        # make sure all other alwayes-on-top windows are hidden
        self.hideAlwaysOnTopWindows()
        win32gui.SetForegroundWindow(self.whand)


    def hideAlwaysOnTopWindows(self):
        pass

    def __str__(self):
        desc = {}
        for k, v in self.__dict__.items():
            if isinstance(v, object):
                v = str(v)
            desc[k] = v
        return str(desc)
