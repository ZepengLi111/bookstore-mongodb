| **课程名称：当代数据管理系统** | **项目名称：bookstore** |
| --- | --- |
| **姓名：高宇菲** | **学号：10215501422** |
| **姓名：李泽朋** | **学号：10215501417** |
| **姓名：徐骏** | **学号：10205304463** |

<a name="svgEd"></a>
# 一，实验要求
实现一个提供网上购书功能的网站后端。<br />网站支持书商在上面开商店，购买者可以通过网站购买。<br />买家和卖家都可以注册自己的账号。<br />一个卖家可以开一个或多个网上商店，<br />买家可以为自已的账户充值，在任意商店购买图书。<br />支持 下单->付款->发货->收货 流程。<br />1.实现对应接口的功能，见项目的 doc 文件夹下面的 .md 文件描述 （60%）<br />其中包括：<br />1)用户权限接口，如注册、登录、登出、注销<br />2)买家用户接口，如充值、下单、付款<br />3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br />通过对应的功能测试，所有 test case 都 pass<br />2.为项目添加其它功能 ：（40%）<br />1)实现后续的流程<br />	发货 -> 收货<br />2)搜索图书<br />	用户可以通过关键字搜索，参数化的搜索方式；<br />	如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。<br />	如果显示结果较大，需要分页<br />	(使用全文索引优化查找)<br />3)订单状态，订单查询和取消定单<br />	用户可以查自已的历史订单，用户也可以取消订单。<br />	取消定单可由买家主动地取消定单，或者买家下单后，经过一段时间超时仍未付款，定单也会自动取消。
<a name="lO0At"></a>
# 二，项目运行

1. 启动MongoDB，并在be数据库下建立book, user, order, store文档集
2. 确保fe/data下有book.db
3. 运行以下命令
```powershell
python app.py
```
<a name="JSv4s"></a>
# 三，数据库设计
<a name="po4KJ"></a>
## 3.1 概念设计
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1697977048969-639c0f11-f734-425a-a76c-4d4e4ed9be86.png#averageHue=%23fbfaf8&clientId=uab65b544-58f0-4&from=paste&height=511&id=u910e226d&originHeight=766&originWidth=941&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=110609&status=done&style=none&taskId=u2be2c219-6fbd-4a4a-b75b-35873855616&title=&width=627.3333333333334)
<a name="vp9Em"></a>
## 3.2 结构设计
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

- 商店和卖家的关系存在了商店中，便于用户付款。
- 买家和订单的关系存在了订单中，我们假设经常会通过订单查询买家，而不会通过买家查询订单。
- 假设用户搜索图书的操作是频繁的，所以store并没有嵌入其他集合。

冗余：

- 用于搜索的冗余条目将在后40%部分详细介绍。

索引：

