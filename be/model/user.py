import jwt
import time
import logging
import pymongo
from pymongo import errors
from be.model import error
from be.model import db_conn


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    """
    编码
    :param user_id:
    :param terminal:
    :return:
    """
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    """
    解码
    :param encoded_token:
    :param user_id:
    :return:
    """
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        if self.user_id_exist(user_id):
            return error.error_exist_user_id(user_id)  # 处理重复用户ID的情况
        else:
            try:
                terminal = "terminal_{}".format(str(time.time()))
                token = jwt_encode(user_id, terminal)
                user_col = self.conn['user']
                user1 = {
                    "user_id": user_id,
                    "password": password,
                    "balance": 0,
                    "token": token,
                    "terminal": terminal,
                }
                user_col.insert_one(user1)
            except errors.PyMongoError as e:
                return error.database_error(e)  # 处理其他数据库相关的异常
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        user_col = self.conn['user']
        result = user_col.find_one({'user_id': user_id})
        if result is None:
            return error.error_authorization_fail()
        db_token = result['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user_col = self.conn['user']
        result = user_col.find_one({'user_id': user_id})
        if result is None:
            return error.error_authorization_fail()
        if password != result['password']:
            return error.error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""
            token = jwt_encode(user_id, terminal)
            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id}, {'$set': {'token': token, 'terminal': terminal}})
            if result.modified_count == 0:  # 因为terminal时间戳不存在重复，所以执行成功必然返回1
                return error.error_authorization_fail() + ("",)
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id}, {'$set': {'token': dummy_token, 'terminal': terminal}})
            if result.modified_count == 0:
                return error.error_authorization_fail() + ("",)
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            user_col = self.conn['user']
            result = user_col.delete_one({'user_id': user_id})
            if result.deleted_count == 0:
                return error.error_authorization_fail()
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id},
                                         {'$set': {'password': new_password, 'token': token, 'terminal': terminal}})

            if result.modified_count == 0:
                return error.error_authorization_fail()
        except errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
