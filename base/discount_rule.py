#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：discount_rule.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/27 
"""
import time

from common.db_mysql import DB_sql
from base.preconditions import Precondition
from common.interface import Openapi

db = DB_sql()
precondition = Precondition()


class Discount:
    def __init__(self, fp_no, amount):
        self.member_info = precondition.member_info
        self.oil = precondition.fp_info(fp_no)
        self.station_id = precondition.station_id
        self.amount = amount
        self.hq_func_config = db.select_db(column='*', table='erp_hq.hq_function_config',
                                           where=f'HQ_ID={self.member_info["HQ_ID"]}')
        self.grade_info = precondition.grade_config(self.oil['PR_NAME'])

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

    def amount_form(self, amount):
        """
        会员加油积分、成长值计算方式  0:按加油实收金额计算;1:按加油实际升数计算
        :param amount: 支付金额
        :return:
        """
        flag = self.hq_func_config['UPGRADE_POINT_CALCULATE_TYPE']
        if flag == 0:
            return amount
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
        获取会员积分  判断规则（成长性会员支不支持积分）
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
        获取成长值 判断规则（获取的条件和奖励）
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
        table = db.select_db(column='table_name', table='data_dict.table_config',
                             where=f'FIND_IN_SET({self.member_info["HQ_ID"]},hq_ids)')
        table, = table.values()
        record = db.select_db(False, table=f'trade.2019_{table}',
                              where=f'HQ_ID = {self.member_info["HQ_ID"]} and '
                                    f'MEMBER_ID ={self.member_info["MEMBER_ID"]} and '
                                    f'RECEIVABLE_AMOUNT > {self.hq_func_config["MONTH_RECHARGE_AMOUNT"]} '
                                    f' and  DATE_FORMAT( CREATED_TIME, "%Y%m" ) = DATE_FORMAT(CURDATE() , "%Y%m" )')
        return len(record)

    def grade_discount_type(self, discount):
        """
        会员优惠类型 DISCOUNT_TYPE 1.折扣 2.直降
        :param discount:
        :return:
        """
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
        min_amount = 'MIN_FUEL_AMOUNT' in self.grade_info[1] and self.grade_info[1]['MIN_FUEL_AMOUNT'] or \
                     ('MIN_CONSUME_AMOUNT' in self.grade_info[1] and self.grade_info[1]['MIN_CONSUME_AMOUNT'])
        if self.hq_func_config['NOT_BALANCE_DISCOUNT'] in (1, 0) and \
                self.amount >= float(min_amount):
            return float(f'{self.grade_descent_count():0.2f}')
        else:
            return 0

    def coupon_amount(self) -> float:
        coupon = db.select_db(False, sql=f"SELECT * FROM marketing.`coupon` WHERE BATCH_NO in (SELECT BATCH_NO FROM "
                                         f"`crm`.`member_coupon` WHERE `MEMBER_ID` = {self.member_info['MEMBER_ID']}"
                                         f" AND `STATUS` = '1' "
                                         f"AND `TYPE` IN (1,6)  GROUP BY BATCH_NO) and USE_CONSUMPTION_TYPE = 0 and "
                                         f"USE_SCENE_TYPE in (1,2)")
        coupon_copy = list(coupon)
        times = Openapi().now_time().split(' ')[1]
        wday, mday = Openapi().now_time(False)
        for i in coupon_copy:
            if self.amount < float(i['MINIMUM_AMOUNT']):
                coupon.remove(i)
                continue
            if i['IS_ALL_STATIONS'] == 0:
                if str(self.station_id) not in i['USABLE_STATION_IDS']:
                    coupon.remove(i)
                    continue
            if i['IS_ALL_PRS'] == 0:
                if self.oil['PR_NAME'] not in i['PR_NAMES']:
                    coupon.remove(i)
                    continue
            if i['IS_ALL_DAYS'] == 2:
                if str(wday) not in i['USABLE_WEEK']:
                    coupon.remove(i)
                    continue
            elif i['IS_ALL_DAYS'] == 3:
                if str(mday) not in i['USABLE_DAYS']:
                    coupon.remove(i)
                    continue
            if i['AVAILABLE_TIME_SCOPE'] not in ('', None):
                time_scope = i['AVAILABLE_TIME_SCOPE'].split('-')
                start, end = time_scope
                if time.strptime(start, '%H:%M:%S') <= time.strptime(times, '%H:%M:%S') <= time.strptime(end,
                                                                                                         '%H:%M:%S'):
                    pass
                else:
                    coupon.remove(i)
                    continue
            if i['TYPE'] == 6:
                coupon.remove(i)
                discount_amount = (10 - i['DIS_LEVEL']) * self.amount / 10
                if discount_amount <= i['DISCOUNT_AMOUNT']:
                    i['DISCOUNT_AMOUNT'] = discount_amount
                    coupon.append(i)
                else:
                    coupon.append(i)
        if len(coupon) == 1:
            return coupon[0]['DISCOUNT_AMOUNT']
        elif len(coupon) > 1:
            discount_amount = []
            for i in range(len(coupon)):
                discount_amount.append(coupon[i]['DISCOUNT_AMOUNT'])
            discount_amount.sort()
            return discount_amount[-1]
        else:
            return 0
