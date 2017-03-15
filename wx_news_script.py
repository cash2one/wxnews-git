import config, tools
import json
import re
import datetime
import pymysql
# import urllib
from urllib import parse
import requests

key = config.redis_wx_news_queue_key
api = config.add_url2mcq_api
log_key = "json-wechat-android"
biz_regex = "__biz=(.*?)&"
d = {}
"""
从redis中读取微信url存储到mcq中
"""


conn = pymysql.connect(**config.mysql_126_config)
cursor = conn.cursor()
sql = "SELECT wx_biz, wx_nick, wx_id FROM wx_pbs"
cursor.execute(sql)
rt = cursor.fetchall()
conn.close()
for record in rt:
    d[record[0]] = {
        "wx_id": record[2],
        "wx_nick": record[1]
    }


while 1:
    record = config.redis_wx.blpop(key)
    if record:
        record = record[1].decode('utf-8')
        record = json.loads(record)
    else:
        print("Invaild record:", record)
        continue
    url = record['url']
    url = str(url).replace("&amp;", "&")

    print(datetime.datetime.now(), url)
    wx_biz = re.findall(biz_regex, url)
    if wx_biz:
        wx_biz = wx_biz[0]
    else:
        continue

    if re.fullmatch(config.weixin_news_pattern, url):
        ru = api + "?url=" + parse.quote_plus(url)
        rp = tools.make_request(ru)
        rp.encoding = "utf-8"
        if rp:
            if rp.text.find("入转码队列成功") != -1:
                log_dict = {}
                log_dict['biz'] = wx_biz
                log_dict['nick'] = d[wx_biz]['wx_nick'] if wx_biz in d else "unknow"
                log_dict['id'] = d[wx_biz]['wx_id'] if wx_biz in d else "unknow"
                log_dict['url'] = url
                log_dict['log_time'] = str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')) + '.000Z'
                config.redis_elk.rpush(log_key, json.dumps(log_dict))
                print("add to mcq success:", rp.text)
            else:
                print("add to mcq error: ", rp.text)
        else:
            print("add to mcq error: ", "request to %s error" % ru)
    else:
        print("url not match pattern", config.weixin_news_pattern)