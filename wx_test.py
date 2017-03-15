#! /usr/bin/env python3
# _*_ coding: UTF-8 _*_
import config, time
import pymysql
from PIL import Image
import json
import datetime
from PIL import ImageGrab
import win32gui, win32con, win32api
from WindowManager import WindowManager as wm


def get_task(count = -1):
    while 1:
        try:
            conn = pymysql.connect(**config.mysql_126_config)
            cursor = conn.cursor()
            sql = "SELECT wx_biz FROM wx_pbs"
            if count > 0:
                sql += ' LIMIT %s' % count
            cursor.execute(sql)
            ret = cursor.fetchall()
            if ret:
                return ret
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    # task_key = 'WX:PBS_MAP'
    # r = config.redis_liu
    # task = []
    # for x in r.hkeys(task_key):
    #     d = dict(json.loads(r.hget(task_key, x).decode('utf-8')))
    #     if 'key-type' in d.keys() and d['key-type'] == 'wx_biz':
    #         task.append(d[d['key-type']])
    #         if count == len(task):
    #             break


def news():
    p = config.wx_pix_pos
    ret = (p[0], 0, p[0] + 1, win32api.GetSystemMetrics(win32con.SM_CYSCREEN))
    img = ImageGrab.grab(ret)
    news_map = []
    count = 0
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pix = img.getpixel((x, y))
            # print(x, y, pix)
            if pix[0] == 255 and pix[1] < 100 and pix[2] < 100:
                count += 1
            else:
                count = 0
            if count >= 14:
                news_map.append((x, y))
                count = 0
    # img.show()
    return news_map


def make_regular_image(img, size = (256, 256)):
    return img.resize(size).convert('RGB')

def hist_similar(m1, m2):
    assert len(m1) == len(m2)
    return sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(m1, m2)) / len(m1)

def is_similar(m1, m2):
    return hist_similar(m1.histogram(), m2.histogram())

def clean_message():
    while True:
        wm.setClipboardText("111")
        time.sleep(0.1)
        wm.mouserClick()
        time.sleep(0.1)
        wm.mouseMove((20, 48))
        time.sleep(0.1)
        wm.mouselClick()
        time.sleep(0.1)
        url = wm.getClipboardText()
        wm.mouseMove((-20, -48))
        time.sleep(1)
        if url.find('http') != -1:
            wm.mouserClick()
            time.sleep(0.1)
            wm.mouseMove((20, 34))
            time.sleep(0.1)
            wm.mouselClick()
            wm.mouseMove((-20, -34))
        else:
            time.sleep(0.5)
            wm.mouselClickPos(config.wx_return_pos)
            return



def collect_message():
    pre = ''
    preurl = ''
    wm.setClipboardText('')
    p = [config.wx_click_pos[0], config.wx_click_pos[1]]
    wm.setCursorPos(p)
    time.sleep(0.1)
    clean = False
    count = 0
    while True:
        if p[1] < 200:
            clean_message()
            return
        wm.mouserClickPos(p)
        time.sleep(0.1)
        wm.mouseMove((20, 48))
        wm.mouselClick(sleep=0.2)
        time.sleep(0.2)
        url = wm.getClipboardText()
        if url == '':
            p[1] -= 70
            continue
        if preurl != url:
            preurl = url
            print("redis set add : " + url)
            info = {
                'submit_time': str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                'source': 'pc',
                'url': url
            }
            config.redis_wx.rpush(config.redis_weixin_news_queue_key, str(info))
        wm.mouseMove((-20, -48))
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)
        if not clean:
            if url == pre:
                count += 1
            else:
                count = 0
                pre = url
        else:
            p[1] -= 70
        if count > 20:
            clean = True


