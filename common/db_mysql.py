#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：db_mysql.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/25 
"""
import pymysql
from config import settings
from common import log

host = settings.database['host']
port = settings.database['port']
user = settings.database['user']
password = settings.database['password']
logger = log.Logger()


class DB_sql:
    def __init__(self):
        """连接"""
        self.db = pymysql.connect(host=host,
                                  port=port,
                                  user=user,
                                  password=password)
        # 使用cursors 游标以字典的形式读取
        self.cur = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        """ 关闭数据库 """
        self.cur.close()
        self.db.close()

    def select_db(self, sql, single=True):
        """查询"""
        self.db.ping(reconnect=True)
        # 使用 execute() 执行sql
        self.cur.execute(sql)
        # 使用 fetchall() 获取查询结果
        if single:
            data = self.cur.fetchone()
            return data
        else:
            data = self.cur.fetchall()
            return data

    def execute_db(self, sql):
        """更新、删除等操作"""
        try:
            self.db.ping(reconnect=True)
            self.cur.execute(sql)
            self.db.commit()
        except Exception as e:
            logger.error(U"操作MySQL出现错误，错误原因：{}".format(e))
            self.db.rollback()
