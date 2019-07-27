# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from db_operation import getDataFromDb
from cloud_words import keywordCounter, export

# 性别比例分布
def genderDistribution(gender_list):
    labels = [each[0] for each in gender_list]
    quantity = [each[1] for each in gender_list]
    fig1, ax1 = plt.subplots()
    ax1.pie(quantity, labels=labels, autopct='%1.2f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()


# 格式化日期和月份格式, 1月份则返回"01", 10月份返回"10", 1号返回"01", 12号返回"12"
def trans(num):
    if num < 10:
        return "0" + str(num)
    elif num >= 2:
        return str(num)


# 从起始月份到结束月份的所有日期，返回一个列表
def birthdayList(month_start, month_end):
    big_month = [1, 3, 5, 7, 8, 10, 12]
    birthday_list = []
    curr_month = month_start
    while curr_month <= month_end:        
        curr_month_string = trans(curr_month)
        day = 1
        if curr_month in big_month:
            while day <= 31:
                day_string = trans(day)
                birthday_list.append(curr_month_string + "-" + day_string)
                day += 1
        elif curr_month == 2:
            while day <= 29:
                day_string = trans(day)
                birthday_list.append(curr_month_string + "-" + day_string)
                day += 1
        else:
            while day <= 30:
                day_string = trans(day)
                birthday_list.append(curr_month_string + "-" + day_string)
                day += 1
        curr_month += 1
    return birthday_list


# 人数的分布
def distribution(curr_list):
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    count_list = []
    for each in curr_list[1]:
        count = len(getDataFromDb(filter={curr_list[0]: each},\
                                    projection={"_id": 0, "birthday": 1}, \
                                        col_name="蔡徐坤_users"))
        count_list.append(count)
    ax = plt.subplots()[1]
    b = ax.bar(curr_list[1], count_list,\
            alpha=0.7, color='g',)
    for each in b:
        height = each.get_height()
        ax.text(each.get_x()+each.get_width()/2, height, "%d"%int(height), \
                        ha="center", va="bottom", color="grey", fontsize=8, rotation=60)
    plt.xticks(fontsize=8, color="grey", rotation=90)
    plt.yticks(fontsize=8, color="grey")
    ax.set_ylabel('人数', color='black', alpha=0.75)
    plt.show()


# 得到发送的弹幕条数"comments_count"和发送者数量之间的关系，以及在多少个视频"cid_count"发送过弹幕
# 和发送者数量之间的关系, 最后输出两个csv文件
def userCommAndCidCount():
    users_list = getDataFromDb({}, projection = {"_id": 0, "comments_count": 1, "cid_count": 1} ,\
                                        col_name = "蔡徐坤_users")

    # comments_count_list = [each["comments_count"] for each in users_list]
    # cid_count_list = [each["cid_count"] for each in users_list]
    comments_count_list = []
    cid_count_list = []

    for each in users_list:
        try:
            comments_count_list.append(each["comments_count"])
        except KeyError:
            pass
        
        try:
            cid_count_list.append(each["cid_count"])
        except KeyError:
            pass
    
    comments_count_frequency = list(keywordCounter(comments_count_list).items())
    cid_count_frequency = list(keywordCounter(cid_count_list).items())

    comments_count_frequency = dict(sorted(comments_count_frequency, key=lambda x: x[0]))
    cid_count_frequency = dict(sorted(cid_count_frequency, key=lambda x: x[0]))

    # export(comments_count_frequency, r"D:\computer\bilibili\search\蔡徐坤\_comments_count_frequency.csv")
    # export(cid_count_frequency, r"D:\computer\bilibili\search\蔡徐坤\_cid_count_frequency.csv")

    return comments_count_frequency, cid_count_frequency


# 人数分布，通用版函数
def generalDistributionFunc(name_list, count_list):
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']

    ax = plt.subplots()[1]
    b = ax.bar(name_list, count_list,\
            alpha=0.7, color='g',)
    for each in b:
        height = each.get_height()
        ax.text(each.get_x()+each.get_width()/2, height, "%d"%int(height), \
                        ha="center", va="bottom", color="grey", fontsize=8, rotation=60)
    plt.xticks(fontsize=8, color="grey", rotation=90)
    plt.yticks(fontsize=8, color="grey")
    ax.set_ylabel('人数', color='black', alpha=0.75)
    plt.show()


# 给人数数区间[1, 2, 3, 4, 5, (6, 10)...],统计各项的人数
def intervalCount(interval_list, count_frequency):
    interval_frequency = []
    interval_name_list = []
    sum_frequency = sum(list(count_frequency.values()))

    for i in interval_list:
        if isinstance(i, int):
            if i != interval_list[-1]:
                curr_frequency = count_frequency.get(i, 0)
                curr_name = str(i)
            else:
                curr_frequency = sum_frequency - sum(interval_frequency) - count_frequency.get(0, 0)
                curr_name = "≥" + str(i)
        else:
            start, end = i[0], i[1] + 1
            curr_frequency = 0
            for each_num in range(start, end):
                curr_frequency += count_frequency.get(each_num, 0)
            curr_name = "[" + str(start) + ", " + str(end - 1) + "]" 
        
        interval_frequency.append(curr_frequency)
        interval_name_list.append(curr_name)
    
    return interval_name_list, interval_frequency

        
if __name__ == "__main__":
    # genderDistribution([(u"female: 61165", 61165), (u"male: 58043", 58043), (u"secret: 195801", 195801)])
    # a = birthdayDistribution(1, 12)
    # print(a)
    # constellation_dict = {
    #     "山羊座": (12.21, 1.20),
    #     "水瓶座": (1.21, 2.19),
    #     "双鱼座": (2.20, 3.20),
    #     "白羊座": (3.21, 4.19),
    #     "金牛座": (4.20, 5.20),
    #     "双子座": (5.21, 6.21),
    #     "巨蟹座": (6.22, 7.22),
    #     "狮子座": (7.23, 8.22),
    #     "处女座": (8.23, 9.22),
    #     "天秤座": (9.23, 10.23),
    #     "天蝎座": (10.24, 11.21),
    #     "射手座": (11.22, 12.20),
    # }
    # mojie = ['12-22', '12-23', '12-24', '12-25', '12-26', '12-27', '12-28', '12-29', '12-30', '12-31', 
    #            '01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07', 
    #            '01-08', '01-09', '01-10', '01-11', '01-12', '01-13', '01-14', 
    #            '01-15', '01-16', '01-17', '01-18', '01-19']
    # _list = ["birthday", mojie]
    # print(_list)
    # constellation_list = list(constellation_dict.keys())
    # print(constellation_list)
    # distribution(_list)
    # genderDistribution([(u"female_danmaku_count: 190223", 190223), (u"male_danmaku_count: 104258", 104258), (u"secret_danmaku_count: 464154", 464154)])
    # comments_count_frequency, cid_count_frequency = userCommAndCidCount()

    # comments_count_list = list(comments_count_frequency.keys())
    # comments_count_frequency_list = list(comments_count_frequency.values())
    # generalDistributionFunc(comments_count_list, comments_count_frequency_list)

    # cid_count_list = list(cid_count_frequency.keys())
    # cid_count_frequency_frequency_list = list(cid_count_frequency.values())
    # generalDistributionFunc(cid_count_list, cid_count_frequency_frequency_list)

    # interval_list = [1, 2, 3, 4, 5, (6, 10),
    #                     (11, 15), (16, 30), (31, 100), 100]
    interval_list = [1, 2, 3, 4, 5, (6, 10),
                        (11, 15), (16, 30), 31]

    
    # comments_and_cid_count_frequency = userCommAndCidCount()
    # comments_count_frequency = comments_and_cid_count_frequency[0]
    # cid_count_frequency = comments_and_cid_count_frequency[1]

    # comments_info = intervalCount(interval_list, comments_count_frequency)
    # comments_interval_count_name = comments_info[0]
    # comments_interval_count_frequency = comments_info[1]

    # cid_info = intervalCount(interval_list, cid_count_frequency)
    # cid_interval_count_name = cid_info[0]
    # cid_interval_count_frequency = cid_info[1]

    # generalDistributionFunc(comments_interval_count_name, comments_interval_count_frequency)
    # generalDistributionFunc(cid_interval_count_name, cid_interval_count_frequency)

    raw_comments_list = getDataFromDb({"mid" : 66137469}, projection={"_id": 0, "content": 1})
    comments_list = [each["content"] for each in raw_comments_list]
    print(comments_list, len(comments_list))
    with open(r"C:\Users\陈翔宇\Desktop\杠我者杖毙哦_content.txt", "w", encoding="utf-8") as f:
        for each_comment in comments_list:
            f.write(each_comment + ";" + "1\n")
    

    
