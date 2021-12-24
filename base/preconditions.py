#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：preconditions.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/17 
"""
import queue

from common.db_mysql import DB_sql
from base import yaml_handle

db = DB_sql()


class Precondition:
    # 会员信息  积分，优惠，成长值规则 站点油品油枪 条件通过读取配置判断
    def __init__(self, fp_no, amount, member_info):
        self.member_info = member_info
        self.oil = Precondition.fp_info(fp_no)
        self.amount = amount
        self.grade_info = self.grade_config()
        self.hq_func_config = db.select_db(column='*', table='erp_hq.hq_function_config',
                                           where=f'HQ_ID={self.member_info["HQ_ID"]}')

    @staticmethod
    def get_member(member_id=yaml_handle.param_value('memberId')):
        """
        获取会员基本信息
        :param member_id: 会员ID
        :return: 会员信息 （会员ID 总部ID 等级ID 会员姓名 手机号 等级名称 等级类型 成长值 积分 余额 ）
        """
        member_info = {}
        member = db.select_db(column='HQ_MEMBER_GRADE_ID,HQ_ID,MEMBER_ID,MEMBER_NAME,PHONE_NUM,HQ_MEMBER_GRADE_NAME',
                              table='crm.member', where=f'MEMBER_ID = {member_id}')
        member_info.update(member)
        member_account = db.select_db(column='AMOUNT, POINT',
                                      table='crm.member_account', where=f'MEMBER_ID = {member_id}')
        member_info.update(member_account)
        grade_type = db.select_db(column='GRADE_TYPE', table='erp_hq.member_grade_config',
                                  where=f'ID = {member["HQ_MEMBER_GRADE_ID"]}')
        member_info.update(grade_type)
        v, = grade_type.values()
        if v != 0:
            upgrade_value = db.select_db(column='MEMBER_UPGRADE_VALUE', table='crm.member_grade',
                                         where=f'MEMBER_ID = {member_id}')

            member_info.update(upgrade_value)
        return member_info

    # 传参  用例数据
    @staticmethod
    def fp_info(num):
        """
        根据用例参数，获取站点下油枪信息
        :param num: 油枪号
        :return: 油枪信息 （油枪号，价格，油品名称）
        """
        fp = db.select_db(column='FP_NO,PR_NAME,PRICE', table='erp_station.fp_monitor_history',
                          where=f'STATION_ID = {yaml_handle.param_value("stationId")} and FP_NO = {num}')
        return fp

    def grade_config(self):
        """
        获取 等级优惠 积分 成长值 基本信息
        :return: 等级优惠 积分 成长值 基本信息
        """
        grade_id = self.member_info['HQ_MEMBER_GRADE_ID']
        grade_type = self.member_info['GRADE_TYPE']
        hq_id = self.member_info['HQ_ID']
        station_id = yaml_handle.param_value('stationId')
        fp_name = self.oil['PR_NAME']
        station_adv_task = db.select_db(column='advanced.SALE_AMOUNT,advanced.POINT',
                                        table='erp_station.`grade_pr_advanced_config` AS advanced',
                                        join='INNER JOIN (SELECT discount.ID, discount.REF_CONFIG_ID,'
                                             'station.USABLE_STATION_IDS,station.RULE_TYPE '
                                             ' FROM erp_station.grade_discount_config AS discount '
                                             'INNER JOIN erp_station.station_grade_config AS station ON '
                                             'discount.REF_CONFIG_ID = station.ID '
                                             ') AS discount ON advanced.REF_ID = discount.ID ',
                                        where=f'GRADE_ID = {grade_id} '
                                              f'AND PR_NAME = "{fp_name}" '
                                              f'AND FIND_IN_SET({station_id},USABLE_STATION_IDS)'
                                              f'AND HQ_ID = {hq_id}')

        station_task = db.select_db(
            column='discount.GAS_POINT,discount.SALE_AMOUNT,discount.DIESEL_POINT,discount.DIESEL_SALE_AMOUNT',
            table='erp_station.grade_discount_config AS discount',
            join='INNER JOIN erp_station.station_grade_config AS station ON discount.REF_CONFIG_ID = station.ID ',
            where=f' GRADE_ID = {grade_id} '
                  f'AND FIND_IN_SET({station_id},USABLE_STATION_IDS)'
                  f'AND HQ_ID = {hq_id}')
        grade_adv_task = db.select_db(
            column='SALE_AMOUNT,POINT',
            table='erp_hq.grade_pr_advanced_config',
            where=f'GRADE_ID = {grade_id} and HQ_ID={hq_id} and PR_NAME = {fp_name}'
        )
        grade_task = db.select_db(column='SALE_AMOUNT,DIESEL_SALE_AMOUNT,POINT,DIESEL_POINT,DISCOUNT_TYPE,GAS_UPGRADE,'
                                         'DIESEL_UPGRADE',
                                  table='erp_hq.member_grade_config',
                                  where=f'ID = {grade_id} and HQ_ID={hq_id} ')
        qp = queue.PriorityQueue()
        if grade_type == 0:
            qp.put((1, station_adv_task))
            qp.put((2, station_task))
            qp.put((3, grade_adv_task))
            grade_task.pop('GAS_UPGRADE', 'DIESEL_UPGRADE')
            qp.put((4, grade_task))
            while not qp.empty():
                member_grade = qp.get()
                priority, value = member_grade
                if value is not None:
                    member_grade.update({'DISCOUNT_TYPE': grade_task['DISCOUNT_TYPE']})
                    return member_grade
        else:
            def grade_discount():
                if station_adv_task is not None:
                    station_adv_task_copy = station_adv_task.copy()
                    station_adv_task_copy.pop('POINT')
                    qp.put((1, station_adv_task_copy))
                elif station_task is not None:
                    station_task_copy = station_task.copy()
                    [station_task_copy.pop(k) for k in ['GAS_POINT', 'DIESEL_POINT']]
                    qp.put((2, station_task_copy))
                elif grade_adv_task is not None:
                    grade_adv_task_copy = grade_adv_task.copy()
                    grade_adv_task_copy.pop('POINT')
                    qp.put((3, grade_adv_task_copy))
                grade_task_copy = grade_task.copy()
                [grade_task_copy.pop(k) for k in
                 ['GAS_UPGRADE', 'DIESEL_UPGRADE', 'POINT', 'DISCOUNT_TYPE', 'DIESEL_POINT']]
                qp.put((4, grade_task_copy))
                while not qp.empty():
                    member_grade_discount = qp.get()
                    dis_priority, dis_value = member_grade_discount
                    if dis_value is not None:
                        qp.queue.clear()
                        return member_grade_discount

            def grade_point():
                if station_adv_task is not None:
                    station_adv_task_copy = station_adv_task.copy()
                    station_adv_task_copy.pop('SALE_AMOUNT')
                    qp.put((1, station_adv_task_copy))
                elif grade_adv_task is not None:
                    grade_adv_task_copy = grade_adv_task.copy()
                    grade_adv_task_copy.pop('SALE_AMOUNT')
                    qp.put((3, grade_adv_task_copy))

                grade_task_copy = grade_task.copy()
                [grade_task_copy.pop(k) for k in
                 ['GAS_UPGRADE', 'DIESEL_UPGRADE', 'SALE_AMOUNT', 'DIESEL_SALE_AMOUNT', 'DISCOUNT_TYPE']]

                qp.put((4, grade_task_copy))
                while not qp.empty():
                    member_grade_point = qp.get()
                    point_priority, point_value = member_grade_point
                    if point_value is not None:
                        qp.queue.clear()
                        return point_value

            member_grade = grade_discount()

            member_grade[1].update(grade_point())
            member_grade[1].update(
                {'GAS_UPGRADE': grade_task['GAS_UPGRADE'], 'DIESEL_UPGRADE': grade_task['DIESEL_UPGRADE'],
                 'DISCOUNT_TYPE': grade_task['DISCOUNT_TYPE']})
            return member_grade

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
            if self.oil[-2:] == U'汽油':
                return int(amount * self.grade_info[1]['GAS_POINT'])
            elif self.oil[-2:] == U'柴油':
                return int(amount * self.grade_info[1]['DIESEL_POINT'])

    def upgrade_count(self,amount):
        """
        成长值计算
        :param amount: 计算值
        :return: 成长值
        """
        amount = self.amount_form(amount)
        if self.oil[-2:] == U'汽油':
            return int(amount * self.grade_info[1]['GAS_UPGRADE'])
        elif self.oil[-2:] == U'柴油':
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
        lites = int((self.amount / self.oil["PRICE"])*100+1)/100
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

    def grade_count(self):
        if self.hq_func_config['MEMBER_GRADE_PRIVILEGE_TYPE'] == 0:
            if self.grade_info[0] in (1, 3):
                return int(self.oil_liters()) * float(self.grade_info[1]['SALE_AMOUNT'])
            else:
                if self.oil[-2:] == U'汽油':
                    return int(self.oil_liters()) * float(self.grade_info[1]['SALE_AMOUNT'])
                elif self.oil[-2:] == U'柴油':
                    return int(self.oil_liters()) * float(self.grade_info[1]['DIESEL_SALE_AMOUNT'])
        else:
            if self.grade_info[0] in (1, 3):
                return self.oil_liters() * float(self.grade_info[1]['SALE_AMOUNT'])
            else:
                if self.oil[-2:] == U'汽油':
                    return self.oil_liters() * float(self.grade_info[1]['SALE_AMOUNT'])
                elif self.oil[-2:] == U'柴油':
                    return self.oil_liters() * float(self.grade_info[1]['DIESEL_SALE_AMOUNT'])

    def get_discount_grade(self):
        if self.hq_func_config['NOT_BALANCE_DISCOUNT'] in (1, 0):
            return float(f'{self.grade_count():0.2f}')
        else:
            return 0