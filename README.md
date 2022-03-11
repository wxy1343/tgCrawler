# tgCrawler
电报爬虫
## 1.安装
* `git clone https://github.com/wxy1343/tgCrawler`
* pip install -r requirements.txt
## 2.修改配置
```python3
api_id = 0
api_hash = ''  # 获取api_id和api_hash：https://my.telegram.org/apps
bot_token = ''  # 机器人token，找@BotFather创建，使用手机登录可不填
entity = '' # 要爬取群组的url
phone = ''  # 手机需要+区号
tg_password = ''  # 密码
proxy = (socks.SOCKS5, 'localhost', 2333)  # 代理
host = 'localhost'  # 数据库地址
port = 3306  # 数据库端口
user = ''  # 数据库账号
password = ''  # 数据库密码
db = ''  # 数据库名称
connect_timeout = 10  # 连接数据库超时时间
charset = 'utf8mb4'  # 数据库编码
```
## 3.运行
* `python telegram_group_crawler.py`
