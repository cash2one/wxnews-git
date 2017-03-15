#! /usr/bin/env python3
# _*_ coding: UTF-8 _*_

import win32gui
import win32api
import config
from WindowManager import WindowManager as wm
import re
import urllib
import datetime
import requests
import time
from PIL import ImageGrab
# url = 'http://mp.weixin.qq.com/s?__biz=MzA3MTgwOTEwMw==&mid=2652166370&idx=5&sn=3d638ad41386491ed729caeb26a7af20&chksm=84c799c2b3b010d4720cac7d7d24c390140590fbcfbd698efbd41131703ea241ec83d4612bd2&scene=0#rd'
# print(config.add_url2mcq_api + urllib.parse.quote(url))
# print(re.match(config.weixin_news_pattern, url))
r = requests.get('https://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzI3MzA5MzgzNw==&uin=MTY2NzczMjIwMA%3D%3D&key=9ed31d4918c154c8e60c55b331de4f8c40617c127f4bd6ae8b971da71b05f60dca3eec87b3458af4c9d6b73efd74d9f37e84f43dec27fced6d7b96df1c239df454e31fbb64edbfb7c08f9dd27783b693&devicetype=Windows+10&version=6203005d&lang=zh_CN&ascene=1&pass_ticket=Zd99JYKG2yBbkRYVrw92UrlposFeqxD9hW2s2qAxgnwLR5A6zFnAFPeXiVr7sV%2Fm#wechat_webview_type=1&winzoom=1')
print(r.text)
# wm.setCursorPos((700, 200))
