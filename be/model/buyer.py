import sqlite3 as sqlite
import uuid
import json
import logging
from typing import Tuple, List, Any, Mapping

from be.model import db_conn
from be.model import error
from be.model import user
from pymongo import errors
import time
from datetime import datetime
from fe.data.utils import cut_word



class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.User = user.User()
        self.store = self.conn['store']
        self.user = self.conn['user']
        self.book = self.conn['book']
        self.order = self.conn['order']

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)], token:str) -> (int, str, str):
        order_id = ""
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message, order_id
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            order_amount = 0  # 总金额
            book_id_list = []
            book_count_list = []
            for book_id, count in id_and_count:

                result = self.book.find_one({'belong_store_id': store_id, 'book_id':book_id})
                # print(result)
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result['stock_level']
                book_info = result
                try:
                    book_info_json = json.loads(book_info)
                    price = book_info_json.get("price")
                except Exception as e:
                    price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result_1 = self.book.update_one({'belong_store_id':store_id,
                                                 'book_id':book_id,
                                                 'stock_level':{'$gte':count}},
                                                {'$inc': {'stock_level': (0-count)}})

                book_id_list.append(book_id)
                book_count_list.append(count)
                order_amount += (price*count)
                # order_detail_data = {'order_id':uid, 'seller_id':user_id,'book_id':book_id, 'count':count, 'price':price}
                # result_2 = self.order.insert_one(order_detail_data)
            creat_time = time.time()
            new_order_data = {'order_id': uid,
                              'buyer_id': user_id,
                              'creat_time': creat_time,
                              'payment_deadline': creat_time+1800,
                              'state': 0,
                              'order_amount': order_amount,
                              'seller_store_id': store_id,
                              'purchased_book_id': book_id_list,
                              'purchase_quantity': book_count_list}
            result_3 = self.order.insert_one(new_order_data)
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            code, message = self.User.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.order.find_one({'order_id': order_id})

            if result is None:
                return error.error_invalid_order_id(order_id)

            order_id = result['order_id']
            buyer_id = result['buyer_id']
            store_id = result['seller_store_id']
            total_price = result['order_amount']

            if buyer_id != user_id:
                return error.error_authorization_fail()

            result_1 = self.user.find_one({'user_id': buyer_id}, {'balance':1, "password":1})
            print('result_1----->',result_1)
            if result_1 is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = result_1['balance']
            if password != result_1['password']:
                return error.error_authorization_fail()

            result_2 = self.store.find_one({'store_id': store_id})
            print('result_2----->',result_2)
            if result_2 is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = result_2['seller_id']

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            print('total_price----->', total_price)

            if balance < total_price:
                return error.error_account_balance(buyer_id)

            result_4 = self.user.update_one({'user_id': buyer_id, 'balance':{'$gte':total_price}}, {'$inc': {'balance': (0-total_price)}})
            print('result_4----->',result_4)

            if result_4.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result_6 = self.order.update_one({'order_id': order_id},{'$set': {'state': 1}})
            print('result_6----->',result_6)

            if result_6.modified_count == 0:
                return error.error_invalid_order_id(order_id)

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "Payment successful"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            code, message = self.User.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.user.update_one({'user_id': user_id},{'$inc': {'balance': add_value}})
            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive(self, user_id:str, order_id:str, token: str) -> (int, str):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            
            result_order = self.order.find_one({"order_id": order_id})
            if result_order is None:
                return error.error_non_exist_order_id(order_id)
            elif result_order['state'] != 2:
                return error.error_order_state(result_order['state'])
            else:
                result = self.order.update_one({"order_id": order_id, "buyer_id": user_id}, {"$set": {"state": 3}})

        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def search_global(self, keyword, page) -> (int, str, list):
        try:
            keywords = ' '.join(cut_word(keyword))
            results = self.book.find({'$text':{'$search': keywords}}, {'_id':0, '_t':0})
            if page > 0:
                results = list(results.skip((page-1)*self.page_size).limit(self.page_size))
            elif page == 0:
                results = list(results)
            else:
                return error.error_invalid_parameter(page) + ([],)
            return 200,'ok', results
        except Exception as e:
            return 401, "{}".format(str(e)), ([],)
    
    def search_in_store(self, keyword, page, store_id) -> (int, str, list):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + ([],)
            keywords = ' '.join(cut_word(keyword))
            results = self.book.find({'$text':{'$search': keywords}, 'belong_store_id':store_id}, {'_id':0, '_t':0})
            if page > 0:
                results = list(results.skip((page-1)*self.page_size).limit(self.page_size))
            elif page == 0:
                results = list(results)
            else:
                return error.error_invalid_parameter(page) + ([],)
            results = list(results)
            return 200,'ok', results
        except Exception as e:
            return 401, "{}".format(str(e)), ([],)

    def search_order(self, user_id: str, token: str, search_state: int) -> (int, str, list):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ([],)
            if search_state == 0: # 查询所有订单
                results = self.order.find({'buyer_id': user_id})
                results = list(results)
                return 200, 'ok', results
            elif search_state == 1: # 查询待支付订单
                results = self.order.find({'buyer_id': user_id, 'state': 0})
                results = list(results)
                return 200, 'ok', results
            elif search_state == 2: # 查询已支付未发货
                results = self.order.find({'buyer_id': user_id, 'state': 1})
                results = list(results)
                return 200, 'ok', results
            elif search_state == 3: # 查询已发货未收货
                results = self.order.find({'buyer_id': user_id, 'state': 3})
                results = list(results)
                return 200, 'ok', results
            elif search_state == 4: # 查询已收货
                results = self.order.find({'buyer_id': user_id, 'state': 4})
                results = list(results)
                return 200, 'ok', results
            elif search_state == 5: # 查询已取消订单
                results = self.order.find({'buyer_id': user_id, 'state': 5})
                results = list(results)
                return 200, 'ok', results
        except Exception as e:
            return 401, "{}".format(str(e)) + ([],)

    def delete_order(self, user_id: str, order_id: str, token: str) -> (int, str):
        try:
            code, message = self.User.check_token(user_id, token)
            if code != 200:
                return code, message
            if not self.order_id_exist(user_id, order_id):
                return error.error_non_exist_user_id(user_id) + ([],)
            order_col = self.conn['order']
            result = order_col.find_one({'buyer_id': user_id,
                                         'order_id': order_id,
                                         'state': {'$in': [0, 1]}})
            self.order.update_one({'buyer_id': user_id,
                                   'order_id': order_id,
                                   'state': {'$in': [0, 1]}},
                                  {'$set': {'state': 5}})  # 修改待付款订单或未发货订单状态为删除状态
            # user_id, balance 更新用户余额
            self.user.update_one({'user_id': user_id},
                                 {'$inc': {'balance': result.get("order_amount")}})
            # purchased_book_id, purchase_quantity, 更新商店库存
            purchased_book_id = result.get('purchased_book_id')
            purchase_quantity = result.get('purchase_quantity')
            store_id = result.get('seller_store_id')
            for i in range(len(purchase_quantity)):
                _id = purchased_book_id[i]
                _q = purchase_quantity[i]
                self.book.update_one({'belong_store_id': _id, 'seller_store_id': store_id},
                                     {'$inc': {'stock_level': _q}})
            return 200, 'ok'
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

    def delete_order_time(self):
        try:
            order_col = self.conn['order']
            now = datetime.now()
            orders = order_col.find({"deadline":  {"$lt":  now}, "state": 0})
            for order in orders:
                order_col.delete_one({"order_id": order["order_id"]})
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
