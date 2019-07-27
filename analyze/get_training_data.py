# -*- coding: utf-8 -*-
from connect_to_mongo import ConnectToMongo


def getTrainingData(cid_list):
    client = ConnectToMongo()
    comments = client.comments
    comments_store = []
    count = 0
    for each_cid in cid_list:       
        curr_cid_commnets = comments.find({"cid": each_cid})
        for each_comment in curr_cid_commnets:
            count += 1
            comments_store.append(each_comment["content"] + "\n")
            print(count, each_comment["content"])     
    return list(set(comments_store))


if __name__ == "__main__":
    # neg_cid_list = [83089367, 76260515, 83538114, 75569308, 85506298, 
    #                 86592768, 78535232, 82707163, 82978644, 78896123, 
    #                 82199455, 52979890, 85436034, 79151718, 86622000,
    #                 85993304, 84038735, 85031311, 84514945, 83256002, 
    #                 85655712, 85808590, 85305796, 82516608, 76223413, 
    #                 78057475, 86301149, 83225996, 24208217, 86362759, 
    #                 74053969, 83143548, 83940042, 69623545, 77082680, 
    #                 86144562, 81498702, 83195443, 85987047, 85519168, 
    #                 84848132, 87311737, 82376700, 81360161, 69899592, 
    #                 71676562, 86998434, 33785229, 84302664, 85115582, 
    #                 76649226]

    neg_cid_list = [83089367, 76260515, 83538114]                
    a = getTrainingData(neg_cid_list)
    with open(r"d:\neg1.txt", "w", encoding='utf-8') as f:
        f.writelines(a)
