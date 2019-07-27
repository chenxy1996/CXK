# -*- coding: utf-8 -*-
'''
主程序函数说明：
'''
# 用于在B站检索关键词，并在search目录下创建关键词目录，里面csv文件保存每个视频的基本信息，包括视频aid
'''searchKeyWord(key_word)'''

# 检索search目录下的name，并创建目录，以json格式记录一定数量的aid, cid.
'''createAidCidDirectory(name)'''

# 将search目录下,关键词key_word目录中,从范围[1, n]包括n的所有文件夹里面的cid_list.json，抽取弹幕和发送者消息
# 存入数据库
'''extract(key_word, end, start = 1)'''


from execute import *

if __name__ == "__main__":
    # key_word = "蔡徐坤"
    # start = int(input("start = "))
    # end = int(input("end = "))
    # extract(key_word, start = start, end = end)
    # insertToDatabase(37759472, key_word="蔡徐坤")
    searchKeyWord("只狼")