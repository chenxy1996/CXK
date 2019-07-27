# -*- coding: utf-8 -*-
from snownlp import SnowNLP


SAVE_WORDS = ["nr", "n", "a", "e", "o"] # 需要留下词的词性
POP_OUT_WORDS = ["时候", "家伙"] # 剔除词的内容
SINGLE_WORDS = ["鸡", "瘦", "傻", "稳", "恶", "帅", "丑", "娘", "酷", "美"] # 单个字


# 对[('当', 'p'), ('他们', 'r'), ('黑', 'a'), ..., ('鹿', 'nr'), ('晗', 'nr')]这种
# 数据类型过滤,删除不需要的类型
def filter(seg_list): 
    i = 0
    ret = []
    length = len(seg_list)
    
    while i < length:
        if seg_list[i][1] in SAVE_WORDS and \
                seg_list[i][0] not in POP_OUT_WORDS:

            if seg_list[i][1] == "nr":
                current_string = ""
                while i < length and seg_list[i][1] == "nr":
                    print(seg_list[i][0])
                    current_string += seg_list[i][0]
                    i += 1
                if len(current_string) > 1:
                    ret.append(current_string)
            
            elif len(seg_list[i][0]) != 1 or seg_list[i][0] in SINGLE_WORDS:
                current_string = seg_list[i][0]
                ret.append(current_string)
        i += 1
        
    return list(set(ret)) # set()去重


def segProcess(content):
    curr_snownlp = SnowNLP(content)
    raw_tags = list(curr_snownlp.tags)
    return filter(raw_tags)


if __name__ == "__main__":
    test = '''当他们黑鹿晗演技的时候，我没有跟风；因为我不会演戏。当他们黑吴亦
                凡说唱的时候，我保持沉默；因为我不会说唱。当他们黑蔡徐坤打篮球
                的时候，我要站起来了，因为我真的会打篮球'''
    print(segProcess(test))
    