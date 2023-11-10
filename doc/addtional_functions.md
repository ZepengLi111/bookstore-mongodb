# 后40%内容的接口文档

## 1. 实现后续流程

## 发货

#### URL:

POST http://[address]/seller/send

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:

```json
{
    "user_id": "seller_id",
    "order_id": "order_id",
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 卖家用户ID | N
order_id | string | 订单ID | N 

#### Response

Status Code:

码 | 描述
--- | ---
200 | 发货成功 
5XX | 卖家用户ID不存在 
5XX | 订单ID不存在 
5XX | 订单状态错误 

Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N

## 收货

#### URL:

POST http://[address]/buyer/receive

#### Request

##### Header:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

##### Body:

```json
{
    "user_id": "buyer_id",
    "order_id": "order_id",
}
```

##### 属性说明：

| 变量名   | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户ID | N          |
| order_id | string | 订单ID     | N          |

#### Response

Status Code:

| 码   | 描述             |
| ---- | ---------------- |
| 200  | 收货成功         |
| 5XX  | 买家用户ID不存在 |
| 5XX  | 订单ID不存在     |
| 5XX  | 订单状态错误     |

Body:
```
{
    "message":"$error message$"
}
```
变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
message | string | 返回错误消息，成功时为"ok" | N

## 全局搜索

#### URL：
POST http://[address]/buyer/search_global

#### Request

##### Body:
```json
{
  "keyword": "keyword",
  "page": "page",
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
keyword | string | 搜索关键词 | N
page | int | 页数，0代表不分页，默认为0 | Y


Status Code:

码 | 描述
--- | ---
200 | 搜索成功
401 | 搜索失败
522 | 无效参数


## 店铺搜索

#### URL：
POST http://[address]/buyer/search_in_store

#### Request

##### Body:
```json
{
  "keyword": "keyword",
  "page": "page",
  "store_id": "store_id"
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
keyword | string | 搜索关键词 | N
page | int | 页数，0代表不分页，默认为0 | Y
store_id | string | 商铺ID | N


Status Code:

码 | 描述
--- | ---
200 | 搜索成功
401 | 搜索失败
522 | 无效参数
513 | 店铺不存在

## 订单状态

### 订单查询

#### URL

查询订单：
POST http://[address]/buyer/search_order

#### Request

##### Body:
```json
{
  "user_id": "user_id",
  "search_state": "search_state",
}
```

##### 属性说明：

key | 类型 | 描述       | 是否可为空
---|---|----------|---
user_id | string | 查询用户历史订单 | N
search_state | string | 查询状态 | N

search_state有以下几种状态：
- 0：查询全部订单
- 1：查询待付款订单
- 2：查询已付款代发货订单
- 3：查询已发货待收货订单
- 4：查询成功结束订单
- 5：查询已取消订单



Status Code:

码 | 描述
--- | ---
200 | 查询成功
401 | 查询失败
522 | 无效参数
513 | user_id不存在



## 订单删除

#### URL
POST http://[address]/buyer/delete_order


#### Request

##### Body:
```json
{
  "user_id": "user_id",
  "order_id": "order_id"
}
```

##### 属性说明：

key | 类型 | 描述        | 是否可为空
---|---|-----------|---
user_id | string | 用户id      | N
order_id | string | 想要删除的订单id | N



Status Code:

码 | 描述
--- | ---
200 | 删除成功
401 | 删除失败
522 | 无效参数
513 | user_id不存在