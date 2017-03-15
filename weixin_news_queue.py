#! /usr/bin/env python3
# _*_ coding: UTF-8 _*_
import redis
import re
import requests
import urllib
import datetime
import json
import config




biz_map_key = "WEIXIN:BIZ_MAP"
r = redis.Redis(host="rm20082.eos.grid.sina.com.cn", port=20082)
show_info_api = 'http://i.tc.service.weibo.com/tc/api.php'
log_key = "json-wechat-android"


def makeRequest(url, method='get', times=10, encoding='utf-8'):
    count = times
    while count > 0:
        try:
            if method == 'get':
                response = requests.get(url)
                response.encoding = encoding
                return response
        except Exception as e:
            print(e)
            count -= 1


def getInfo(wxurl):
    info_regex = r'__biz=([\w=]+)&mid=(\d+)&idx=(\d)&sn=(\w+)&'
    ret = re.findall(info_regex, wxurl)
    if len(ret) == 1:
        info = {}
        info['biz'] = ret[0][0]
        info['mid'] = ret[0][1]
        info['idx'] = ret[0][2]
        info['sn'] = ret[0][3]
        return info
    elif len(ret) == 0:
        regex = r'var msg_link = "(.*?)"'
        r = makeRequest(wxurl)
        matchers = re.search(regex, r.text)
        if matchers:
            url = matchers.group(1).replace('\\x26amp;', '&')
            if len(re.findall(info_regex, url)) == 1:
                return getInfo(url)
        else:
            print("Maybe rumor")
            return False


def get_src(ori):
    if isinstance(ori, tuple):
        return get_src(ori[1])
    else:
        try:
            return json.loads(ori.decode('utf-8'))
        except Exception as e:
            print("Exception: " + str(e))


while 1:
    try:
        log_dict = {}
        ori = r.blpop("WEIXIN_NEWS_QUEUE")
        oj = get_src(ori)
        url = oj.pop("url", "ERROR")
        log_dict['url'] = url
        log_dict['from'] = oj.pop('source', oj.pop('serial', 'ERROR'))
        log_dict['enqueue_time'] = str(oj.pop('submit_time', "ERROR")) + '.000Z'
        info = getInfo(url)
        if info:
            if r.hexists(biz_map_key, info['biz']):
                ins = dict(json.loads(r.hget(biz_map_key, info['biz']).decode('utf-8').replace('\'', '"')))
                log_dict['nick'] = ins.pop("nick", "ERROR")
                log_dict['id'] = ins.pop('id', "ERROR")
                log_dict['biz'] = info['biz']
            else:
                info_regex = 'profile_nickname">(.*)<([\s\S]*?)value">(.*?)<([\s\S]*?)value">(.*?)<'
                text = makeRequest(url).text
                biz_info = {}
                log_dict['biz'] = info['biz']
                regex_match = re.search(info_regex, text)
                if regex_match:
                    biz_info['biz'] = info['biz']
                    biz_info['nick'] = regex_match.group(1)
                    biz_info['id'] = regex_match.group(3)
                    biz_info['desc'] = regex_match.group(5)
                    r.hset(biz_map_key, biz_info['biz'], json.dumps(biz_info))
                    log_dict['nick'] = regex_match.group(1)
                    log_dict['id'] = regex_match.group(3)
        else:
            raise Exception
            print("Get info error:",  ori)
            print("Add to WEIXIN_NEWS_QUEUE_FAILURE:")
            print(info)
        url = config.add_url2mcq_api + '?url=' + urllib.parse.quote(log_dict['url'])
        response = makeRequest(url)
        if response and response.text.find("入转码队列成功") != -1:
            log_dict['log_time'] = str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')) + '.000Z'
            print("ADD WEIXIN URL TO MCQ: " + str(log_dict))
            r.rpush(log_key, str(log_dict).replace('\'', '"'))
        elif response.text.find("不在抓取范围内") == -1:
            raise Exception
        else:
            print("不在抓取范围内：", str(log_dict))
    except Exception as e:
        print("Error:\nItem: " + str(ori))
        print("Add to WEIXIN_NEWS_QUEUE_FAILURE:")
        r.rpush("WEIXIN_NEWS_QUEUE_FAILURE", ori[1])
        print(e)
