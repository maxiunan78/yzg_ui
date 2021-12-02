import logging
import time
from datetime import datetime

import pymysql


class DB_sql:
    def __init__(self, host, port, user, password):
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
            return dict(data)
        else:
            data = self.cur.fetchall()
            return list(data)

    def execute_db(self, sql):
        """更新、删除等操作"""
        try:
            self.db.ping(reconnect=True)
            self.cur.execute(sql)
            self.db.commit()
        except Exception as e:
            # 应该封装logger,暂时print
            print("操作MySQL出现错误，错误原因：{}".format(e))
            self.db.rollback()

    def get_sql_value(self, result, name):
        """
        获取sql某一项值
        :param result: sql查询的结果
        :param name: 字段名
        :return: str类型的值
        """
        if type(result) == dict:
            return str(result[name])
        else:
            result_list = []
            for i in result:
                result_list.append(str(i[name]))
            return result_list


db = DB_sql(host="47.97.35.19",
            port=3306,
            user="root",
            password="rain1q2w3e4r5t")

