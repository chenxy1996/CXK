# -*- coding: utf-8 -*-
from conf import *

import random, json, xlwt, requests, time, pymongo
import pandas as pd
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from datetime import datetime
from random import choice

# 得到当前时间
def getCurrentTime():
    current_time = str(datetime.now())[0:-7]
    current_time = current_time.replace(" ", "-")
    current_time = current_time.replace(":", "-")
    return current_time

# 随机选取conf中User_Agent列表中的任意一个
def getUserAgent():
    return random.choice(User_Agent)

# Requests请求:
def getResponse(url, rest_time = REST_TIME):
    headers = {
        "User-Agent": getUserAgent(),
    }
    response = requests.get(url, headers = headers, timeout = TIME_OUT_LIMIT)
    time.sleep(REST_TIME)
    return response
 
# 检索search文件夹下面的csv文件，找到目标，获取视频aid,平均分为DIV份，返回二维数组
def getAid(csv_file_path):
    all_aid_list = []
    data_frame = pd.read_excel(csv_file_path, encoding='gbk')
    aid_raw_data = data_frame["视频aid"].tolist()
    length = len(aid_raw_data)
    chunk_size = length // DIV
    start = 0
    end = 0
    i = 0
    while start < length:
        i += 1
        end = end + chunk_size
        current_aid_list = aid_raw_data[start:end]
        all_aid_list.append(current_aid_list)
        start = end
    return all_aid_list
     
# 通过输入包含aid的列表，返回cid列表
def getCid(aid_list):
    cid_list = []
    for each_aid in aid_list:
        cid_url = CID_SOURCE.format(each_aid)
        cid = json.loads(getResponse(cid_url, rest_time = USER_HASH_REST_TIME).text)["data"][0]["cid"]
        # print(cid)
        cid_list.append(cid)
    return cid_list

# 获取cid对应视频的所有弹幕，以及弹幕发送者的信息, 平均分成8份，返回二维数组.
def divideDanmakuList(cid, key_word):
    try:
        ret = [] # 返回值，每一项包含弹幕发送者信息和发送内容
        danmaku_url = DANMAKU_SOURCE.format(cid)
        xml = getResponse(danmaku_url, rest_time = USER_HASH_REST_TIME).content.decode("utf-8")
        xmlData = ET.fromstring(xml)
        danmaku_list = xmlData.findall("d")

        length = len(danmaku_list)
        chunk_size = length // 7
        start = 0
        end = 0
        i = 0
        while start < length:
            i += 1
            end = end + chunk_size
            danmaku_list_partition = danmaku_list[start:end]
            start = end
            ret.append((danmaku_list_partition, cid, key_word))
        return ret
    except requests.exceptions.ProxyError:
        print(cid)


# 有uid经hash后的user_hash账号，同个getUserInfo得到基本信息
def getUserInfo(user_hash):
    user_hash_id_url = USER_FIND_SOURCE.format(user_hash)
    user_hash_id_list = json.loads(getResponse(user_hash_id_url, rest_time = USER_HASH_REST_TIME).text)["data"]

    try:
        user_id = user_hash_id_list[1]["id"]
    except IndexError:
        user_id = user_hash_id_list[0]["id"]

    user_info_url = USER_INFO_SOURCE.format(user_id)
    user_info_json = json.loads(getResponse(user_info_url, rest_time = REST_TIME).text)

    # user_info_json["code"] == 0 判断账号有没有被封，如果被封了user_info_json["code"]: -404,没被封user_info_json["code"]: 0
    if user_info_json["code"] == 0:
        return {
            "name": user_info_json["data"]["name"],
            "sex": user_info_json["data"]["sex"],
            "birthday": user_info_json["data"]["birthday"],
            "coins": user_info_json["data"]["coins"],
            "level": user_info_json["data"]["level"],
            "vip": user_info_json["data"]["vip"]["status"],
            "mid": user_info_json["data"]["mid"],
        }
    else:
        return 

