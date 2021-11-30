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

start = time.time()
sql = "select table_name from data_dict.self_table_config  where FIND_IN_SET('16548',hq_ids)"
c = db.select_db(sql)
# print(c)
sql2 = "SELECT * FROM trade.2021_{} where ORDER_ID ='{}'".format(str(c['table_name']), 'SP1654810411637806351894')
# d = db.select_db(sql2)
# print(d)
# print(db.get_sql_value(d, 'UPDATED_TIME'))
#
#
sql3 = "select ID FROM  erp_hq.member_grade_config  WHERE erp_hq.member_grade_config.HQ_ID ='16548' and " \
       "erp_hq.member_grade_config.GRADE_TYPE != '0' "
# i = 0
# while i < 10:
#
#     ref_order_id = db.get_sql_value(db.select_db(sql2), 'MEMBER_CARD_NO')
#
#     if ref_order_id != "None":
#         break
#     else:
#         time.sleep(5)
#
#     i += 1
x = db.select_db(sql3, False)
print(x)
print(db.get_sql_value(x[0], 'ID'))
end = time.time()
print(end - start)
