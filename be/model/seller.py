import json
import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from be.model import user
from pymongo import errors


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.User = user.User()
        self.store = self.conn['store']
        self.user = self.conn['user']
        self.book = self.conn['book']
        self.order = self.conn['order']

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
            token: str
    ):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.user_id_exist(user_id):
                print('----->1')
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                print('----->2')
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                print('----->3')
                return error.error_exist_book_id(book_id)
            book_dict = json.loads(book_json_str)
            del book_dict['id']
            book_dict['book_id'] = book_id
            book_dict['belong_store_id'] = store_id
            book_dict['stock_level'] = stock_level
            self.book.insert_one(book_dict)
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int, token: str
    ):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            self.book.update_one({"belong_store_id": store_id, "book_id": book_id},{'$inc': {'stock_level': add_stock_level}})
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str, token: str) -> (int, str):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.store.insert_one({"store_id": store_id, "seller_id": user_id})
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "Successfully created the store"
    
    def send(self, user_id:str, order_id:str, token: str) -> int:
        try:
            # code, message = self.User.check_token(user_id, token)
            # if code != 200:
            #     return code, message
            
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            result = self.order.find_one({"order_id": order_id})
            if result is None:
                return error.error_non_exist_order_id(order_id)
            elif result['state'] != 1:
                return error.error_order_state(result['state'])
            else:
                result2 = self.order.update_one({"order_id": order_id, "seller_id": user_id}, {"$set": {"state": 2}})
                if result2.modified_count == 0:
                    return error.error_authorization_fail()

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

