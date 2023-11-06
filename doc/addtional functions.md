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