def init(mode='devx'):
    # 屏幕尺寸
    width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    whands = wm.getWindows("WeChatMainWndForPC", "微信")
    if not len(whands) >= 1:
        raise EnvironmentError()

    # 铺设窗口的起点
    p0 = [0, 0]
    starts = []

    # 等距离的铺设微信窗口
    for whand in whands:
        win32gui.ShowWindow(whand, win32con.SW_SHOW)
        starts.append((p0[0], p0[1]))
        win32gui.SetWindowPos(whand, win32con.HWND_TOP, p0[0], p0[1], config.wx_window_width, config.wx_window_height, win32con.SWP_SHOWWINDOW)
        if len(whands) > 1:
            p0[1] += int((height - config.wx_window_height) / (len(whands) - 1))

    for whand in whands:
        # 获得矩形窗口， 将指针放置到微信图标上
        pos = win32gui.GetWindowPlacement(whand)[4]
        win32gui.SetWindowPos(whand, win32con.HWND_TOPMOST, pos[0], pos[1], config.wx_window_width, config.wx_window_height, win32con.SWP_SHOWWINDOW)
        win32api.SetCursorPos((pos[0] + config.wx_chat_w, pos[1] + config.wx_chat_h))

        s = 0
        # 与标准订阅号的图片进行对比，清理在订阅号上的图标
        while s < 0.9:
            img = ImageGrab.grab((pos[0] + config.wx_icon_pos_x, pos[1] + config.wx_icon_pos_y,
                                  pos[0] + config.wx_icon_pos_x + config.wx_icon_width,
                                  pos[1] + config.wx_icon_pos_y + config.wx_icon_height))
            # 计算图片相似度
            img = make_regular_image(img)
            m1 = make_regular_image(Image.open('wxicon.bmp'))
            s = is_similar(m1, img)
            win32api.SetCursorPos((pos[0] + config.wx_icon_pos_x, pos[1] + config.wx_icon_pos_y))
            wm.mouserClick()
            win32api.mouse_event(win32con.MOUSE_MOVED, 10, 10)
            wm.mouselClick()
        # 移动指针到公众号列表的第一个
        win32api.mouse_event(win32con.MOUSE_MOVED, 100, 0)

    #
    for whand in whands:
        pos = win32gui.GetWindowPlacement(whand)[4]
        p = config.wx_pix_pos
        # 空消息/空订阅号列表的图像
        img = Image.open('wxmessage.bmp')
        while True:
            wm.mouselClickPos(config.wx_mes_icon_pos, times=2, sleep=0.05)
            news_map = news()
            print("news map: " + str(news_map))

            if len(news_map) == 0:
                break
            point = (411, news_map[0][1])
            print(point)
            time.sleep(0.1)
            wm.mouselClickPos(point, sleep=0.2)
            wm.mouselClickPos(config.wx_show_msg_pos, sleep=1)
            wm.setCursorPos(config.wx_click_pos)
            time.sleep(0.1)
            wm.mouseMove((75, 0))
            wm.mouselClick()
            win32api.keybd_event(win32con.VK_NEXT, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_NEXT, 0, win32con.WM_KEYDOWN, 0)
            wm.mouseMove((75, 0))
            collect_message()

            continue

        exit(0)
        while True:
            wm.mouselClickPos(config.wx_mes_icon_pos, times=2)
            time.sleep(3)
            wm.setCursorPos(config.wx_pub_rec_pos)
            img = ImageGrab.grab((p[0] + pos[0], p[1] + pos[1], p[0] + pos[0] + 1, p[1] + pos[1] + 1))
            print(img.getpixel((0, 0)))
            # new message
            if img.getpixel((0, 0))[0] >= 200:
                wm.mouselClick()
                time.sleep(0.5)
                wm.mouselClickPos(config.wx_show_msg_pos)
                time.sleep(0.5)
                wm.setCursorPos(config.wx_click_pos)
                time.sleep(3)
                wm.mouseMove((75, 0))
                wm.mouselClick()
                win32api.keybd_event(win32con.VK_NEXT, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_NEXT, 0, win32con.WM_KEYDOWN, 0)
                wm.mouseMove((-75, 0))
                # wm.mouselClickPos(config.wx_top_pos, times=2, sleep=1)
                m2 = ImageGrab.grab(config.wx_article_ret)
                s = is_similar(m2, img)
                p0 = config.wx_click_pos
                pre = ''
                count = 0
                clean = False
                while s < 0.9:
                    wm.setCursorPos(p0)
                    if p0[1] < (pos[1] + 200):
                        while True:
                            wm.setClipboardText('')
                            wm.mouserClick()
                            time.sleep(0.1)
                            wm.mouseMove((20, 34))
                            wm.mouselClick()
                            time.sleep(0.1)
                            url = str(wm.getClipboardText())
                            if url.find('http') != -1:
                                time.sleep(0.5)
                                wm.mouserClickPos(config.wx_del_msg_pos)
                                time.sleep(0.1)
                                wm.mouseMove((20, 27))
                                wm.mouselClick()
                            else:
                                wm.mouselClickPos(config.wx_return_pos)
                                break
                        # wm.mouserClickPos(config.wx_pub_rec_pos)
                        # time.sleep(3)
                        # wm.mouseMove((10, 5))
                        # wm.mouselClick()
                        break
                    wm.mouserClick()
                    time.sleep(0.1)
                    wm.mouseMove((20, 34))
                    wm.mouselClick()
                    time.sleep(0.1)
                    url = wm.getClipboardText()
                    print(url)
                    # p0[1] += config.wx_pub_msg_box_height
                    print(p0)
                    wm.setCursorPos(config.wx_click_pos)
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)
                    if not clean:
                        if url == pre:
                            count += 1
                        else:
                            count = 0
                            pre = url
                    if count > 20:
                        p0[1] -= int(config.wx_pub_msg_box_height * 7 / 8)
                        clean = True
                    # exit(0)
                    m2 = ImageGrab.grab(config.wx_article_ret)
                    s = is_similar(m2, img)
            else:
                break
            time.sleep(3)
    return

width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

def layout(whand, with_start = True):
    ret = (0, 0, 850, 590)
    h = height
    # if not with_start:
    #     h -= 40
    win32gui.SetWindowPos(whand, win32con.HWND_TOP, ret[0], ret[1], ret[2], ret[3],win32con.SWP_SHOWWINDOW)
    wm.mouselClickPos(config.wx_mes_icon_pos, times=2, sleep=0.05)


