

## bookstore目录结构

```
bookstore
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 sqlite 数据库(book.db，较少量的测试数据)
            |-- book_lx.db              sqlite 数据库(book_lx.db， 较大量的测试数据，要从网盘下载)
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```

## 安装配置

安装 python (需要 python3.6 以上)

进入 bookstore 文件夹下：

安装依赖

`pip install -r requirements.txt`
执行测试

`bash script/test.sh`
> （注意：如果提示"RuntimeError: Not running with the Werkzeug Server"，请输入下述命令，将 flask 和 Werkzeug 的版本均降低为2.0.0。）

` pip install flask==2.0.0  `

` pip install Werkzeug==2.0.0`

## 要求

1.bookstore 文件夹是该项目的 demo，采用 Flask 后端框架与 SQLite 数据库，实现了前60%功能以及对应的测试用例代码。
要求大家创建本地 MongoDB 数据库，将bookstore/fe/data/book.db中的内容以合适的形式存入本地数据库，后续所有数据读写都在本地的 MongoDB 数据库中进行

书本的内容可自行构造一批，也可参从网盘下载，下载地址为：

https://pan.baidu.com/s/1bjCOW8Z5N_ClcqU54Pdt8g
提取码：

hj6q
2.在完成前60%功能的基础上，继续实现后40%功能，要有接口、后端逻辑实现、数据库操作、代码测试。对所有接口都要写 test case，通过测试并计算测试覆盖率（尽量提高测试覆盖率）。

3.尽量使用索引，对程序与数据库执行的性能有考量