# -*- coding: utf-8 -*-
import os

# 搜索关键词,返回json
SEARCH_SOURCE = "https://api.bilibili.com/x/web-interface/search/type?jsonp=jsonp&search_type=video&highlight=1&keyword={0}&from_source=nav_suggest&order=click&duration=0&page={1}&single_column=-1&tids=0"

'''
json结构
data -> result -> result(list, len = 20) -> aid; author; mid; play(播放量); tag; title
'''

# 通过aid即AV号获取cid
CID_SOURCE = "https://api.bilibili.com/x/player/pagelist?aid={0}&jsonp=jsonp"

'''
json结构
data(list, len = 1) -> cid; duration
'''

# 获取所有弹幕，返回的是xml文件,这里的oid就是cid
DANMAKU_SOURCE = "https://api.bilibili.com/x/v1/dm/list.so?oid={0}" 

# 默认搜索页数为50页数，B站最大搜索页数
PAGE_COUNT = 50

# 用户uid通过ITU I.363.5算法进行了Hash，根据Hash后的结果反推uid
USER_FIND_SOURCE = "https://biliquery.typcn.com/api/user/hash/{0}"

# 用户信息json, mid处填uid
USER_INFO_SOURCE = "https://api.bilibili.com/x/space/acc/info?mid={0}&jsonp=jsonp"
'''
json结构
data -> birthday; coins; level; name; sex; vip -> status
'''

# 设置User-Agent列表
User_Agent = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
]

# 根目录ROOT
ROOT = os.path.dirname(__file__)

# 设置休息时间，单位秒, 获取requests请求后的休息时间
REST_TIME = 0.5

# 设置user_hash获取requests请求时候的休息时间
USER_HASH_REST_TIME = 0

# 设置TIME_OUT_LIMIT，单位秒, 用于requests中，响应时间的最大值
TIME_OUT_LIMIT = 10

# 设置返回aid列表的时候,平均分的份数，也就是创建的保存aid的文件夹个数
DIV = 63

# 设置爬取数据被捕捉到的时候，停的时间
MEDIATE_TIME = 10 * 60

