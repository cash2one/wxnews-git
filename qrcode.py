#! /usr/bin/env python3
# _*_ coding: UTF-8 _*_
import xlrd
import json
import os
import redis
import config
r = config.redis_wx
key = 'WX:PBS_MAP'


def merge_map(d1, d2):
    for key in d2.keys():
        if not key in d1.keys():
            d1[key] = d2[key]
    return d1

fields_map = {
    'wb_uid': ['UID'],
    'wb_nick': ['微博昵称'],
    'wx_biz': ['biz_id'],
    'id': ['编号'],
    'area': ['地区', '地域'],
    'wx_nick': ['微信名', '昵称', '匹配公众号昵称'],
    'wx_nick_secondary': ['修改后公号昵称'],
    'auth_status':['授权状态'],
    'auth_time': ['用户授权时间'],
    'operating_time': ['操作时间'],
    'operator': ['操作人'],
    'media': ['媒体'],
    'wx_id': ['微信号'],
    'biz_uri': ['带biz链接', '示例链接'],
    'priority': ['优先级'],
    'classification': ['地域/分类'],
    'submit_date': ['提出日'],
    'profile': ['简介'],
    'food_status': ['美食内容情况']
}

fs = {
    # 'new.xlsx': [
    #     'Sheet1'
    # ],
    '第二批城市微信来源_20161114.xlsx': [
        '筛选后可抓取的来源'
    ],
    '第二批城市微信号1108.xlsx': [
        'Sheet1 (2)'
    ],
    '微信抓取列表.xlsx': [
        '内容交换平台',
        '微信号排行榜',
        '运营标定'
    ]
}

base = 'C:/Users/Sumi/Desktop'
ret = []
for file, desc in fs.items():
    file = os.path.join(base, file)
    if os.path.exists(file):
        book = xlrd.open_workbook(file)
        for sheet_name in desc:
            sheet = book.sheet_by_name(sheet_name)
            fm = {}
            for col in range(0, sheet.ncols):
                cell = sheet.cell(0, col)
                value = cell.value.__str__()
                for field, keywords in fields_map.items():
                    if value in keywords:
                        fm[field] = col
            if not 'wx_biz' in fm.keys():
                if not 'wx_id' in fm.keys():
                    raise Exception
            for row in range(1, sheet.nrows):
                p = {}
                for f, index in fm.items():
                    p[f] = sheet.cell(row, index).value
                if 'biz_uri' in p.keys() and p['biz_uri']:
                    if 'wx_biz' not in p.keys():
                        p['wx_biz'] = ''.join(map(lambda x: x[6:] if x.startswith('__biz=')else '', p['biz_uri'].split('?')[1].split('&')))
                if 'wx_biz' in p.keys() and p['wx_biz']:
                    p['key-type'] = 'wx_biz'
                elif 'wx_id' in p.keys() and p['wx_id']:
                    p['key-type'] = 'wx_id'
                else:
                    continue
                ret.append(json.dumps(p))

for (i,p) in enumerate(ret):
    a = json.loads(p)
    pk = a[a['key-type']]
    if not r.hexists(key, pk):
        r.hset(key, pk, json.dumps(a))
    else:
        oj = dict(json.loads(r.hget(key, pk).decode('utf-8')))
        j = merge_map(oj, a)
        print('original: ' + str(oj))
        print(j)
        r.hset(key, pk, json.dumps(j))
