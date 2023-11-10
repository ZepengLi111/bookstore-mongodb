import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: int) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    def receive(self, order_id: str) -> int:
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "receive")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_global(self, keyword: str, page: int = None) -> int:
        json = {"keyword": keyword, "page": page}
        url = urljoin(self.url_prefix, "search_global")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_in_store(self, keyword: str, store_id: str, page: int = None) -> int:
        json = {"keyword": keyword, "page": page, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_in_store")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_order(self, buyer_id: str, state) -> int:
        json = {
            "buyer_id": buyer_id,
            "search_state": state
        }
        url = urljoin(self.url_prefix, "search_order")
        if state == 0:
            url = urljoin(self.url_prefix, "search_order")
        elif state == 1:  # 查询待付款订单
            url = urljoin(self.url_prefix, "search_unpaid_order")
        elif state == 2:  # 查询已付款待发货订单
            url = urljoin(self.url_prefix, "search_undelivered_order")
        elif state == 3:  # 查询已发货待收货订单
            url = urljoin(self.url_prefix, "search_unreceive_order")
        elif state == 4:  # 查询已收货订单
            url = urljoin(self.url_prefix, "search_ok_order")
        elif state == 5:  # 查询已取消订单
            url = urljoin(self.url_prefix, "search_canceled_order")

        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def delete_order(self, buyer_id: str, order_id: str) -> int:
        json = {"buyer_id": buyer_id, "order_id": order_id}
        url = urljoin(self.url_prefix, "delete_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