def insertDanmakuUserInfo(danmaku_list_partition):
    key_word = danmaku_list_partition[2]

    client = pymongo.MongoClient(host = "localhost", port = 27017)
    db = client.bilibili
    users_str = key_word + "_users"
    comments_str = key_word + "_comments"
    users = db[users_str]
    comments = db[comments_str]

    '''
    record
    '''
    user_true_count = 0
    user_error_count = 0

    comment_true_count = 0
    comment_error_count = 0

    check_user_error_count = 0

    cid = danmaku_list_partition[1]
    for each_danmaku in danmaku_list_partition[0]:

        # if check_user_error_count >= 8:
        #     raise TypeError
            
        if each_danmaku.get("p").split(",")[6]:
            user_hash = each_danmaku.get("p").split(",")[6]
            text = each_danmaku.text

            try:
                user_info = getUserInfo(user_hash)
                if user_info:
                    if not list(users.find({"mid": user_info["mid"]})):
                        check_user_error_count = 0
                        user_true_count += 1
                        users.insert_one(user_info)
                        print("User_Insert:True", user_info)
                    else:
                        print("User_Insert:False", user_info)

            except json.decoder.JSONDecodeError:
                user_error_count += 1
                check_user_error_count += 1
                print("User_error")
            
            try:
                comment_info = {}
                
                if user_info:
                    comment_info["mid"] = user_info["mid"]
                    comment_info["sender"] = user_info["name"]

                comment_info["content"] = text
                comment_info["cid"] = cid
                comments.insert_one(comment_info)
                print("Comment_Insert:True", comment_info)
                comment_true_count += 1
            except json.decoder.JSONDecodeError:
                comment_error_count += 1
                print("Comment_error")
    client.close()
            
    '''
    user_error_count数量过多
    '''
    if (user_error_count > 5 * user_true_count) and (user_error_count >= 50):
        raise TypeError
    
    # return "true_count: %d; false_count: %d" % (true_count, false_count) 
    return user_true_count, user_error_count, comment_true_count, comment_error_count

# 在search下找到name文件夹，得到csv文件下包括的所有视频aid消息, 再创立DIV或（DIV + 1）个文件夹，内部创建含有一定aid信息的json文件
def createAidDirectoryAndFile(name):
    file_root_dir_path = csv_file_path = os.path.join(ROOT, "search", name)
    csv_file_path = os.path.join(file_root_dir_path, name + "_index.xls")

    if not os.path.exists(csv_file_path):
        print("%s not exist." % csv_file_path)
    else:
        all_aid_list = getAid(csv_file_path)
        i = 0
        for each_aid_list in all_aid_list:
            i += 1
            file_dir_path = os.path.join(file_root_dir_path, str(i))
            os.mkdir(file_dir_path)
            aid_file = os.path.join(file_dir_path, "aid_list.json")

            with open(aid_file, "a") as f:
                json.dump(each_aid_list, f)

#  检索name目录下包含cid文件的文件夹, 返回有aid_list.json的文件目录列表
def getAidPathList(name):
    aid_path_list = []
    file_root_dir_path = csv_file_path = os.path.join(ROOT, "search", name)
    for each in os.listdir(file_root_dir_path):
        file_dir_path = os.path.join(file_root_dir_path, each)
        aid_file = os.path.join(file_dir_path, "aid_list.json")
        if os.path.exists(aid_file):
            aid_path_list.append(file_dir_path)
    return aid_path_list

#  在保存有aid_list.json文件下, 创建对应的cid_list.json文件
# param = [aid_list, file_dir_path]
def createCidFile(file_dir_path):
    aid_file = os.path.join(file_dir_path, "aid_list.json")
    with open(aid_file) as f:
            aid_list = json.load(f)
    if aid_list:
        cid_list = getCid(aid_list)
        cid_file = os.path.join(file_dir_path, "cid_list.json")
        with open(cid_file, "a") as f:
                json.dump(cid_list, f)

