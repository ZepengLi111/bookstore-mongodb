import logging
from pymongo import MongoClient
from pymongo import errors
import pymongo


class Store:
    database: str

    def __init__(self, db_url):
        self.client = MongoClient('mongodb://{}:27017/'.format(db_url))

    def get_db_conn(self):  # 返回MongoDB连接
        # 选择数据库
        self.mydb = self.client["be"]
        try:
            # 单键索引
            self.mydb['user'].create_index("user_id")
            self.mydb['order'].create_index("order_id")
            self.mydb['store'].create_index("store_id")
            # 复合索引， book_id 正序， belong_store_id 倒序
            self.mydb['book'].create_index([("book_id", pymongo.ASCENDING), ("belong_store_id", pymongo.DESCENDING)])
            self.mydb['book'].create_index([("_t", pymongo.TEXT)])
            print('---------->索引命中！')
        except Exception as e:
            print('---------->已存在索引！')
        return self.mydb

database_instance: Store = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
