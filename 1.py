#!/usr/bin/python3.9.10
# -*- coding: utf-8 -*-
# @Time    : 2023/10/27 20:46
# @File    : 1.py
import pymongo
import time
import datetime

# # 连接到 MongoDB 服务器
# client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
#
# # 选择数据库和集合
# db = client["be"]
# user = db["user"]
# user_store = db['user_store']
# #
#
# user.create_index({"user_id": 1})
#
# user_store_data = {"user_id":'222', "password":"222"}
# user.insert_one(user_store_data)

print("terminal_{}".format(str(time.time())))

# time_new = time.localtime(time.time() + 1800)
# print(time_new)
# time_new = time.strftime("[%Y-%m-%d %H:%M:%S]", time_new)
# print(time_new)