import pytest
from fe.access.buyer import Buyer
from fe.access.new_buyer import register_new_buyer
import uuid
from fe.data.utils import gen_random_keyword
import random

class TestSearchGlobal:
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_payment_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        

    def test_page_0(self):
        keyword = gen_random_keyword()  # 生成4-9长度不等的中文短句
        page = 0
        status= self.buyer.search_global(keyword, page)
        assert status == 200

    def test_page_not_0(self):
        keyword = gen_random_keyword()  # 生成4-9长度不等的中文短句
        page = random.randint(2,6)
        status = self.buyer.search_global(keyword, page)
        assert status == 200
    
    def test_page_none(self):
        keyword = gen_random_keyword()  # 生成4-9长度不等的中文短句
        page = None
        status = self.buyer.search_global(keyword, page)
        assert status == 200

    def test_invalidparam(self):
        keyword = gen_random_keyword()  # 生成4-9长度不等的中文短句
        page = -2
        status = self.buyer.search_global(keyword, page)
        assert status == 522