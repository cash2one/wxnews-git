import config
import json
import requests
import re
import tools
import time
import datetime
import pymysql

key = config.redis_wx_newslist_queue_key
regex = "msgList = (.*?);\s"
biz_regex = "__biz=(.*?)&"
conn = pymysql.connect(**config.mysql_126_config)
cursor = conn.cursor()

"""
在{r}中，以{key}命名的值是一个阻塞队列，其中存储的是可以在浏览器中访问的某个具体biz对应的近期历史文章

存储方式为rpush,所以读取时以blpop
"""


def make_request(url, times = 3):
    while times > 0:
        try:
            rq = requests.get(url)
            if rq.status_code < 300:
                return rq
        except Exception as e:
            print(e)
            times -= 1


c = 1
while 1:
    try:
        ret = config.redis_wx.blpop(key)
        ret = json.loads(ret[1].decode('utf-8'))
        url = ret['url']
        timestamp = ret['time']

        wx_biz = re.findall(biz_regex, url)
        if wx_biz:
            wx_biz = wx_biz[0]
        else:
            print("no biz: " + url)
            continue
        rq = make_request(url)
        if not rq:
            continue
        index = rq.text.find("请在微信客户端打开链接")
        if index > 0:
            print("expire url: " + url)
            continue
        else:
            print(datetime.datetime.now(), url)
            # massages
            ms = re.findall(regex, rq.text)
            if ms:
                ms = ms[0]
                ms = json.loads(ms)['list']

                # 取最后一次消息的时间戳
                sql = "SELECT lastnews FROM wx_pbs WHERE wx_biz = %s" % tools.quote_words(wx_biz)
                cursor.execute(sql)
                ts = cursor.fetchone()
                if ts:
                    ts = (lambda x: x[0] if x[0] else 0)(ts)
                    max_time = ts
                    if len(ms) > 0:
                        for m in ms:
                            if not 'comm_msg_info' in dict(m).keys():
                                continue
                            comm_msg_info = m['comm_msg_info']
                            # 消息列表是以时间戳从大到小排列的，所以当发现其不大于mysql中的时间时，可以认为结束了
                            if ts < comm_msg_info['datetime'] and "app_msg_ext_info" in dict(m).keys():
                                print(json.dumps(m))
                                max_time = (lambda x: comm_msg_info['datetime'] if max_time < x['datetime'] else max_time)(comm_msg_info)
                                msg = m['app_msg_ext_info']
                                d = {}
                                d['url'] = msg['content_url']
                                d['submit_time'] = time.time()
                                config.redis_wx.rpush(config.redis_wx_news_queue_key, json.dumps(d))
                                if "multi_app_msg_item_list" in dict(msg).keys():
                                    msgs = msg['multi_app_msg_item_list']
                                    for msg in msgs:
                                        d = {}
                                        d['url'] = msg['content_url']
                                        d['submit_time'] = time.time()
                                        config.redis_wx.rpush(config.redis_wx_news_queue_key, json.dumps(d))
                            else:
                                # end
                                break
                        if max_time > ts:
                            insert_sql = "UPDATE wx_pbs SET lastnews = %s WHERE wx_biz = %s" % (
                            tools.quote_words(max_time), tools.quote_words(wx_biz))
                            cursor.execute(insert_sql)
                            conn.commit()
    except Exception as e:
        print(e)
        time.sleep(10)

