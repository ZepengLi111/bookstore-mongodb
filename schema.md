# 概念设计
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1697977048969-639c0f11-f734-425a-a76c-4d4e4ed9be86.png#averageHue=%23fbfaf8&clientId=uab65b544-58f0-4&from=paste&height=511&id=u910e226d&originHeight=766&originWidth=941&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=110609&status=done&style=none&taskId=u2be2c219-6fbd-4a4a-b75b-35873855616&title=&width=627.3333333333334)
# 结构设计
共4个文档集，订单，书籍，商店，用户，里面存储上图中的属性。除此以外，还存储它们之间的关系：
```json
user: {
  user_id,
  user_name,
  balance,
  password,
  token,
  terminal,
}

order: {
	order_id,
  seller_id,
  creat_time,
  payment_deadline,
  state,
  order_amount,
  seller_store_id,
  purchased_book_id,
  purchase_quantity,
}

store: {
  store_id,
  seller_id,
}

book: {
  book_id,
  belong_store_id,
  title,
  author,
  ...,
  price,
  quantity,
} 
```
嵌入：商店信息没有嵌入到用户文档集，因为书籍信息体积很大且经常被修改，更适合独立出来。商店和卖家的关系存在了商店中，便于用户付款。买家和订单的关系存在了订单中，因为经常会通过订单查询订买家，而不会通过订单查询买家。
冗余：暂无冗余设计。
索引：用户文档集在用户ID建立索引， 订单文档集在订单ID建立索引，商店文档集在商店ID建立索引，在书籍ID建立索引。

Note:
state取值为0（已下单），1（已付款），2（已发货），3（已收货）
