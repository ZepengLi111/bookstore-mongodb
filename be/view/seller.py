from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    token: str = request.headers.get("token")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id, token)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: int = request.json.get("stock_level", 0)
    token: str = request.headers.get("token")

    s = seller.Seller()
    code, message = s.add_book(
        user_id, store_id, book_info.get("id"), json.dumps(book_info), stock_level, token
    )

    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: int = request.json.get("add_stock_level", 0)
    token: str = request.headers.get("token")

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num, token)

    return jsonify({"message": message}), code

@bp_seller.route("/send", methods=["POST"])
def send():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    token: str = request.headers.get("token")
    store_id: str = request.json.get("store_id")

    s = seller.Seller()
    code, message = s.send(user_id, order_id, store_id, token)

    return jsonify({"message": message}), code