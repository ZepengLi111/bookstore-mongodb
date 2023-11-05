import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid
from fe import conf

class TestSend:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    confuse_seller_id: str
    buyer: Buyer
    seller: Seller
    confuse_seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_send_seller_id_{}".format(str(uuid.uuid1()))
        self.confuse_seller_id = "test_send_confuse_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_send_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_send_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        # code, self.confuse_order_id = b.new_order(self.store_id, buy_book_id_list)
        # assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        self.seller = Seller(conf.URL, self.seller_id, self.seller_id)
        self.confuse_seller = register_new_seller(self.confuse_seller_id, self.confuse_seller_id)
        yield

    def test_ok(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.send(self.order_id, self.store_id)
        assert code == 200

    def test_authorization_error(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.seller.seller_id = self.seller.seller_id + "_x"
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    def test_non_exist_order_id(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.order_id = self.order_id + "_x"
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    def test_non_exist_store_id(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.store_id = self.store_id + "_x"
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    def test_store_order_not_match_id(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        self.order_id = self.order_id + "_x"
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    def test_error_order_state(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    def test_error_store_wonership(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.confuse_seller.send(self.order_id, self.store_id)
        assert code != 200
