#! /usr/bin/env python3
# _*_ coding: UTF-8 _*_
import re
import json
import config
import requests
import pymysql
import datetime


text = """
"""
cursor = ""
conn = ""

conn = pymysql.connect(**config.mysql_126_config)
cursor = conn.cursor()

def make_request(url, times = 3):
    while times > 0:
        try:
            rq = requests.get(url)
            if rq and rq.status_code < 300:
                return rq
        except Exception as e:
            print(e)
            times -= 1


def quote_words(word):
    if isinstance(word, (int, bool, float)):
        return str(word)
    elif isinstance(word, str):
        return "\"" + word + "\""


def normal():
    exists = []
    for line in text.strip().split("\n"):
        fields = re.split('\s+', line)
        pb = {
            'local': fields[2],
            'wx_nick': fields[1],
            'wx_id': fields[0],
            'biz_url': fields[3],
            'wx_biz': fields[3][fields[3].find('biz=') + 4: fields[3].find('&mid')]
        }
        sql_query = "SELECT * FROM wx_pbs WHERE wx_biz = %s" % quote_words(pb['wx_biz'])
        cursor.execute(sql_query)
        ret = cursor.fetchall()
        print(ret)
        if not ret:
            # a = tuple(map(quote_words, (pb['local'], pb['wx_nick'], pb['wx_id'], pb['biz_url'], pb['biz_url'])))
            # print(a)
            sql_insert = "INSERT INTO wx_pbs( local, wx_nick, wx_id, biz_url, wx_biz, batches) VALUES (%s, %s, %s, %s, %s, %s)" % tuple(
                map(quote_words,
                    (pb['local'], pb['wx_nick'], pb['wx_id'], pb['biz_url'], pb['wx_biz'], '第四批城市扩展内容源')))
            # print(sql_insert)
            print(sql_insert)
            cursor.execute(sql_insert)
            conn.commit()
        else:
            exists.append(pb)
    conn.close()

    print("exists")
    for p in exists:
        print(p)


def travel():
    exists = []
    for line in text.strip().split("\n"):
        fields = re.split('\s+', line)
        pb = {
            'wx_nick': fields[0],
            'wx_id': fields[1],
            'wx_biz': fields[2]
        }
        sql_query = "SELECT * FROM wx_pbs WHERE wx_biz = %s" % quote_words(pb['wx_biz'])
        cursor.execute(sql_query)
        ret = cursor.fetchall()
        print(ret)
        if not ret:
            # a = tuple(map(quote_words, (pb['local'], pb['wx_nick'], pb['wx_id'], pb['biz_url'], pb['biz_url'])))
            # print(a)
            sql_insert = "INSERT INTO wx_pbs(wx_nick, wx_id, wx_biz, batches) VALUES (%s, %s, %s, %s)" % tuple(map(quote_words,(pb['wx_nick'], pb['wx_id'], pb['wx_biz'], '鲜城旅游需求')))
            # print(sql_insert)
            print(sql_insert)
            cursor.execute(sql_insert)
            conn.commit()
        else:
            exists.append(pb)
    conn.close()

    print("exists")
    for p in exists:
        print(p)


# 其他来源微信抓站需求
def other():
    exists = []
    for line in text.strip().split("\n"):
        fields = re.split('\s+', line)
        pb = {
            'wx_id': fields[0],
            'wx_nick': fields[1],
            'wx_biz': fields[2],
            'biz_url': fields[3],
            'class': fields[4],
            'level': fields[5]
        }
        sql_query = "SELECT * FROM wx_pbs WHERE wx_biz = %s" % quote_words(pb['wx_biz'])
        cursor.execute(sql_query)
        ret = cursor.fetchall()
        print(ret)
        if not ret:
            # a = tuple(map(quote_words, (pb['local'], pb['wx_nick'], pb['wx_id'], pb['biz_url'], pb['biz_url'])))
            # print(a)
            sql_insert = "INSERT INTO wx_pbs(wx_id, wx_nick, wx_biz, biz_url, class, level, batches) VALUES (%s, %s, %s, %s, %s, %s, %s)" % tuple(map(quote_words,(pb['wx_id'], pb['wx_nick'], pb['wx_biz'], pb['biz_url'], pb['class'], pb['level'], '其他来源微信抓站需求')))
            # print(sql_insert)
            print(sql_insert)
            cursor.execute(sql_insert)
            conn.commit()
        else:
            exists.append(pb)
    conn.close()

    print("exists")
    for p in exists:
        print(p)

