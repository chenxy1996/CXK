from model import *

# 用于在B站检索关键词，并在search目录下创建关键词目录，里面csv文件保存每个视频的基本信息，包括视频aid
def searchKeyWord(key_word):
    foo = Search(key_word)
    foo.createVideosInfoFile()

# 检索search目录下的name，并创建目录，以json格式记录一定数量的aid, cid.
def createAidCidDirectory(name):
    # 创建进程池
    pool = Pool()
    createAidDirectoryAndFile(name)
    aid_path_list = getAidPathList(name)
    pool.map(createCidFile, aid_path_list)
    pool.close()
    pool.join()

# 将search目录下,关键词key_word目录中,从范围[1, n]包括n的所有文件夹里面的cid_list.json，抽取弹幕和发送者消息
# 存入数据库
def extract(key_word, end, start = 1):
    key_word_dir = os.path.join(ROOT, "search", key_word)
    now = getCurrentTime()

    print(key_word_dir, start, end)
    if os.path.exists(key_word_dir):
        for i in range(start, end + 1):
            cid_dir_path = os.path.join(key_word_dir, str(i))
            insertAllCidInDirToDatabase(cid_dir_path, key_word)
    else:
        print("not exist.")
        
        




