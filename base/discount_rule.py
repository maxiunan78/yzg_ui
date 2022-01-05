#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：discount_rule.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/27 
"""
import time
from decimal import Decimal

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
        if 'POINT' in self.grade_info[1] and 'DIESEL_POINT' not in self.grade_info[1]:
            return int(amount * self.grade_info[1]['POINT'])
        elif 'POINT' in self.grade_info[1] and 'DIESEL_POINT' in self.grade_info[1]:
            if self.oil['PR_NAME'][-2:] == U'汽油':
                return int(amount * self.grade_info[1]['POINT'])
            elif self.oil['PR_NAME'][-2:] == U'柴油':
                return int(amount * self.grade_info[1]['DIESEL_POINT'])
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
            return int(amount * float(self.grade_info[1]['GAS_UPGRADE']))
        elif self.oil['PR_NAME'][-2:] == U'柴油':
            return int(amount * float(self.grade_info[1]['DIESEL_UPGRADE']))

    def amount_form(self, amount) -> float:
        """
        会员加油积分、成长值计算方式  0:按加油实收金额计算;1:按加油实际升数计算
        :param amount: 支付金额
        :return:
        """
        flag = self.hq_func_config['UPGRADE_POINT_CALCULATE_TYPE']
        if flag == 0:
            return float(amount)
        else:
            return float(self.oil_liters())

    def oil_liters(self) -> Decimal:
        """
        获取油品升数
        :return:
        """
        digit = str(Decimal(self.amount) / Decimal(self.oil["PRICE"])).split('.')[1]
        if len(digit) >= 3:
            lites = int((Decimal(self.amount) / Decimal(self.oil["PRICE"])) * 100 + 1) / 100
            return Decimal(f'{lites:0.2f}')
        else:
            lites = self.amount / Decimal(self.oil["PRICE"])
            return Decimal(f'{lites:0.2f}')

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
                                    f' and PAY_STATUS = 1'
                                    f' and  DATE_FORMAT( CREATED_TIME, "%Y%m" ) = DATE_FORMAT(CURDATE() , "%Y%m" )')
        return len(record)

    def grade_discount_type(self, discount):
        """
        会员优惠类型 DISCOUNT_TYPE 1.折扣 2.直降
        :param discount: 优惠价格
        :return:
        """
        if self.grade_info[1]['DISCOUNT_TYPE'] == 1:
            discount = int(Decimal(discount) / 100 * self.oil["PRICE"] * 100) / 100
            return discount
        else:
            return discount

    def grade_descent_count(self):
        """
        等级优惠判断计算
        :return:
        """
        if self.hq_func_config['MEMBER_GRADE_PRIVILEGE_TYPE'] == 0:
            if self.grade_info[0] in (1, 3):
                return int(self.oil_liters()) * Decimal(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
            else:
                if self.oil['PR_NAME'][-2:] == U'汽油':
                    return int(self.oil_liters()) * Decimal(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
                elif self.oil['PR_NAME'][-2:] == U'柴油':
                    return int(self.oil_liters()) * Decimal(
                        self.grade_discount_type(self.grade_info[1]['DIESEL_SALE_AMOUNT']))
        else:
            if self.grade_info[0] in (1, 3):
                return self.oil_liters() * Decimal(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
            else:
                if self.oil['PR_NAME'][-2:] == U'汽油':
                    return self.oil_liters() * Decimal(self.grade_discount_type(self.grade_info[1]['SALE_AMOUNT']))
                elif self.oil['PR_NAME'][-2:] == U'柴油':
                    return self.oil_liters() * Decimal(
                        self.grade_discount_type(self.grade_info[1]['DIESEL_SALE_AMOUNT']))

    def get_discount_grade(self):
        """
        获取等级优惠
        :return:
        """
        min_amount = 'MIN_FUEL_AMOUNT' in self.grade_info[1] and self.grade_info[1]['MIN_FUEL_AMOUNT'] or \
                     ('MIN_CONSUME_AMOUNT' in self.grade_info[1] and self.grade_info[1]['MIN_CONSUME_AMOUNT'])
        if self.hq_func_config['NOT_BALANCE_DISCOUNT'] in (1, 0) and \
                self.amount >= Decimal(min_amount):
            return Decimal(f'{self.grade_descent_count():0.2f}')
        else:
            return 0

    def coupon_amount(self) -> float:
        """
        优惠券判断计算
        :return:
        """
        coupon = db.select_db(False, sql=f"SELECT * FROM marketing.`coupon` WHERE BATCH_NO in (SELECT BATCH_NO FROM "
                                         f"`crm`.`member_coupon` WHERE `MEMBER_ID` = {self.member_info['MEMBER_ID']}"
                                         f" AND `STATUS` = '1' "
                                         f"AND `TYPE` IN (1,6)  GROUP BY BATCH_NO) and USE_CONSUMPTION_TYPE = 0 and "
                                         f"USE_SCENE_TYPE in (1,2)")
        coupon_copy = list(coupon)
        times = Openapi().now_time().split(' ')[1]
        wday, mday = Openapi().now_time(False)
        for i in coupon_copy:
            if self.amount < Decimal(i['MINIMUM_AMOUNT']):
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

    def special_activity_count(self):
        """
        特惠活动 判断计算
        :return:
        """
        activity = db.select_db(False, sql="SELECT * FROM `marketing`.`activity` WHERE `TYPE` = '64' AND `STATUS` = '1'"
                                           f" and HQ_ID ={self.member_info['HQ_ID']}")
        activity_copy = list(activity)
        times = Openapi().now_time().split(' ')[1]
        wday, mday = Openapi().now_time(False)

        for i in activity_copy:
            if i['IS_ALL_GRADES'] == 0:
                if str(self.member_info['HQ_MEMBER_GRADE_ID']) not in i['USABLE_GRADE_IDS']:
                    activity.remove(i)
                    continue
            if self.amount < Decimal(i['MIN_FUEL_AMOUNT']):
                activity.remove(i)
                continue
            if i['IS_ALL_STATIONS'] == 0:
                if str(self.station_id) not in i['USABLE_STATION_IDS']:
                    activity.remove(i)
                    continue
            if i['IS_ALL_PRS'] == 0:
                if self.oil['PR_NAME'] not in i['USABLE_PR_NAMES']:
                    activity.remove(i)
                    continue
            if i['USABLE_WEEK'] is not None and str(wday) not in i['USABLE_WEEK']:
                activity.remove(i)
                continue
            elif i['USABLE_DAYS'] is not None and str(mday) not in i['USABLE_DAYS']:
                activity.remove(i)
                continue
            if i['CONDITION_VALUE_3'] not in ('', None):
                time_scope = i['CONDITION_VALUE_3'].split(',')
                temp = []
                for scope in time_scope:
                    time_start, time_end = scope.split('-')
                    if time.strptime(time_start, '%H:%M:%S') <= time.strptime(times, '%H:%M:%S') <= time.strptime(
                            time_end, '%H:%M:%S'):
                        temp.append(1)
                    else:
                        temp.append(0)
                if 1 not in temp:
                    activity.remove(i)
        if len(activity) <= 0:
            return 1, 0
        else:
            activity_amt = 0
            # 目前因优惠互斥 存在问题  未进行判断
            grade_type = 0
            for dis_activity in activity:
                if dis_activity['ENJOY_MEMBER_GRADE_DIS'] == 1:
                    grade_type = 1
                activity_amt = Decimal(activity_amt) + Decimal(dis_activity['CONDITION_VALUE_4'])
            activity_amt = self.hq_func_config['SPECIAL_DISCOUNT'] in (1, 0) and Decimal(
                f'{activity_amt * self.oil_liters():0.2f}') or 0
            return grade_type, activity_amt

    @staticmethod
    def times_scope(time_scopes: str):
        times = Openapi().now_time().split(' ')[1]

        flag = False
        if time_scopes is not ('' or None):
            time_scopes = time_scopes.split(',')
            for scope in time_scopes:
                time_start, time_end = scope.split('-')
                if time.strptime(time_start, '%H:%M:%S') <= time.strptime(times, '%H:%M:%S') <= time.strptime(
                        time_end, '%H:%M:%S'):
                    flag = True
        return flag

    def coupon(self):
        """
        获取优惠券
        :return:
        """
        times = Openapi().now_time().split(' ')
        wday, mday = Openapi().now_time(False)
        flag = False
        if self.hq_func_config['CAN_USE_CASH_COUPON'] == 1:
            if self.hq_func_config['IS_ALLOWED_USE_COUPON'] == 0 and \
                    time.strptime(str(self.hq_func_config['COUPON_LIMIT_START_TIME']), '%Y-%m-%d') \
                    <= time.strptime(times[0], '%Y-%m-%d') <= time.strptime(
                str(self.hq_func_config['COUPON_LIMIT_END_TIME']), '%Y-%m-%d'):
                flag = self.times_scope(self.hq_func_config['TIME_SCOPE'])
            elif self.hq_func_config['IS_ALLOWED_USE_COUPON'] == 2:
                if str(mday) in self.hq_func_config['DATE_SCOPE']:
                    flag = self.times_scope(self.hq_func_config['TIME_SCOPE'])
            elif self.hq_func_config['IS_ALLOWED_USE_COUPON'] == 3:
                if str(wday) in self.hq_func_config['DATE_SCOPE']:
                    flag = self.times_scope(self.hq_func_config['TIME_SCOPE'])

            if not flag:
                return self.coupon_amount()
            else:
                return 0

        else:
            return 0

    def total_discount(self):
        """
        获得总优惠
        :return:
        """
        grade = Decimal(self.get_discount_grade())
        coupon = Decimal(self.coupon())
        grade_act_type, activity_amt = self.special_activity_count()

        if grade_act_type == 0:
            return Decimal(f'{(grade < activity_amt and activity_amt or grade) + coupon:0.2f}')
        else:

            return Decimal(f'{grade + activity_amt + coupon:0.2f}')

    def pay_amount(self):
        """
        获得支付金额
        :return:
        """
        pay = self.amount - self.total_discount()
        return pay > 0 and pay or 0


