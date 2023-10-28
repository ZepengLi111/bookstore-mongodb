import logging
from pymongo import MongoClient
from pymongo import errors


class Store:
    database: str

    def __init__(self, db_url):
        self.client = MongoClient('mongodb://{}:27017/'.format(db_url))


    def get_db_conn(self):  # 返回MongoDB连接
        # 选择数据库
        self.mydb = self.client["be"]
        return self.mydb


database_instance: Store = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