# 含有cid和aid的目录下,把cid_list.json文件储存的，切分成等长后，返回二维数组, 其中每一个元素element为一个数组
def getCidList(cid_dir_file):
    # ret = []
    cid_file = os.path.join(cid_dir_file, "cid_list.json")
    with open(cid_file) as f:
        cid_list = json.load(f)
    return cid_list

# 给每一个cid, 先用divideDanmakuList 函数把里面的弹幕信息平分，在多进程分别用insertDanmakuUserInfo函数
def insertToDatabase(cid,  key_word):
    separate_danmaku_list = divideDanmakuList(cid, key_word)
    pool = Pool()

    start_time = time.time()
    # 多进程
    try:
        record = pool.map(insertDanmakuUserInfo, separate_danmaku_list)
        pool.close()
        pool.join()
        end_time = time.time()

        execute_duration = str(int(end_time - start_time)) + "s"
        sum_user_true_count = 0
        sum_user_error_count = 0
        sum_comment_true_count = 0
        sum_comment_error_count = 0
        for each in record:
            sum_user_true_count += each[0]
            sum_user_error_count += each[1]
            sum_comment_true_count += each[2]
            sum_comment_error_count += each[3]

        # "cid: %s, sum_true_count: %s, sum_error_count: %s\n" % (cid, sum_true_count, sum_error_count)
        return {
            "cid": cid,
            "sum_user_true_count": sum_user_true_count,
            "sum_user_error_count": sum_user_error_count,
            "sum_comment_true_count": sum_comment_true_count,
            "sum_comment_error_count": sum_comment_error_count,
            "execute_duration": execute_duration,
        }

    except Exception as e:
        print(e)
        pool.close()
        pool.join()
        return False

# 把含有cid_json的目录下的cid_list.json中包含的所有cid，所对应的视频中的所有弹幕存入数据库
def insertAllCidInDirToDatabase(cid_dir_path, key_word):
    cid_list = getCidList(cid_dir_path)
    log = os.path.join(cid_dir_path, "log.json")
    log_array = []
    for each_cid in cid_list:
        if_execute = True
        while if_execute:
            # 如果顺利执行 insertToDatabase会返回字典if_execute会变成False, 
            # 没顺利执行会返回False,if_execute会变成True
            ret = insertToDatabase(each_cid, key_word)
            if_execute = not ret

            # 没有顺利执行
            if if_execute:
                print("%d分钟后继续" % (MEDIATE_TIME / 60))
                print(getCurrentTime())
                print(each_cid)
                time.sleep(MEDIATE_TIME / 2)
                print("%d分钟后继续" % (MEDIATE_TIME / 60 / 2))
                print(getCurrentTime())

                # 删除数据库中的一些数据
                client = pymongo.MongoClient(host = "localhost", port = 27017)
                db = client.bilibili # database
                comments_str = key_word + "_comments"
                comments = db[comments_str]
                comments.delete_many({"cid" : each_cid})
                time.sleep(MEDIATE_TIME / 2)
                client.close()

            # 顺利执行
            else:
                log_array.append(ret)

    with open(log, "a") as f:
        json.dump(log_array, f)
    return True

