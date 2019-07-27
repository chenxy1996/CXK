# -*- coding: utf-8 -*-
from pymongo import MongoClient


class ConnectToMongo:
    def __init__(self, db="bilibili", comments="蔡徐坤_comments", users="蔡徐坤_users"):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client.get_database(db)
        self.comments = self.db.get_collection(comments)
        self.users = self.db.get_collection(users)
    
    def close(self):
        self.client.close()