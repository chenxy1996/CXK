# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import pymongo

from pymongo import MongoClient
from bson import ObjectId

from snownlp import normal
from snownlp import seg
from snownlp.summary import textrank
from snownlp import SnowNLP
from snownlp import sentiment

from connect_to_mongo import ConnectToMongo
from multiprocessing import Pool
from danmaku_seg import segProcess


REFINE_LIST = [[".*蔡徐坤.*", "蔡徐坤"], [".*范丞.*", "范丞丞"], \
                [".*吴亦.*", "吴亦凡"], [".*哈哈.*", "哈哈哈"], [".*233.*", "2333"], \
                   [".*林彦.*", "林彦俊"], [".*彦俊.*", "林彦俊"], \
                    [".*朱正.*", "朱正廷"], [".*正廷.*", "朱正廷"], [".*律师.*", "律师函"], \
                        [".*66.*", "666"]]


# 把一个列表或别的均分，返回二维数组[[list1], ..., [listN]]
def divide(target, part_num = 12):
    ret = [] # 返回值
    sum_count = len(target)
    chunk_size = sum_count // part_num
    if chunk_size:
        start = 0
        end = 0
        while start < sum_count:
            end += chunk_size
            targey_partition = target[start:end]
            start = end
            ret.append(targey_partition)
        return ret
    else:
        return [target]
    

# 得到content的sentiment系数
def getSentimentalIndex(content):
    s = SnowNLP(content)
    index = round(s.sentiments, 4)
    return index


# 根据出生日期得到星座
def getConstellation(birthday_string):
    birthday_string = birthday_string.replace("-", ".")
    birthday_num = float(birthday_string)
    constellation_dict = {
        "山羊座": (12.21, 1.20),
        "水瓶座": (1.21, 2.19),
        "双鱼座": (2.20, 3.20),
        "白羊座": (3.21, 4.19),
        "金牛座": (4.20, 5.20),
        "双子座": (5.21, 6.21),
        "巨蟹座": (6.22, 7.22),
        "狮子座": (7.23, 8.22),
        "处女座": (8.23, 9.22),
        "天秤座": (9.23, 10.23),
        "天蝎座": (10.24, 11.21),
        "射手座": (11.22, 12.20),
    }
    
    for each in constellation_dict:
        if each != "山羊座":
            if constellation_dict[each][0] <= birthday_num and\
                birthday_num <= constellation_dict[each][1]:
                    return each
        else:
            if constellation_dict[each][0] <= birthday_num or\
                birthday_num <= constellation_dict[each][1]:
                    return each


# 给数据库中comments集合中的每一个document根据其content，添加sentiment <field>
def addSentimentToComment():
    client = ConnectToMongo()
    comments = client.comments
    count = 0
    current_cid_comments = comments.find({})
    for each in current_cid_comments:
        count += 1
        id = each["_id"]
        content = each["content"]
        sentiment = getSentimentalIndex(content)
        comments.update_one({"_id": id}, {"$set": {"sentiment": sentiment}})
        print(count, content, sentiment)
    client.close()


# 给users_set集合中的每一个document根据其出生日期，添加星座;并添加评论数量;
def addConsAndCommCountToUsers(users_set): 
    client = ConnectToMongo()
    comments = client.comments
    users = client.users

    for each_user in users_set:
        mid = each_user["mid"]
        name = each_user["name"]
        constellation = each_user["constellation"]

        comments_count = comments.count_documents({"mid": mid})
        users.update_one({"mid": mid}, {"$set": {"constellation": \
                            constellation, "comments_count": comments_count}})
        print(name, constellation, comments_count)
    client.close()


# 给users_set集合中的每一个document添加给多少个视频发过弹幕(同一cid视频发送多个弹幕只算一个);
def addCidCountToUsers(users_set): 
    client = ConnectToMongo()
    comments = client.comments
    users = client.users

    for each_user in users_set:
        mid = each_user["mid"]
        name = each_user["name"]
        cid_stack = []
        count = 0
        curr_mid_comments = comments.find({"mid": mid})
        for each_comment in curr_mid_comments:
            if each_comment["cid"] not in cid_stack:
                cid_stack.append(each_comment["cid"])
                count += 1
                
        users.update_one({"mid": mid}, {"$set": {"cid_count": count}})
        print(name, count)

    client.close()


# 给comments_set集合中的每一个document添加星座;并添加发送者性别;
def addConstsAndSexToComments(users_set): 
    client = ConnectToMongo()
    comments = client.comments

    for each_user in users_set:
        name = each_user["name"]
        mid = each_user["mid"]
        sex = each_user["sex"]
        constellation = each_user["constellation"]
        comments.update_many({"mid": mid}, {"$set": {"constellation": \
                            constellation, "sex": sex}})
        print(name, constellation, sex)
    client.close()


# 给集合female_cloud_words或male_cloud_words添加document————关键词以及权重提取
def createCloudWords(params): 
    name = params[0] #name: female或male
    comments_set = params[1] # comments_set: [{comments:####}, {}, ..., {}]
                                                        
    client = MongoClient()
    db = client.get_database("bilibili")
    col = db.get_collection(name + "_cloud_words")
    comments_col = db.get_collection("蔡徐坤_comments")

    for each_comment in comments_set:
        curr_comm_id = each_comment["_id"]
        curr_comm_keywords = segProcess(each_comment["content"])
        comments_col.update_one({"_id": curr_comm_id}, {"$set": {"ifSeg": 1}})       
        for each_keyword in curr_comm_keywords:
            col.update_one({"word" : each_keyword}, {"$inc": {"count": 1}}, upsert=True)
            print(each_keyword, "+1")
        
    client.close()


