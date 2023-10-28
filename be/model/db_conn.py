from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        user_col = self.conn['user']
        result = user_col.find_one({'user_id': user_id})
        if result is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        book_col = self.conn['book']
        result = book_col.find_one({'belong_store_id': store_id, 'book_id':book_id})
        if result is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        store_col = self.conn['store']
        result = store_col.find_one({'store_id': store_id})
        if result is None:
            return False
        else:
            return True