- 用户文档集在用户ID建立索引， 订单文档集在订单ID建立索引，商店文档集在商店ID建立索引，书籍文档集在book_id和belong_store_id建立**复合索引**。用于搜索的全文索引将在后40%部分详细介绍。
<a name="O2wBq"></a>
# 四，功能实现
<a name="x0RI2"></a>
## 4.1 前60%
前60%主要是修改**数据库的读取方式**。在实现以下三个接口之前，要先修改`be/model/store.py` 和 `be/model/db_conn.py`。<br />在`be/model/store.py`中使用be数据库，并建立索引。
```python
def get_db_conn(self):  # 返回MongoDB连接
        # 选择数据库
        self.mydb = self.client["be"]
        try:
            # 单键索引
            self.mydb['user'].create_index("user_id")
            self.mydb['order'].create_index("order_id")
            self.mydb['store'].create_index("store_id")
            # 复合索引， book_id 正序， belong_store_id 倒序
            self.mydb['book'].create_index([("belong_store_id", pymongo.DESCENDING), ("book_id", pymongo.ASCENDING)])
            print('---------->索引命中！')
        except Exception as e:
            print('---------->已存在索引！')
        return self.mydb
```
`be/model/db_conn.py`中的`db_conn`类是所有用户的父类，负责实现所有用户、书籍、商店是否存在的检查。这三个接口使用较频繁，有了store.py中的索引，效率可以得到提升。
```python
def user_id_exist(self, user_id):
    user_col = self.conn['user']
    result = user_col.find_one({'user_id': user_id})
    # ... 

def book_id_exist(self, store_id, book_id):
    book_col = self.conn['book']
    result = book_col.find_one({'belong_store_id': store_id, 'book_id':book_id})
    # ...

def store_id_exist(self, store_id):
    store_col = self.conn['store']
    result = store_col.find_one({'store_id': store_id})
    # ... 
```
<a name="NhLuw"></a>
### 4.1.1 用户权限接口
用户权限接口共5个，分别是注册，注销，登录，登出，更改密码。这些功能的后端逻辑全部沿用demo中的逻辑，不同的是要改为与MongoDB 交互。即pymongo的CRUD: `col.update_one`,`col.fine_one`, `col.insert_one`,`col.delete_one`。<br />具体地，做了如下修改：
```python
	def register(self, user_id: str, password: str):
    	# ...
            try:
                # ...
                user_col = self.conn['user']
                user1 = {
                    "user_id": user_id,
                    "password": password,
                    "balance": 0,
                    "token": token,
                    "terminal": terminal,
                }
                user_col.insert_one(user1)
        # ...

    def check_token(self, user_id: str, token: str) -> (int, str):
        user_col = self.conn['user']
        result = user_col.find_one({'user_id': user_id})
        # ...

    def check_password(self, user_id: str, password: str) -> (int, str):
        user_col = self.conn['user']
        result = user_col.find_one({'user_id': user_id})
        # ...

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            # ...
            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id}, {'$set': {'token': token, 'terminal': terminal}})
            # ...

    def logout(self, user_id: str, token: str) -> bool:
        try:
            # ...
            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id}, {'$set': {'token': dummy_token, 'terminal': terminal}})
            # ...

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            # ...
            user_col = self.conn['user']
            result = user_col.delete_one({'user_id': user_id})
            # ...


    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            # ...
            user_col = self.conn['user']
            result = user_col.update_one({'user_id': user_id},
                                         {'$set': {'password': new_password, 'token': token, 'terminal': terminal}})
        # ...
```
<a name="D9i7u"></a>
### 4.1.2 买家用户接口
<a name="TktYC"></a>
#### 下单`new_order`接口
实现以下功能：

1. 首先需要保证`user_id`和`store_id`存在；
2. 通过`user_id`，`store_id`，和唯一标识符相连生成`uid`；
3. 在`book表`中查找商户中是否存在对应的书籍；
4. 若上述条件满足，那么就减少商店中的库存数量；
5. 在`order表`中插入以下信息, 其中设置1800秒内付款：
```python
new_order_data = {'order_id':uid,
                  'buyer_id':user_id,
                  'creat_time':creat_time, # create_time通过datetime得到
                  'payment_deadline':creat_time+1800,
                  'state':0,
                  'order_amount':order_amount,
                  'seller_store_id':store_id,
                  'purchased_book_id':book_id_list,
                  'purchase_quantity':book_count_list}
```
<a name="w1xKz"></a>
#### 支付`payment接口`
实现以下功能：

1. 查询在`order`表中，是否存在属于用户的订单，若存在那么就对`order_id`、`buyer_id`、`seller_store_id`进行比对；
2. 如果比对成功，再判断用户余额和代付价格之间大小；
3. 若付款成功那么就`order表`中删除对应的待支付订单信息；
4. 最后修改订单状态信息；
<a name="PgGIw"></a>
#### 充值接口`add_funds`
实现以下功能：

1. 判断用户是否存在，并对用户和密码进行比对；
2. 若密码正确，那么就在`user表`中更新用户余额；
<a name="ACfU1"></a>
### 4.1.3 卖家用户接口
<a name="cEqt5"></a>
#### 创建商店`create_store接口`
实现以下功能：

1. 检查`seller_id(即user_id)`是否存在，不存在返回错误，检查`store_id`是否存在，若存在返回错误；
2. 接下来将`{"store_id": store_id, "seller_id": user_id}`插入`store表`；
<a name="ab5bn"></a>
#### 商家图书`add_book接口`
实现以下功能：

1. 检查`user_id`、`store_id`以及`book_id`是否存在，若不存在就报错；
2. 将`store_id`、`book_id`和`书籍信息`插入到`book表`中；
<a name="FgIvX"></a>
#### 添加库存`add_stock_level接口`
实现以下功能：