# 给users中全部数据添加新的field
def mainForUsers(filter, processes_num, function_name):
    client = ConnectToMongo()
    users_col = client.users
    users = list(users_col.find(filter, {"birthday": 1, "mid": 1, "name": 1}))
    client.close()
    all_users_set = divide(users)
    pool = Pool(processes_num)  
    pool.map(function_name, all_users_set)
    pool.close()
    pool.join()


# 给comments集合中全部数据添加新的field
def mainForComments(processes_num):
    client = ConnectToMongo()
    users_col = client.users
    users = list(users_col.find({"comments_count": {"$exists": True}}, 
                                    {"mid": 1, "constellation": 1, "name": 1, "sex": 1}))
    client.close()
    all_users_set = divide(users)
    pool = Pool(processes_num)  
    pool.map(addConstsAndSexToComments, all_users_set)
    pool.close()
    pool.join()


# 关键词词云
def mainForKeywords(name, progress_num):
    if name == "female":
        sex = u"女"
    elif name == "male":
        sex = u"男"

    client = ConnectToMongo()
    comments_col = client.comments
    comments = list(comments_col.find({"sex": sex, "ifSeg": {"$exists": False}}, {"content": 1})) # "ifSeg": {"$exists": False}
    client.close()
    all_comments_set = divide(comments)
    params_list = []
    for each in all_comments_set:
        params_list.append([name, each])
    pool = Pool(progress_num)  
    pool.map(createCloudWords, params_list)
    pool.close()
    pool.join()

# 对现有的云词（关键词及其词频）， 做整合和优化。
# 由于关键词分割的遗留问题，造成一些关键词未能很好的提取出来。
# 例如“蔡徐坤”， “蔡徐坤蔡”等等
def collateCloudWord(refine_list = REFINE_LIST): 
    client = MongoClient()
    db = client.get_database("bilibili")
    female_col = db.get_collection("female_cloud_words")
    male_col = db.get_collection("male_cloud_words")

    for each in REFINE_LIST:
        regex = each[0]
        target = each[1]

        female_regex_mathched_list = female_col.find({"word": {"$regex": regex}})
        male_regex_mathched_list = male_col.find({"word": {"$regex": regex}})

        print("-------------------------------------")
        for female_each in female_regex_mathched_list:
            word_content = female_each["word"] 
            if word_content != target:
                current_count = female_each["count"]
                female_col.update_one({"word": target}, {"$inc": {"count": current_count}})
                female_col.delete_one({"word": word_content})
                print(word_content, current_count)
        
        for male_each in male_regex_mathched_list:
            word_content = male_each["word"] 
            if word_content != target:
                current_count = male_each["count"]
                male_col.update_one({"word": target}, {"$inc": {"count": current_count}})
                male_col.delete_one({"word": word_content})
                print(word_content, current_count)
    client.close()


# 从female_cloud_words或male_cloud_words词云中提取数据, 存入csv文件中
def getKeywordsFromCloudWordsCOl(nums): # nums为获取的数量
    client = MongoClient()
    db = client.get_database("bilibili")
    female_col = db.get_collection("female_cloud_words")
    male_col = db.get_collection("male_cloud_words")
    female_frequency_list = female_col.find().sort("count", pymongo.DESCENDING).limit(nums)
    male_frequency_list = male_col.find().sort("count", pymongo.DESCENDING).limit(nums)
    client.close()
    
    with open("female_frequency.csv", "w", encoding="utf-8") as f:
        for each_doc in female_frequency_list:
            f.write(each_doc["word"] + ";" + str(each_doc["count"]) + "\n")
    
    with open("male_frequency.csv", "w", encoding="utf-8") as f:
        for each_doc in male_frequency_list:
            f.write(each_doc["word"] + ";" + str(each_doc["count"]) + "\n")


# 从数据库中拿到数据, 返回列表
def getDataFromDb(filter, projection=None, col_name = "蔡徐坤_comments", db_name="bilibili"):
    client = MongoClient()
    db = client.get_database(db_name)
    col = db.get_collection(col_name)
    ret = list(col.find(filter, projection))
    client.close()
    return ret

        
if __name__ == "__main__":  
    # mainForKeywords("male", 4)
    # params = mainForKeywords("female", 8)
    # createCloudWords(params)
    # collateCloudWord()
    # getKeywordsFromCloudWordsCOl(100)
    # mainForUsers({"cid_count": {"$exists": False}}, function_name=addCidCountToUsers, processes_num=6)
    # test = getDataFromDb({"sex": "男"}, {"_id": 0, "sentiment": 1})
    # print(len(test))
    index1 = getSentimentalIndex(u"666")
    index2 = getSentimentalIndex(u"哈哈哈")
    print("%s: %s" % (u"666", index1))
    print("%s: %s" % (u"哈哈哈", index2))