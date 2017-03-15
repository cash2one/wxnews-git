import redis

# mysql
mysql_126_config = {
    "host": "10.13.1.126",
    "user": "root",
    "passwd": "qwe123",
    "db": "wxnews",
    'use_unicode': True,
    'charset': "utf8"
}


# redis weibo
redis_host_yanjun = "rm20258.eos.grid.sina.com.cn"      # 10G
redis_port_yanjun = 20258
redis_host_wx = "rc8946.hebe.grid.sina.com.cn"    # 1G
redis_port_wx = 8946
redis_host_elk = "rm20082.eos.grid.sina.com.cn"    # 10G
redis_port_elk = 20082


# weixin capture news
MSG_LIST_TEMPLATE = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s#wechat_webview_type=1&wechat_redirect'
redis_wx = redis.Redis(host=redis_host_wx, port=redis_port_wx)
redis_elk = redis.Redis(host=redis_host_elk, port=redis_port_elk)
redis_weixin_pc_set_key_prefix = "WEIXIN:PC_NEWS_SET:"
redis_weixin_news_queue_key = "WEIXIN_NEWS_QUEUE"

redis_wx_newslist_queue_key = 'WX:NEWSLIST_QUEUE'
redis_wx_news_queue_key = 'WX:NEWS_QUEUE'

# path
image_tmp_1 = "feeds/tmpImage"


# http://mp.weixin.qq.com/s?__biz=MjM5Njc5MzA5Mw==&mid=2653670303&idx=3&sn=6ad6033d95a4e434e87fe8390e1a91d8&chksm=bd3cb5f58a4b3ce31b0a59517ac76161605068b46664dead79c19ef3938ab1d03c901aa1db13&scene=0#rd
weixin_news_pattern = 'http://mp.weixin.qq.com/s\?__biz=(.*?)&mid=(.*?)&idx=(\d+?)&sn=(.*?).*'

add_url2mcq_api = 'http://i.tc.service.weibo.com/daemon/topnews/addurl2mcq4wx.php'
# weixin window about

wx_check_ret = [(63, 127, 98, 162), (63, 62, 98, 97)]

wx_window_width = 850
wx_window_height = 590
wx_window_gap = 200
wx_chat_w = 20
wx_chat_h = 60
wx_icon_pos_x = 65
wx_icon_pos_y = 65
wx_icon_width = 36
wx_icon_height = 36
wx_article_ret = (360, 90, 800, 440)
wx_pix_pos = (412, 58, 412, 59)
wx_mes_icon_pos = (23, 68)
wx_pub_rec_pos = (500, 80)
wx_return_pos = (330, 20)
wx_top_pos = (842, 55)
wx_pub_msg_box_height = 70
wx_click_pos = (550, 1010)
wx_show_msg_pos = (843, 1150)
wx_del_msg_pos = (600, 150)

# for wx
wx_x0 = 1
wx_x0 = 1
wx_x = 850
wx_y = 590