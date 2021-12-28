#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：db_mysql.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/25 
"""
import pymysql
from dbutils.pooled_db import PooledDB

from config.config import settings
from common import log

host = settings.database['host']
port = settings.database['port']
user = settings.database['user']
password = settings.database['password']
logger = log.Logger()


class DB_sql:
    def __init__(self):
        """连接"""
        self.db = PooledDB(creator=pymysql, mincached=1, maxcached=10,maxconnections=10,
                           host=host,
                           port=port,
                           user=user,
                           password=password, charset="utf8").connection()
        # 使用cursors 游标以字典的形式读取
        self.cur = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        """ 关闭数据库 """
        self.cur.close()
        self.db.close()

    def select_db(self, single=True, **kwargs):
        """
        查询语句
        :param single: 单条：True 多条：False
        :param kwargs: 查询字段
        :return: 数据
        """
        try:
            self.db.ping(reconnect=True)
            if 'sql' in kwargs:
                self.cur.execute(kwargs['sql'])
            else:
                # 列
                column = 'column' in kwargs and kwargs['column'] or '*'
                # 表
                table = 'table' in kwargs and kwargs['table']
                # 连接
                join = 'join' in kwargs and kwargs['join'] or ''
                # 条件
                where = 'where' in kwargs and 'where ' + kwargs['where'] or ''
                # 其他 如排序 输出限制
                other = 'other' in kwargs and kwargs['other'] or ''
                sql = f'select {column} from {table} {join} {where} {other}'
                # 使用 execute() 执行sql
                self.cur.execute(sql)
            if single:
                data = self.cur.fetchone()
                return data
            else:
                data = self.cur.fetchall()
                return data
        except Exception as e:
            logger.error("操作MySQL出现错误，错误原因：{}".format(e), 5)

    def execute_db(self, sql):
        """更新、删除等操作"""
        try:
            self.db.ping(reconnect=True)
            self.cur.execute(sql)
            self.db.commit()
        except Exception as e:
            logger.error(U'操作MySQL出现错误，错误原因：{}'.format(e), 5)
            self.db.rollback()
