#!/usr/bin/python3.9.10
# -*- coding: utf-8 -*-
# @Time    : 2023/10/27 23:07
# @File    : insert_book.py
import pymongo
import sqlite3
import base64
import cv2
import numpy as np
import random




def main():
    # 1.硬盘上创建连接
    con = sqlite3.connect('book.db')
    con.row_factory = dict_factory
    # 获取cursor对象
    cur = con.cursor()
    # 执行sql查询
    sql = 'SELECT * FROM book'

    cur.execute(sql)
    books_data = cur.fetchall()
    # print(books_data)

    # 连接到 MongoDB 服务器
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017")

    # 选择数据库和集合
    db = client["be"]
    collection = db["book"]

    for x in books_data:
        book_id = x['id']
        del x['id']
        x['book_id'] = book_id
        x['belong_store_id'] = '1001'
        x['stock_level'] = random.randint(1, 1000)
        collection.insert_one(x)

        # 关闭游标
    cur.close()
    # 关闭连接
    con.close()





def dict_factory(cursor, row):
   d = {}
   for idx, col in enumerate(cursor.description):
       d[col[0]] = row[idx]
   return d

if __name__ == '__main__':
    main()