def get_info_from_mysql():
    results = {}
    m = {
        "increase": 0,
        "wb_uid": 1,
        "wb_nick": 2,
        "wx_nick": 3,
        "wx_biz": 4,
        "wx_id_gh": 5,
        "wx_id": 6,
        "biz_url": 7,
        "local": 8,
        "local_code": 9,
        "batches": 10,
        "class": 11,
        "level": 12,
        "profile": 13,
        "lastnews": 14
    }
    cursor = conn.cursor()
    sql = "SELECT *  FROM `wx_pbs`"
    cursor.execute(sql)
    rets = cursor.fetchall()

    for ret in rets:
        result = {}
        for key, index in m.items():
            result[key] = ret[index]
        results[result['wx_id']] = result
    return results


def get_info_from_id():
    task = []
    info_mysql = get_info_from_mysql()

    file = open("C:\\Users\\sumi\\Desktop\\wxdata", 'r', encoding="utf-8")
    for line in file.readlines():
        fields = re.split("\s+", line.strip())
        if fields and len(fields) == 4:
            task.append({
                "wb_uid": fields[0],
                "wx_nick": fields[1],
                "wb_nick": fields[2],
                "wx_id": fields[3]
            })

    api = "http://www.newrank.cn/public/info/detail.html?account=%s"
    cursor = conn.cursor()
    for info in task:
        if info['wx_id'] in info_mysql.keys():
            continue
        else:
            wx_nick = info['wx_nick']
            wb_uid = info['wb_uid']
            wb_nick = info['wb_nick']
            wx_id = info['wx_id']

            url = api % wx_id
            r_g = make_request(url)
            if r_g:
                text = r_g.text
                matchers = re.findall(r"var fgkcdg = (.*);", text)
                if matchers:
                    n_info = json.loads(matchers[0])
                    r_p = requests.post(url="http://www.newrank.cn/xdnphb/detail/getAccountArticle", data={
                        "flag": True,
                        "uuid": n_info['uuid']
                    })
                    data = json.loads(r_p.text)
                    if data and "success" in data and data['success']:
                        if  wx_nick == n_info["name"]:
                            latest_news = data['value']['lastestArticle'][0]
                            wx_biz = latest_news["url"][latest_news['url'].find("__biz=") + 6:latest_news['url'].find("&mid")]
                            values = [wb_uid, wb_nick, wx_nick, wx_biz, n_info['wx_id'], wx_id, "开通微信文章转长文20170314", n_info['description'] if "description" in n_info else None, n_info['certified_text'] if "certified_text" in n_info else None, n_info['type'], n_info['uuid'], datetime.datetime.now()]
                            sql = "INSERT INTO `wx_pbs`(`wb_uid`, `wb_nick`, `wx_nick`, `wx_biz`, `wx_id_gh`, `wx_id`, `batches`, `profile`, `nr_certified_text`, `nr_type`, `nr_uuid`, `update_date`) VALUES %s" % "(" + ",".join(map(conn.escape, values)) + ")"
                            cursor.execute(sql)
                        else:
                            print("id与名称不匹配:", wb_uid, wx_nick, wb_nick, wx_id)
                else:
                    print("新榜未收录：", wb_uid, wx_nick, wb_nick, wx_id)
    cursor.close()


def get_info_from_newrank():


    data = {
        "filter": "",
        "hasDeal": "false",
        "keyName": "zhxiangzhou",
        "order": "NRI",
        "nonce": "34684b886",
        "xyz": "3695a589daffc670371edd9551527505"
    }

