import logging
import os
import pymongo


class Store:
    database: str

    def __init__(self, db_path):
        self.database = "mongodb://localhost:27017/"
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            # MongoDB 设置主键
            for colid in ['user_id', 'order_id', 'store_id', 'book_id']:
                col = colid[:-3]
                _test_str = f'_{colid}' 
                conn[col].insert_one({colid: _test_str})
                conn[col].create_index([(colid, 1)], unique=True)

        except pymongo.errors.ConnectionFailure as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):  # 返回MongoDB连接
        return pymongo.MongoClient(self.database)['bookstore']


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()