def clean_left(whand):
    std = Image.open('wxicon.bmp')
    r = (config.wx_icon_pos_x, config.wx_icon_pos_y, config.wx_icon_width + config.wx_icon_pos_x, config.wx_icon_pos_y + config.wx_icon_height)
    pos = win32gui.GetWindowPlacement(whand)[4]
    t = (r[0] + pos[0], r[1] + pos[1], r[2] + pos[0], r[3] + pos[1])
    img = ImageGrab.grab(t)
    # img.show()
    while is_similar(std, ImageGrab.grab(t)) < 0.9:
        wm.mouserClickPos((t[0], t[1]))
        wm.mouseMove((10, 5))
        time.sleep(0.5)
        wm.mouselClick()
    wm.mouselClickPos((t[0], t[1]))

def collect_msg(whand):
    while True:
        wm.mouselClickPos(config.wx_mes_icon_pos, times=2, sleep=0.05)
        news_map = news()
        if len(news_map) == 0:
            print("No new message in this window0.0")
            break
        point = (411, news_map[0][1])
        print(point)
        time.sleep(0.1)
        wm.mouselClickPos(point, sleep=0.2)
        wm.mouselClickPos(config.wx_show_msg_pos, sleep=1)
        wm.mouselClickPos((820, 1000), sleep=1)
        time.sleep(0.2)
        win32api.keybd_event(win32con.VK_NEXT, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_NEXT, 0, win32con.WM_KEYDOWN, 0)
        time.sleep(0.5)
        wm.setCursorPos(config.wx_click_pos)
        time.sleep(0.5)
        collect_message()

def send_text(text):
    # 单击以置输入窗于最前端
    wm.mouselClickPos((500, 500))
    wm.setClipboardText(text)
    time.sleep(0.5)
    wm.mouserClick()
    time.sleep(0.5)
    wm.mouseMove((20, 10))
    time.sleep(1)
    wm.mouselClick()
    time.sleep(1)
    # 发送消息按钮位置
    wm.setCursorPos((820, 570))
    wm.mouselClick()


def get_url():
    # 确认弹出窗口
    while True:
        wm.setCursorPos((600, 130))
        time.sleep(0.5)
        wm.mouselClick()
        time.sleep(0.5)
        ws = wm.getWindows('CefWebViewWnd', '微信')
        if len(ws) == 1:
            w = ws[0]
            win32gui.SetWindowPos(w, win32con.HWND_TOP, 310, 200, 540, 390, win32con.SWP_SHOWWINDOW)
            time.sleep(0.5)
            break
        else:
            time.sleep(1)
            print("no window")

    # 确认分享窗口
    while True:
        wm.mouselClickPos((390, 250))
        time.sleep(0.5)
        ws = wm.getWindows('SelectContactWnd', '微信')
        if len(ws) == 1:
            w = ws[0]
            win32gui.SetWindowPos(ws[0], win32con.HWND_TOP, 250, 95, 600, 495, win32con.SWP_SHOWWINDOW)
            time.sleep(0.5)
            break

    wm.setCursorPos((270, 160))
    time.sleep(0.5)
    wm.mouselClick()
    time.sleep(0.5)

    # 分享链接的确定按钮
    wm.setCursorPos((700, 560))
    time.sleep(0.5)
    wm.mouselClick()
    time.sleep(0.5)

    # 复制链接
    wm.setCursorPos((700, 195))
    time.sleep(0.5)
    wm.mouserClick()
    time.sleep(0.5)
    wm.setCursorPos((720, 300))
    time.sleep(0.5)
    wm.mouselClick()
    time.sleep(0.5)

    request_url = wm.getClipboardText()
    print("request url:\n", request_url)

    ret = {}
    ret['url'] = request_url
    ret['time'] = time.time()
    config.redis_wx.rpush(config.redis_wx_newslist_queue_key, json.dumps(ret))
    print("add to redis " + config.redis_wx_newslist_queue_key + ": " + json.dumps(ret))
    time.sleep(1)


def clean_msg():
    ps = [(610, 280), (610, 190)]
    ms = [180]
    for p in ps:
        wm.setCursorPos((600, 100))
        time.sleep(0.5)
        wm.mouserClick()
        time.sleep(0.5)
        wm.setCursorPos(p)
        time.sleep(0.3)
        wm.mouselClick()
        time.sleep(1)


whands = wm.getWindows("WeChatMainWndForPC", "微信")
while True:
    task = get_task()
    print("task size: %d" % len(task))
    for whand in whands:
        layout(whand, True)
        for wx_biz in task:
            url = config.MSG_LIST_TEMPLATE % wx_biz
            print(url)
            send_text(url)
            get_url()
            clean_msg()
            time.sleep(2)
        # clean_left(whand)
        print("sleep: ", 10)
        time.sleep(10)
    print("sleep: ", 10)
    time.sleep(10)
