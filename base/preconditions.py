#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：preconditions.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/17 
"""
import queue
import time
from decimal import Decimal

from common.db_mysql import DB_sql
from base import yaml_handle
from common.interface import OilServer

db = DB_sql()


class Precondition:
    # 会员信息  积分，优惠，成长值规则 站点油品油枪 条件通过读取配置判断
    def __init__(self):
        self.member_info = Precondition.get_member()
        self.station_id = yaml_handle.param_value("stationId")

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
        if member_account['AMOUNT'] == Decimal(0):
            OilServer().charge(500, member_id)
            member_account['AMOUNT'] = member_account['AMOUNT'] + Decimal(500)
        member_info.update(member_account)
        grade_type = db.select_db(column='GRADE_TYPE', table='erp_hq.member_grade_config',
                                  where=f'ID = {member["HQ_MEMBER_GRADE_ID"]}')
        member_info.update(grade_type)
        v, = grade_type.values()
        if v != Decimal(0):
            upgrade_value = db.select_db(column='MEMBER_UPGRADE_VALUE', table='crm.member_grade',
                                         where=f'MEMBER_ID = {member_id}')

            member_info.update(upgrade_value)
        return member_info

    @staticmethod
    def self_pay_id_info(hq_id, self_pay_id):
        table_name = db.select_db(sql=f'select table_name from data_dict.self_table_config'
                                      f'  where FIND_IN_SET({hq_id},hq_ids)')

        i = 0
        while i <= 10:
            info = db.select_db(sql=f'SELECT * FROM trade.2021_{table_name} where ORDER_ID ="{self_pay_id}"')
            if info['REF_FUELLING_ORDER_ID'] not in ("", None):
                return info
            else:
                time.sleep(2)
            i += 1

    def fp_info(self, num):
        """
        根据用例参数，获取站点下油枪信息
        :param num: 油枪号
        :return: 油枪信息 （油枪号，价格，油品名称）
        """
        fp = db.select_db(column='FP_NO,PR_NAME,PRICE', table='erp_station.fp_monitor_history',
                          where=f'STATION_ID = {self.station_id} and FP_NO = {num}')
        return fp

    def grade_config(self, fp_name: str):
        """
        获取 等级优惠 积分 成长值 基本信息
        :return: 等级优惠 积分 成长值 基本信息
        """
        grade_id = self.member_info['HQ_MEMBER_GRADE_ID']
        grade_type = self.member_info['GRADE_TYPE']
        hq_id = self.member_info['HQ_ID']
        station_id = self.station_id
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
                                              f'AND advanced.HQ_ID = {hq_id}')

        station_task = db.select_db(
            column='discount.GAS_POINT,discount.SALE_AMOUNT,discount.DIESEL_POINT,'
                   'discount.DIESEL_SALE_AMOUNT,discount.DISCOUNT_TYPE,discount.MIN_FUEL_AMOUNT',
            table='erp_station.grade_discount_config AS discount',
            join='INNER JOIN erp_station.station_grade_config AS station ON discount.REF_CONFIG_ID = station.ID ',
            where=f' GRADE_ID = {grade_id} '
                  f'AND FIND_IN_SET({station_id},USABLE_STATION_IDS)'
                  f'AND discount.HQ_ID = {hq_id}')
        grade_adv_task = db.select_db(
            column='SALE_AMOUNT,POINT',
            table='erp_hq.grade_pr_advanced_config',
            where=f'GRADE_ID = {grade_id} and HQ_ID={hq_id} and PR_NAME = {fp_name}'
        )
        grade_task = db.select_db(column='SALE_AMOUNT,DIESEL_SALE_AMOUNT,POINT,DIESEL_POINT,DISCOUNT_TYPE,GAS_UPGRADE,'
                                         'DIESEL_UPGRADE,MIN_CONSUME_AMOUNT',
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
                if value is not None and priority in (1, 2):
                    member_grade[1].update({'DISCOUNT_TYPE': station_task['DISCOUNT_TYPE'],
                                            'MIN_FUEL_AMOUNT': station_task['MIN_FUEL_AMOUNT']
                                            })
                    return member_grade
                elif value is not None and priority in (3, 4):
                    member_grade[1].update({'DISCOUNT_TYPE': grade_task['DISCOUNT_TYPE'],
                                            'MIN_CONSUME_AMOUNT': grade_task['MIN_CONSUME_AMOUNT']
                                            })
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
                 ['GAS_UPGRADE', 'DIESEL_UPGRADE', 'POINT', 'DIESEL_POINT']]
                qp.put((4, grade_task_copy))
                while not qp.empty():
                    member_grade_discount = qp.get()
                    dis_priority, dis_value = member_grade_discount
                    if dis_value is not None and dis_priority in (1, 2):
                        qp.queue.clear()
                        member_grade_discount[1].update({'DISCOUNT_TYPE': station_task['DISCOUNT_TYPE']})
                        return member_grade_discount
                    elif dis_value is not None and dis_priority in (3, 4):
                        qp.queue.clear()
                        member_grade_discount[1].update({'DISCOUNT_TYPE': grade_task['DISCOUNT_TYPE']})
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
                {'GAS_UPGRADE': grade_task['GAS_UPGRADE'], 'DIESEL_UPGRADE': grade_task['DIESEL_UPGRADE']})
            return member_grade
