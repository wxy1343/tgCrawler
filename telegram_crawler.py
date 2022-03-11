#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/10 18:16
# @Author  : wxy1343
# @File    : telegram_group_crawler.py

import asyncio

import aiomysql.sa as aio_sa
import socks
import telethon
from aiomysql.sa import SAConnection
from aiomysql.sa.result import ResultProxy
from telethon import TelegramClient
from telethon.tl.patched import MessageService
from telethon.tl.types import User


async def init_db(*args, **kwargs):
    engine = await aio_sa.create_engine(*args, **kwargs)
    data = await (await execute(engine, "SELECT VERSION()")).fetchone()
    print("Database version : %s " % data[0])
    return engine


async def execute(engine, sql, *args, **kwargs):
    async with engine.acquire() as conn:
        conn: SAConnection
        result: ResultProxy = await conn.execute(sql, args, **kwargs)
        return result


async def main(engine, entity, phone=None, password=None, bot_token=None, proxy=None):
    """

    :param engine: 数据库对象
    :param entity: 要爬取的对象，可以是url
    :param phone: 手机号
    :param password: 密码
    :param bot_token: 机器人token
    :param proxy: 代理
    :return:
    """
    client: telethon.client.telegramclient.TelegramClient = await TelegramClient('bot', api_id, api_hash,
                                                                                 proxy=proxy).start(phone=lambda: phone,
                                                                                                    password=lambda: password,
                                                                                                    bot_token=bot_token)

    async def start():
        sql_create = """CREATE TABLE IF NOT EXISTS %s (
                         `mid`  INT(10) NOT NULL,
                         `sid`  INT(10),
                         `time` DATETIME,
                         `text` TEXT(1024),
                         PRIMARY KEY ( `mid` )
                         )DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin"""
        me = await client.get_me()
        print(me.username)
        e = await client.get_entity(entity)
        try:
            print(e.title)
        except AttributeError:
            pass
        sql_create %= e.username
        await execute(engine, sql_create)
        sql_insert = 'INSERT INTO {} ( mid, sid, time, text ) VALUES ( %s, %s, %s, %s );'.format(e.username)
        sql_get_msg_id = 'select mid from {} order by mid desc limit 1;'.format(e.username)
        data = await (await execute(engine, sql_get_msg_id)).fetchone()
        msg_id = data[0] if data else 0
        async for msg in client.iter_messages(e, reverse=True, offset_id=msg_id):
            msg: MessageService
            if msg.message is not None:
                text = str(msg.id) + '|' + str(msg.date) + '|'
                sid = None
                if msg.sender is not None:
                    sender = msg.sender
                    if isinstance(msg.sender, User):
                        sender: User
                        first_name = sender.first_name
                        last_name = sender.last_name
                        name = first_name + last_name if first_name and last_name else first_name if first_name else last_name
                        text += name + ':' if name else ''
                        sid = sender.id
                text += msg.raw_text
                mid = msg.id
                dt = msg.date.strftime("%Y-%m-%d %H:%M:%S")
                print(text)
                await execute(engine, sql_insert, mid, sid, dt, msg.raw_text)
                # with open(f'{e.username}.txt', 'a', encoding='utf-8') as f:
                #     f.write(text + '\n')

    await start()
    await client.disconnect()


api_id = 0
api_hash = ''  # 获取api_id和api_hash：https://my.telegram.org/apps
bot_token = ''  # 机器人token，找@BotFather创建，使用手机登录可不填
entity = 'https://t.me/aliyundriveShare'
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

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    get_future = asyncio.ensure_future(
        init_db(host=host, port=port, user=user, password=password, db=db, connect_timeout=connect_timeout,
                charset=charset))
    loop.run_until_complete(get_future)
    engine = get_future.result()
    loop.run_until_complete(main(engine, entity, phone, password, bot_token, proxy))