1. 检查`user_id`和`book_id`是否存在，不存在报错；
2. 根据`store_id`、`book_id`和原有`store表`中，并根据新的库存数进行更新；
<a name="cMWzw"></a>
### 4.1.4 前60% 测试结果
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1699423790711-bbd9832b-45ed-44c8-b407-0bfce9ebff7e.png#averageHue=%23f3f2ee&clientId=u2e61caa5-d564-4&from=paste&height=17&id=u978af4b1&originHeight=26&originWidth=1204&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=5249&status=done&style=none&taskId=ue1c6238f-d9a1-4190-bf08-aff6974e4f7&title=&width=802.6666666666666)
```
=============================== 33 passed, 1 warning in 149.24s (0:02:29) ================================ 
2023-11-08 14:20:15,978 [Thread-2914 ] [INFO ]  127.0.0.1 - - [08/Nov/2023 14:20:15] "GET /shutdown HTTP/1.1" 200 -
frontend end test
No data to combine
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
be\__init__.py                        0      0      0      0   100%
be\model\buyer.py                   118     25     42     10    74%
be\model\db_conn.py                  23      0      6      0   100%
be\model\error.py                    33      8      0      0    76%
be\model\seller.py                   73     17     28      4    73%
be\model\store.py                    25      1      0      0    96%
be\model\user.py                    121     25     40      6    76%
be\server.py                         35      1      2      1    95%
be\view\__init__.py                   0      0      0      0   100%
be\view\auth.py                      43      0      0      0   100%
be\view\buyer.py                     36      0      2      0   100%
be\view\seller.py                    34      0      0      0   100%
fe\__init__.py                        0      0      0      0   100%
fe\access\__init__.py                 0      0      0      0   100%
fe\access\auth.py                    31      0      0      0   100%
fe\access\book.py                    70      1     12      2    96%
fe\access\buyer.py                   36      0      2      0   100%
fe\access\new_buyer.py                8      0      0      0   100%
fe\access\new_seller.py               8      0      0      0   100%
fe\access\seller.py                  31      0      0      0   100%
fe\bench\__init__.py                  0      0      0      0   100%
fe\bench\run.py                      13      0      6      0   100%
fe\bench\session.py                  47      0     12      1    98%
fe\bench\workload.py                125      1     22      2    98%
fe\conf.py                           11      0      0      0   100%
fe\conftest.py                       17      0      0      0   100%
fe\data\utils.py                     22      0     10      1    97%
fe\test\gen_book_data.py             48      1     16      1    97%
fe\test\test_add_book.py             36      0     10      0   100%
fe\test\test_add_funds.py            23      0      0      0   100%
fe\test\test_add_stock_level.py      39      0     10      0   100%
fe\test\test_bench.py                 6      2      0      0    67%
fe\test\test_create_store.py         20      0      0      0   100%
fe\test\test_login.py                28      0      0      0   100%
fe\test\test_new_order.py            40      0      0      0   100%
fe\test\test_password.py             33      0      0      0   100%
fe\test\test_payment.py              61      1      4      1    97%
fe\test\test_register.py             31      0      0      0   100%
-------------------------------------------------------------------
TOTAL                              1325     83    224     29    91%
```
<a name="IInxF"></a>
## 4.2 后40%
后40%接口文档在`doc/addtional_functions.md`中，在此不再占用篇幅。
<a name="Q88tJ"></a>
### 4.2.1 发货 -> 收货
考虑到后续订单状态查询和取消的需求，设定order文档集中的state取值为以下四种。

| **state** | 0 | 1 | 2 | 3 | 5 |
| --- | --- | --- | --- | --- | --- |
| **含义** | 下单未付款 | 已付款未发货 | 已发货未收货 | 已收货 | 已取消 |