#类：搜索关键词,将结果存入csv文件中
class Search(object):

    # views为最小观看数; page_count为B站搜索页数，默认为在conf中设置为50页
    def __init__(self, key_word, play = 0, page_count = PAGE_COUNT):  
        self.key_word = key_word
        self.play = play
        self.page_count = page_count

    # 创建文件用于保存所搜索出的视频信息
    def createVideosInfoFile(self):
        file_dir_path = os.path.join(ROOT, "search", self.key_word)

        # 检查之前是否存在相同关键词的搜索,即已经存在关键词目录文件夹
        if os.path.exists(file_dir_path):
            print("之前已经搜索过{0}，是否再次搜索？y/n.".format(self.key_word))
            getchar = input()
            if getchar == "y":
                #创建新的文件夹，给这次的文件夹重新起名
                file_dir_path = os.path.join(ROOT, "search", self.key_word + "_" + getCurrentTime())
            else:
                file_dir_path = ""                 
        
        # 创建关键词目录文件夹
        if file_dir_path:
            os.mkdir(file_dir_path)
            video_info_generator = self.listVideosInfo()
            
            # 在文件夹中创建index.xls记录搜索出来的每个视频的信息
            # 定义单元格第一行样式
            style = xlwt.XFStyle()  # 初始化样式
            font = xlwt.Font()  # 为样式创建字体
            al = xlwt.Alignment()
            # 设置水平居中
            al.horz = 0x02
            font.name = "宋体"      
            # 设置字体颜色
            font.colour_index = 2
            # 字体大小
            font.height = 250
            # 定义格式
            style.font = font
            style.alignment = al

            # 定义单元格其它行样式，居中
            style_others = xlwt.XFStyle()
            font_others = xlwt.Font()
            font_others.height = 200
            font_others.name = "宋体"
            style_others.alignment = al
            style_others.font = font_others
            
            csv_file_path = os.path.join(file_dir_path, self.key_word + "_index.xls")
            csv_file = xlwt.Workbook(encoding='utf-8')
            sheet = csv_file.add_sheet("result")
            sheet.write_merge(0, 0, 0, 0, "序号", style)
            sheet.write_merge(0, 0, 1, 3, "up主", style)
            sheet.write_merge(0, 0, 4, 5, "up主mid", style)
            sheet.write_merge(0, 0, 6, 7, "视频aid", style)
            sheet.write_merge(0, 0, 8, 9, "视频播放量", style)
            sheet.write_merge(0, 0, 10, 11, "视频时长", style)
            sheet.write_merge(0, 0, 12, 20, "视频名称", style)
            sheet.write_merge(0, 0, 21, 29, "视频标签", style)

            for each in video_info_generator:
                sheet.write_merge(each["order"], each["order"], 0, 0, each["order"], style_others)
                sheet.write_merge(each["order"], each["order"], 1, 3, each["author"], style_others)
                sheet.write_merge(each["order"], each["order"], 4, 5, each["mid"], style_others)
                sheet.write_merge(each["order"], each["order"], 6, 7, each["aid"], style_others)
                sheet.write_merge(each["order"], each["order"], 8, 9, each["play"], style_others)
                sheet.write_merge(each["order"], each["order"], 10, 11, each["duration"], style_others)
                sheet.write_merge(each["order"], each["order"], 12, 20, each["title"], style_others)
                sheet.write_merge(each["order"], each["order"], 21, 29, each["tag"], style_others)
            
            csv_file.save(csv_file_path)
                   
    # 将符合条件的所有视频的信息存入生成器中
    def listVideosInfo(self):
        order = 0 # order 序号
        stop = False # stop 当视频的观看数小于前面设置的play时候，停止循环

        for i in range(1, self.page_count + 1):
            current_search_source = SEARCH_SOURCE.format(self.key_word, i)

            if stop:
                break

            # 每一页中的所有视频的json信息
            videos_one_page_info = json.loads(getResponse(current_search_source, rest_time = REST_TIME).text)["data"]["result"]

            time.sleep(REST_TIME)

            for each in videos_one_page_info:
                order += 1
                video_info = {}
                # video_info结构字典 {"author": , "mid":, "aid":, "play":, "tag":, "title": }

                # 判断此视频的播放了是否大于预设的量
                if int(each["play"]) < self.play:
                    stop = True
                    break

                video_info["order"] = order
                video_info["author"] = each["author"]
                video_info["mid"] = each["mid"]
                video_info["aid"] = each["aid"]
                video_info["duration"] = each["duration"]
                video_info["play"] = each["play"]
                video_info["tag"] = each["tag"]

                # 对title进行处理去掉里面的html标签
                titile = each["title"]
                titile = titile.replace('<em class="keyword">', "")
                titile = titile.replace("</em>", "")
                video_info["title"] = titile

                yield video_info