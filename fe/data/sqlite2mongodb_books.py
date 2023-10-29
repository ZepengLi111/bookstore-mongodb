import pymongo
import sqlite3 as sqlite
import os
import jieba



class sqlite2mongodb:
    def __init__(self, mongo_url: str="mongodb://localhost:27017/", ) -> None:
        """默认的mongodb服务器路径为mongodb://localhost:27017/，可以修改。"""
        self.client = pymongo.MongoClient(mongo_url)
        parent_path = os.path.dirname(__file__)
        self.db_s = os.path.join(parent_path, "book.db")
        self.db_l = os.path.join(parent_path, "book_lx.db")

    def get_book_info_cursor(self, db_path):
        """从book.db/book_lx.db中取出书籍数据"""
        conn = sqlite.connect(db_path)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            )
        return cursor
    
    def store(self, cursor):
        """将获取的数据数据存入mongodb"""
        book_db = self.client["book"]
        info_col = book_db["book_s_info"]
        # 获取所有的字段名
        names = [x[0] for x in cursor.description]

        """=======将标题，内容等分词并存入 _t 条目下============="""
        cols = ['title', 'author', 'tags', 'author_intro', 'book_intro', 'content']
        col_idx = [names.index(col) for col in cols]
        names.append('_t')
        stopwords = ['―','“','”','。','    ','.','\'','，','\n',']','[', '·','(', ')', '（', '）', '；', '...', '......']
        """============gyf==============="""

        for row in cursor:
            row = list(row)

            """============gyf==============="""
            _t_insert = []
            for idx in col_idx:
                text = row[idx]
                if text != None:
                    text_cutted = jieba.cut(text)  # jieba 
                    words = [word for word in text_cutted if word not in stopwords]
                    _t_insert.extend(words)
            row.append(' '.join(_t_insert))
            """============gyf==============="""

            # 对tags进行处理。原来的形式："标签1\n标签2\n标签3\n"，处理后：[标签1，标签2，标签3]
            row[15] = [tag for tag in row[15].split("\n") if tag != '']
            # 构造书籍json
            book = {names[i]: row[i] for i in range(len(names))}
            # 存入mongodb
            info_col.insert_one(book)
    
    def run(self, store_large=False):
        if store_large:
            curosr = self.get_book_info_cursor(self.db_l)
        else:
            curosr = self.get_book_info_cursor(self.db_s)
        if curosr:
            self.store(curosr)




if __name__ == "__main__":
    # 先将mongodb启动起来，再执行下面的语句
    # 执行前确保 book.db 或者 book_lx.db 在 data 目录下
    s = sqlite2mongodb()
    # 默认只将 book.db 存入，如果需要可以设置 store_large=True 以存入 book_lx.db
    # s.run(store_large=True)
    s.run()

