#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：discount_rule.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/27 
"""
from common.db_mysql import DB_sql
from base.preconditions import Precondition

db = DB_sql()
precondition = Precondition()


class Discount:
    def __init__(self, fp_no, amount):
        self.member_info = precondition.member_info
        self.oil = precondition.fp_info(fp_no)
        self.amount = amount
        self.hq_func_config = db.select_db(column='*', table='erp_hq.hq_function_config',
                                           where=f'HQ_ID={self.member_info["HQ_ID"]}')
        self.grade_info = precondition.grade_config(self.oil['PRICE'])

    def grade_point_count(self, amount):
        """
        会员等级积分计算
        :param amount: 计算值
        :return:积分
        """
        amount = self.amount_form(amount)
        if 'POINT' in self.grade_info[1]:
            return int(amount * self.grade_info[1]['POINT'])
        else:
            if self.oil['PR_NAME'][-2:] == U'汽油':
                return int(amount * self.grade_info[1]['GAS_POINT'])
            elif self.oil['PR_NAME'][-2:] == U'柴油':
                return int(amount * self.grade_info[1]['DIESEL_POINT'])

    def upgrade_count(self, amount):
        """
        成长值计算
        :param amount: 计算值
        :return: 成长值
        """
        amount = self.amount_form(amount)
        if self.oil['PR_NAME'][-2:] == U'汽油':
            return int(amount * self.grade_info[1]['GAS_UPGRADE'])
        elif self.oil['PR_NAME'][-2:] == U'柴油':
            return int(amount * self.grade_info[1]['DIESEL_UPGRADE'])

    # 未做优惠 暂时先获取元素 进行计算  后续传入应付金额
    def amount_form(self, amount):
        flag = self.hq_func_config['UPGRADE_POINT_CALCULATE_TYPE']
        if flag == 0:
            return amount[U'支付金额']
        else:
            return self.oil_liters()

    def oil_liters(self):
        """
        获取油品升数
        :return:
        """
        lites = int((self.amount / self.oil["PRICE"]) * 100 + 1) / 100
        return float(lites)

    def get_grade_point(self, amount):
        """
        获取会员积分
        :param amount: 金额或升数
        :return:积分
        """
        count = self.grade_point_count(amount)
        if self.member_info['GRADE_TYPE'] != 0:
            count = self.hq_func_config['IS_UPGRADE_POINT'] == 1 and count or 0
            return count
        else:
            return count

    def get_upgrade_value(self, amount):
        """
        获取成长值
        :param amount: 金额或升数
        :return: 成长值
        """
        count = self.upgrade_count(amount)
        if self.hq_func_config['IS_BALANCE_PAY'] == 0 and self.hq_func_config['ORDER_MIN_AMOUNT'] < self.amount:
            if self.get_upgrade_additional() == int(self.hq_func_config['MONTH_RECHARGE_COUNT']) + 1:
                return count + int(self.hq_func_config['MONTH_ADD_VALUE'])
            else:
                return count
        else:
            return 0

    def get_upgrade_additional(self):
        """
        获取满足附加成长值的次数
        :return: 次数
        """
        table = db.select_db(column='table_name', table='data_dict.table_config', where='FIND_IN_SET(16548,hq_ids)')
        table, = table.values()
        record = db.select_db(False, table=f'trade.2019_{table}',
                              where=f'HQ_ID = {self.member_info["HQ_ID"]} and '
                                    f'MEMBER_ID ={self.member_info["MEMBER_ID"]} and '
                                    f'RECEIVABLE_AMOUNT > {self.hq_func_config["MONTH_RECHARGE_AMOUNT"]} '
                                    f' and  DATE_FORMAT( CREATED_TIME, "%Y%m" ) = DATE_FORMAT(CURDATE() , "%Y%m" )')
        return len(record)

    def grade_discount_type(self, discount):
        if self.grade_info[1]['DISCOUNT_TYPE'] == 1:
            discount = int(discount / 100 * float(self.oil["PRICE"]) * 100) / 100
            return discount
        else:
            return discount

    def grade_descent_count(self):
        if self.hq_func_config['MEMBER_GRADE_PRIVILEGE_TYPE'] == 0:
            if self.grade_info[0] in (1, 3):
                return int(self.oil_liters()) * float(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
            else:
                if self.oil['PR_NAME'][-2:] == U'汽油':
                    return int(self.oil_liters()) * float(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
                elif self.oil['PR_NAME'][-2:] == U'柴油':
                    return int(self.oil_liters()) * float(
                        self.grade_discount_type(self.grade_info[1]['DIESEL_SALE_AMOUNT']))
        else:
            if self.grade_info[0] in (1, 3):
                return self.oil_liters() * float(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
            else:
                if self.oil['PR_NAME'][-2:] == U'汽油':
                    return self.oil_liters() * float(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
                elif self.oil['PR_NAME'][-2:] == U'柴油':
                    return self.oil_liters() * float(self.grade_discount_type(self.grade_info[1]['DIESEL_SALE_AMOUNT']))

    def get_discount_grade(self):
        if self.hq_func_config['NOT_BALANCE_DISCOUNT'] in (1, 0):
            return float(f'{self.grade_descent_count():0.2f}')
        else:
            return 0


