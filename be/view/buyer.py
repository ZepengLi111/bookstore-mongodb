from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer
import json

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    token: str = request.headers.get("token")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))
    b = Buyer()
    b.delete_order_time()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count, token)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    b.delete_order_time()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    b.delete_order_time()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


@bp_buyer.route("/receive", methods=["POST"])
def send():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    token: str = request.headers.get("token")
    b = Buyer()
    b.delete_order_time()
    code, message = b.receive(user_id, order_id, token)
    return jsonify({"message": message}), code


@bp_buyer.route("/search_global", methods=["POST"])
def search_global():
    keyword: str = request.json.get("keyword")
    page: int = request.json.get("page")
    if page == None:
        page = 0
    b = Buyer()
    b.delete_order_time()
    code, message, results = b.search_global(keyword, page)
    res_dict = json.dumps(results, ensure_ascii=False)
    return jsonify({"message": message, "results": res_dict}), code


@bp_buyer.route("/search_in_store", methods=["POST"])
def search_in_store():
    keyword: str = request.json.get("keyword")
    page: int = request.json.get("page")
    store_id: int = request.json.get("store_id")
    if page == None:
        page = 0
    b = Buyer()
    b.delete_order_time()
    code, message, results = b.search_in_store(keyword, page, store_id)
    res_dict = json.dumps(results, ensure_ascii=False)
    return jsonify({"message": message, "results": res_dict}), code


'''
@ search_all_order()
查询所有订单，根据user_id在order表中查询

order表的属性：
'order_id'：订单id 
'buyer_id'：用户购买id 
'creat_time'： 订单创建时间 
'payment_deadline'：支付截止时间
'state'：订单状态信息 
'order_amount'：购买书本总量
'seller_store_id'：商家id
'purchased_book_id'：购买书本id[]
'purchase_quantity'：购买数量[]

search_state:
0 查询所有订单
1 查询待付款订单
2 查询已付款待发货订单
3 查询已发货待收货订单
4 查询已取消订单
'''

@bp_buyer.route("/search_order", methods=["POST"])
def search_order():
    user_id: str = request.json.get("buyer_id")
    search_state: int = request.json.get("search_state")
    b = Buyer()
    b.delete_order_time()
    code, message, results = b.search_order(user_id, search_state)
    results = [str(result) for result in results]
    res_dict = json.dumps(results, ensure_ascii=False)
    return jsonify({"message": message, "results": res_dict}), code


@bp_buyer.route("/delete_order", methods=["POST"])
def delete_order():
    user_id: str = request.json.get("buyer_id")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.delete_order(user_id, order_id)
    return jsonify({"message": message}), code
