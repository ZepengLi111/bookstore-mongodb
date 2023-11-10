| 课程名称：当代数据管理系统 | 项目名称：bookstore |
| --- | --- |
| **姓名：高宇菲** | **学号：10215501422** |
| **姓名：李泽朋** | **学号：** |
| **姓名：徐骏** | **学号：** |

<a name="svgEd"></a>
# 一，实验要求
实现一个提供网上购书功能的网站后端。<br />网站支持书商在上面开商店，购买者可以通过网站购买。<br />买家和卖家都可以注册自己的账号。<br />一个卖家可以开一个或多个网上商店，<br />买家可以为自已的账户充值，在任意商店购买图书。<br />支持 下单->付款->发货->收货 流程。<br />1.实现对应接口的功能，见项目的 doc 文件夹下面的 .md 文件描述 （60%）<br />其中包括：<br />1)用户权限接口，如注册、登录、登出、注销<br />2)买家用户接口，如充值、下单、付款<br />3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br />通过对应的功能测试，所有 test case 都 pass<br />2.为项目添加其它功能 ：（40%）<br />1)实现后续的流程<br />发货 -> 收货<br />2)搜索图书<br />用户可以通过关键字搜索，参数化的搜索方式；<br />如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。<br />如果显示结果较大，需要分页<br />(使用全文索引优化查找)<br />3)订单状态，订单查询和取消定单<br />用户可以查自已的历史订单，用户也可以取消订单。<br />取消定单可由买家主动地取消定单，或者买家下单后，经过一段时间超时仍未付款，定单也会自动取消。
<a name="lO0At"></a>
# 二，项目运行

1. 启动MongoDB，并在be数据库下建立book, user, order, store文档集
2. 运行以下命令
```powershell
python app.py
```
<a name="JSv4s"></a>
# 三，数据库设计
<a name="po4KJ"></a>
## 概念设计
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1697977048969-639c0f11-f734-425a-a76c-4d4e4ed9be86.png#averageHue=%23fbfaf8&clientId=uab65b544-58f0-4&from=paste&height=511&id=u910e226d&originHeight=766&originWidth=941&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=110609&status=done&style=none&taskId=u2be2c219-6fbd-4a4a-b75b-35873855616&title=&width=627.3333333333334)
<a name="vp9Em"></a>
## 结构设计
共4个文档集，订单，书籍，商店，用户，里面存储上图中的属性。除此以外，还存储它们之间的关系：
```
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
  buyer_id,
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
  books:{
    book_id,
    price,
    quantity
  }
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
嵌入：

- 商店信息中嵌入了**必要的**书籍信息：book_id, price, quantity，提高查询效率。
- 商店信息没有嵌入到用户文档集，因为书籍信息体积很大且经常被修改，更适合独立出来。
- 商店和卖家的关系存在了商店中，便于用户付款。
- 买家和订单的关系存在了订单中，我们假设经常会通过订单查询买家，而不会通过买家查询订单。

冗余：

- 书籍中存有所属商店信息，商店中存有所有书籍的id, 价格，数量。

索引：

- 用户文档集在用户ID建立索引， 订单文档集在订单ID建立索引，商店文档集在商店ID建立索引，书籍文档集在书籍ID建立索引。用于搜索的全文索引将在后40%部分详细介绍。
<a name="O2wBq"></a>
# 四，功能实现
<a name="NhLuw"></a>
## 用户权限接口
<a name="D9i7u"></a>
## 买家用户接口
<a name="ACfU1"></a>
## 卖家用户接口
<a name="cMWzw"></a>
## 前60% 测试结果
<a name="Q88tJ"></a>
## 发货 -> 收货
<a name="Zxu90"></a>
## 搜索图书
<a name="s9lkb"></a>
## 订单状态，订单查询和取消定单
<a name="Ww0kN"></a>
## 总体测试结果
<a name="ImhSj"></a>
# 五，分工
**高宇菲：**<br />**李泽朋：**<br />**徐骏：**
<a name="PDOar"></a>
# 六，亮点展示

