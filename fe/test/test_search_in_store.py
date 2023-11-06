import pytest
from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
import uuid
from fe.data.utils import gen_random_keyword
import random
from fe.access import book
from fe import conf

class TestSearchInStore:
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_payment_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.seller = register_new_seller(self.seller_id, self.password)
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))

        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 18)
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        

    def test_page_0(self):
        keyword = gen_random_keyword()  # 生成4-9长度不等的中文短句
        page = 0
        status = self.buyer.search_in_store(keyword, self.store_id, page)
        assert status == 200

    def test_page_not_0(self):
        keyword = gen_random_keyword()  # 生成长度不等的中文短句
        page = random.randint(2,6)
        status = self.buyer.search_in_store(keyword, self.store_id, page)
        assert status == 200
    
    def test_page_none(self):
        keyword = gen_random_keyword()  # 生成长度不等的中文短句
        page = None
        status = self.buyer.search_in_store(keyword, self.store_id, page)
        assert status == 200

    def test_invalidparam(self):
        keyword = gen_random_keyword()  # 生成长度不等的中文短句
        page = -2
        status = self.buyer.search_in_store(keyword, self.store_id, page)
        assert status == 522
    
    def test_error_store_id_exist(self):
        keyword = gen_random_keyword()  # 生成长度不等的中文短句
        page = 0
        status = self.buyer.search_in_store(keyword, store_id= "fake_store_id", page=page)
        assert status == 513
