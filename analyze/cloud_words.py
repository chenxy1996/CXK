# -*- coding: utf-8 -*-
import pandas as pd
import os


# 从记录1000个视频的xls文件中提取关键词,存入一个列表并返回
def getKeywordList(path):
    keyword_list = []
    file = pd.read_excel(path)
    keyword_col = file["视频标签"]
    for each_string in keyword_col:
        each_string = each_string.replace(" ", "")
        each_string_list = each_string.split(",")
        keyword_list.extend(each_string_list)
    return keyword_list
        

# 统计关键词列表中的每个关键词的词频,返回一个字典,按照词频从多到少排序
def keywordCounter(keyword_list):
    keyword_frequency_dict = {}
    for each_word in keyword_list:
        try:
            keyword_frequency_dict[each_word] += 1
        except KeyError:
            keyword_frequency_dict[each_word] = 1
    keyword_frequency_dict = dict(sorted(keyword_frequency_dict.items(), 
                                key=lambda item: item[1], reverse=True))
    return keyword_frequency_dict


# 将字典导出成txt文件
def export(keyword_frequency_dict, save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        for each in keyword_frequency_dict.items():
            f.write(str(each[0]) + ";" + str(each[1]) + "\n")


if __name__ == "__main__":
    target_path = r"D:\computer\bilibili\search\蔡徐坤\蔡徐坤_index.xls"
    save_path = r"D:\computer\bilibili\search\蔡徐坤\keywords.csv"

    keyword_list = getKeywordList(target_path)
    keyword_frequency_dict = keywordCounter(keyword_list)
    export(keyword_frequency_dict, save_path)