所以当卖家发货以及买家收货时，只需要修改相应order条目的state即可。但是需要注意的是，订单状态的修改是**无法越级**的（无法从状态0跳转到状态2）。
<a name="u5xyf"></a>
#### 后端实现
在后端实现中，除了状态可能不对之外，还需要考虑到店铺与卖家不匹配的情况。为此，设置两个新的error。
```python
error_code = {
    # ...
    523: "order state error, order status {}",   
    524: "store not belongs the seller {}",
}
```
后端实现代码
```python
def send(self, user_id:str, order_id:str, store_id: str, token: str) -> (int, str):
    try:
    	# ...
        # 查询商店文档集
        result_store = self.store.find_one({"store_id": store_id})
        if result_store is None:
            return error.error_non_exist_store_id(store_id)
        elif result_store['seller_id'] != user_id:
            # 商店与卖家不匹配
            return error.error_store_ownership(user_id)
        result_order = self.order.find_one({"order_id": order_id})
        if result_order is None:
            # 订单不存在
            return error.error_non_exist_order_id(order_id)
        elif result_order['state'] != 1:
            # 订单未处于已付款状态，无法发货
            return error.error_order_state(result_order['state'])
        else:
            result = self.order.update_one({"order_id": order_id, "seller_store_id": store_id}, {"$set": {"state": 2}})
            return 200, "ok"
    # except ...
```
```python
def receive(self, user_id:str, order_id:str, token: str) -> (int, str):
    try:
        # ...
        result_order = self.order.find_one({"order_id": order_id})
        if result_order is None:
            return error.error_non_exist_order_id(order_id)
        elif result_order['state'] != 2:
            # 订单状态位未处于已发货，无法收货
            return error.error_order_state(result_order['state'])
        else:
            result = self.order.update_one({"order_id": order_id, "buyer_id": user_id}, {"$set": {"state": 3}})
    # except ...
```
<a name="zpM8C"></a>
#### 测试实现
状态不对这一error比较好测试，在未付款之前直接发货即可。而对于商店与卖家不匹配，我需要构造一个"confusal user"，必须是已经注册的用户，否则触发的就是Authentication error了。<br />由于发货和收货是付款的后续进程，所以测试代码可以看作是test_payment.py的后续，只是增加了一些其他步骤。
```python
class TestSend:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
    	# 注册confusal seller
        self.confuse_seller_id = "test_send_confuse_seller_id_{}".format(str(uuid.uuid1()))
        # ...

    # 测试状态不对，未付款直接发货
    def test_error_order_state(self):
        code = self.seller.send(self.order_id, self.store_id)
        assert code != 200

    # 使用confusal seller测试订单和商店不匹配
    def test_error_store_ownership(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.confuse_seller.send(self.order_id, self.store_id)
        assert code != 200
```
test_receive.py与test_send.py大同小异，在此不再赘述。
<a name="Zxu90"></a>
### 4.2.2 搜索图书
<a name="gBLQw"></a>
#### 需求分析
搜索功能可以通过正则表达式实现；然而考虑到数据量大，正则表达式匹配的效率是![](https://cdn.nlark.com/yuque/__latex/e65a67ac353abeeff44c359310d05c02.svg#card=math&code=O%28n%29&id=U0320)，搜索时间太长可能影响用户体验；而且如果用户关键词有多个，正则表达式书写就变得复杂， 不利于维护。所以考虑使用全文索引。
<a name="RkTY6"></a>
#### 分析MongoDB支持情况
经查阅资料和实际试验，MongoDB不支持中日韩文的全文索引，仅支持空格分词。所以不论何种语言，MongoDB都会按照空格分词，而这样的分词结果往往不是用户的搜索关键词。虽然MongoDB也支持模糊查询，但仍然不能满足中文查询需求。<br />MongoDB也会对查询关键词进行空格分词，而且有无标点符号并不影响查询结果，这为我们提供了便利。
<a name="CsaOv"></a>
#### 拟解决方案
使用结巴中文分词，对题目，标签，目录，内容进行分词后，使用空格分隔，另外存储到一个名为`_t`的条目**（这是一个冗余条目）**。在这个冗余条目上建立全文索引。这个过程在卖家添加书籍时完成。
<a name="XIYZ5"></a>
#### 过程：
<a name="XEVIT"></a>
#### jieba分词
在`fe/data/utils.py`中实现`cut_word`函数和`gen__t`函数，并在`be/model/sell.py`中调用，这样卖家增加的每一本书籍都多了一个`_t`键。
```python
'''        
输入：一本书籍信息
输出：title, author 等内容的分词结果，并用空格分开
'''
def gen__t(book_dict):
    _t_insert = []
    attrs = ['title', 'author', 'tags', 'author_intro', 'book_intro', 'content']
    for attr in attrs:
        text = book_dict[attr]
        if text != None:
            _t_insert.extend(cut_word(text))
    return ' '.join(_t_insert)
```
<a name="ZiaCL"></a>
#### 添加冗余属性
即添加`_t`键，里面是标题、作者、目录、书籍和作者介绍等所以内容的分词结果。
```python
from fe.data.utils import gen__t
def add_book():
        try:
            # ...
            book_dict = json.loads(book_json_str)
            # ...
            book_dict['_t'] = gen__t(book_dict)
            self.book.insert_one(book_dict)
        # ...
```
效果如下：
<a name="n78Rt"></a>
#### ![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1699490410678-f9eaae06-22a1-4400-9738-1b947c9d6bcf.png#averageHue=%230c0c0c&clientId=ub812e396-faef-4&from=paste&height=564&id=u85ab67b3&originHeight=846&originWidth=1893&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=249064&status=done&style=none&taskId=udec09196-869a-4d1d-8059-0dfd6fec3ae&title=&width=1262)
<a name="zu8Mu"></a>
#### 添加全文索引
在`be/model/store.py`中添加全文索引：
```python
def get_db_conn(self):  # 返回MongoDB连接
        # 选择数据库
        self.mydb = self.client["be"]
        try:
            # 单键索引
            # ...
            # 复合索引， book_id 正序， belong_store_id 倒序
            # ...
            # 全文索引
            self.mydb['book'].create_index([("_t", pymongo.TEXT)])
```
<a name="E0Fv7"></a>
#### 实现搜索

- 对搜索实现两个接口，分别是`search_global`, `search_in_store`;
- `search_global` 接受两个参数，`keyword`和`page`(`page`可缺省) , `search_in_store`还要接受`store_id`;
- 首先，对用户输入的keyword分词并用空格分开，然后调用使用全文索引查询数据库：
```python
keywords = ' '.join(cut_word(keyword))
results = self.book.find({'$text':{'$search': keywords}}, {'_id':0, '_t':0})
```

- 店内搜索还要检查店铺是否存在：
```python
if not self.store_id_exist(store_id):
    return error.error_non_exist_store_id(store_id) + ([],)
keywords = ' '.join(cut_word(keyword))
results = self.book.find({'$text':{'$search': keywords}, 'belong_store_id':store_id}, {'_id':0, '_t':0})
```

- 如果page为None或page为0，表示不分页，输出全部查询结果。
- 如果page>0，表示用户请求第page页。我们在`DBConn`类中定义`page_size`属性为5，即固定一页5条数据。然后对find的结果使用skip和limit，实现分页功能：
```python
if page > 0:
    results = list(results.skip((page-1)*self.page_size).limit(self.page_size))
```

- 如果用户输入了小于0的page，将触发`error_invalid_parameter`。
<a name="qxl9q"></a>
#### 效果展示
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1699625047434-10f9f90f-553c-48f5-b42c-af92bb131bc0.png#averageHue=%23fcfcfb&clientId=ucda4898e-4acd-4&from=paste&height=522&id=ue1062027&originHeight=783&originWidth=1285&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=173982&status=done&style=none&taskId=u897fc094-6d7c-425e-ae2d-d7825669de1&title=&width=856.6666666666666)<br />![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1699625827138-a3a0d2c5-b0d9-4ce1-bd49-12cff60e83e2.png#averageHue=%23fcfcfb&clientId=ucda4898e-4acd-4&from=paste&height=507&id=uc856e653&originHeight=760&originWidth=1300&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=136419&status=done&style=none&taskId=u1407687d-08e4-4e10-9873-39e0b5986bb&title=&width=866.6666666666666)
<a name="WLj15"></a>
#### 测试
对page的大于0，等于0，小于0和为None的情况分别测试，以及对商店不存在的情况进行测试。
<a name="f0pM7"></a>
#### 性能分析
全局搜索访问数据库一次，店铺搜索访问数据库两次，都可以视为![](https://cdn.nlark.com/yuque/__latex/a2006f1ac61cb1902beacb3e29fff089.svg#card=math&code=O%281%29&id=RR5YJ)复杂度。
<a name="s9lkb"></a>
### 4.2.3 订单状态，订单查询和取消定单
<a name="qnp4r"></a>
#### 查询历史订单信息
根据`buyer_id`在`order表`中查询所有订单。如果查询成功，那么就返回订单的相关信息；然后根据订单信息划分为以下查询接口：

- `buyer_id`不存在情况
- 查询所有订单；
- 查询待支付订单；
- 查询已发货待发货订单；
- 查询已发货待收货订单；
- 查询取消订单；
<a name="ZalKf"></a>
#### 手动取消订单
实现顺序：

1. 根据`order_id`和`buyer_id`在`order表`中查询是否存在，并判断是否属于待支付订单（只允许在未发货和未付款的情况下才能取消订单）；
2. 如果符合那么就在`order`中删除对应订单；
3. 如果订单状态是`已支付代发货`，那么在删除后在`user表`中更新余额；
4. 最后在对`store表`对应书籍的库存进行更新

测试用例：

1. `buyer_id`不存在情况
2. 已付款未发货
3. 未付款情况
<a name="pdpDk"></a>
#### 自动取消订单
订单中有一个属性为`deadline`，即订单支付截止时间，如果当前时间超过了这个截止时间那么就自动取消；<br />有两种实现方法：

1. 在每次接口调用时都检查一次是否有超时的订单，如果有删除它；
2. 通过多线程的方式解决；

介绍多线程的解决方式：<br />创建文件`autocancel.py`：
```python
from be.model.buyer import Buyer
def delete_order_time():
    buyer = Buyer()
    while True:
        buyer.delete_order_time()
if __name__ == '__main__':
    delete_order_time()
```
实现自动取消订单的功能可以在`app.py`中单开一个进程运行自动取消订单的程序`autocancel.py`，然后在运行`app.run()`
```python
if __name__ == '__main__':
    p = multiprocessing.Process(target=subprocess.call, args=(["python", "auto_cancel.py"],))
    p.start()
    server.be_run()
```
<a name="Ww0kN"></a>
### 4.3 总体测试结果
![image.png](https://cdn.nlark.com/yuque/0/2023/png/34343420/1699629323271-774e7f16-3bdd-4cce-86ab-df74b988f466.png#averageHue=%23f3f2ee&clientId=ucda4898e-4acd-4&from=paste&height=19&id=u29ac6880&originHeight=28&originWidth=1236&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=5576&status=done&style=none&taskId=ue93d02a3-8a04-46c4-a7cb-cbd2ada22cc&title=&width=824)
```
================================== 59 passed, 1 warning in 399.05s (0:06:39) ================================== 
F:\Romio\ECNU period\课程\数据库\bookstore-mongodb\be\serve.py:18: UserWarning: The 'environ['werkzeug.server.shutdown']' function is deprecated and will be removed in Werkzeug 2.1.
  func()
2023-11-10 23:08:45,679 [Thread-4308 ] [INFO ]  127.0.0.1 - - [10/Nov/2023 23:08:45] "GET /shutdown HTTP/1.1" 200 -
frontend end test
No data to combine
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
be\__init__.py                        0      0      0      0   100%
be\model\buyer.py                   188     28     72      6    84%
be\model\db_conn.py                  23      0      6      0   100%
be\model\error.py                    33      4      0      0    88%
be\model\seller.py                   85     14     34      2    82%
be\model\store.py                    26      3      0      0    88%
be\model\user.py                    121     25     40      6    76%
be\serve.py                          35      1      2      1    95%
be\view\__init__.py                   0      0      0      0   100%
be\view\auth.py                      43      0      0      0   100%
be\view\buyer.py                     88      0      8      0   100%
be\view\seller.py                    43      0      0      0   100%
fe\__init__.py                        0      0      0      0   100%
fe\access\__init__.py                 0      0      0      0   100%
fe\access\auth.py                    31      0      0      0   100%
fe\access\book.py                    70      1     12      2    96%
fe\access\buyer.py                   66      0      2      0   100%
fe\access\new_buyer.py                8      0      0      0   100%
fe\access\new_seller.py               8      0      0      0   100%
fe\access\seller.py                  37      0      0      0   100%
fe\bench\__init__.py                  0      0      0      0   100%
fe\bench\run.py                      13      0      6      0   100%
fe\bench\session.py                  47      0     12      1    98%
fe\bench\workload.py                125      1     22      2    98%
fe\conf.py                           11      0      0      0   100%
fe\conftest.py                       17      0      0      0   100%
fe\data\utils.py                     22      0     10      1    97%
fe\test\gen_book_data.py             49      0     16      0   100%
fe\test\test_add_book.py             37      0     10      0   100%
fe\test\test_add_funds.py            23      0      0      0   100%
fe\test\test_add_stock_level.py      40      0     10      0   100%
fe\test\test_bench.py                 6      2      0      0    67%
fe\test\test_create_store.py         20      0      0      0   100%
fe\test\test_delete_order.py         41      0      2      0   100%
fe\test\test_login.py                28      0      0      0   100%
fe\test\test_new_order.py            40      0      0      0   100%
fe\test\test_password.py             33      0      0      0   100%
fe\test\test_payment.py              60      1      4      1    97%
fe\test\test_receive.py              77      1      4      1    98%
fe\test\test_register.py             31      0      0      0   100%
fe\test\test_search_global.py        35      0      0      0   100%
fe\test\test_search_in_store.py      53      0      2      0   100%
fe\test\test_search_order.py         71      0      4      0   100%
fe\test\test_send.py                 97      1      4      1    98%
-------------------------------------------------------------------
TOTAL                              1881     82    282     24    94%
```
<a name="ImhSj"></a>
# 五，分工
**高宇菲：**概念设计，结构设计，用户权限接口，测试前60%，搜索功能及测试<br />**李泽朋：**概念设计，结构设计，发货和收货及测试，将book.db存入mongodb<br />**徐骏：**概念设计，结构设计，买家卖家接口，订单查询和取消订单及测试
<a name="PDOar"></a>
# 六，亮点展示
<a name="LdMmU"></a>
### 索引设计
出于对提高用户体验的考虑，我们设计如下索引：

- 单键索引：

在`user`、`order`、`store`文档集中分别对`user_id`、`order_id`、`store_id`建立索引

- 复合索引：

由于在搜索图书的接口（添加库存，更新书籍信息，下单）全部是通过商店id配合进行搜索，所以在`book`文档集中建立复合索引`(belong_store_id, book_id)`。这个索引对于通过商店 id 搜索店内书籍的接口（当前店铺通过关键字搜索书籍）也会有帮助。

- 全文索引：

在`book`文档集中对分词结果 `_t` 建立全文索引，加快搜索速度
<a name="i14uE"></a>
### 版本管理
github仓库：[https://github.com/ZepengLi111/bookstore-mongodb](https://github.com/ZepengLi111/bookstore-mongodb)<br />本项目使用Github进行代码托管和版本控制。下面是在开发过程中我们一小段我们的项目迭代过程。![image.png](https://cdn.nlark.com/yuque/0/2023/png/40512603/1699622832210-d8583ceb-8f98-4986-9981-76a3437f8720.png#averageHue=%231f2838&clientId=u179df3a4-f62a-4&from=paste&height=419&id=u14e9b334&originHeight=628&originWidth=1198&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=160532&status=done&style=none&taskId=uf80e794d-1a33-4468-ab87-1dcec16b084&title=&width=798.6666666666666)<br />在git的帮助下，我们组员内可以轻易的分工协作，使用不同的分支进行模块更新和bug修复。
<a name="zCe1w"></a>
### 测试驱动开发
在本项目中，我们尝试使用测试驱动开发（Test-Driven Development，TDD）进行项目的迭代开发，具体流程如下。<br />![](https://cdn.nlark.com/yuque/0/2023/jpeg/40512603/1699624262240-ad3b2d0d-a1a7-47e4-a420-96487c38bc32.jpeg)<br />在前60%中，我们根据项目的已有的单元测试进行开发。在后40%中，我们首先讨论功能需求，编写单元测试用例，然后根据测试用例进行新功能的开发。
<a name="YjlYW"></a>
#### TDD的优势：

1. 更高的软件质量：我们在编写代码之前编写测试用例，有助于捕获和修复潜在的问题和缺陷，编写更稳健更可靠的软件代码。
2. 更好的文档和示例：我们在编写代码之前，首先通过需求编写后端接口文档，然后根据文档编写测试用例。该单元测试描述了每个功能的预期行为，有助于我们组员之间快速理解代码和功能。
3. 增量开发：TDD通过小步骤进行迭代开发，逐渐构建功能，避免了开发后期修复大量问题的发生。
<a name="UP5XK"></a>
# 七，总结
本次实验专注于后端开发和测试，让我们对数据库设计时的**索引设计、冗余设计、嵌入设计**有了更深入的理解，也积累了一定实践经验，为今后学习打下基础。实验中遇到的困难大多予以解决。最后，我们的程序通过了59个测试，覆盖率达 **94%**（不考虑except出现的严重数据库错误，覆盖率达到了 **97% **），取得了较为满意的结果。
