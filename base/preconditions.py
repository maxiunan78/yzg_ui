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
import yaml_handle

db = DB_sql()


def get_member(member_id=yaml_handle.param_value('memberId')):
    member_info = {}
    member = db.select_db(column='HQ_MEMBER_GRADE_ID,HQ_ID,MEMBER_ID,MEMBER_NAME,PHONE_NUM,HQ_MEMBER_GRADE_NAME',
                          table='crm.member', where=f'MEMBER_ID = {member_id}')
    member_info.update(member)
    member_account = db.select_db(column='AMOUNT, POINT',
                                  table='crm.member_account', where=f'MEMBER_ID = {member_id}')
    member_info.update(member_account)
    grade_type = db.select_db(column='GRADE_TYPE', table='erp_hq.member_grade_config',
                              where=f'ID = {member["HQ_MEMBER_GRADE_ID"]}')

    v, = grade_type.values()
    if v != 0:
        upgrade_value = db.select_db(column='MEMBER_UPGRADE_VALUE', table='crm.member_grade',
                                     where=f'MEMBER_ID = {member_id}')

        member_info.update(upgrade_value)
    return member_info
# 传参  用例数据
fp_name = '95#汽油'



class Precondition:
    # 会员信息  积分，优惠，成长值规则 站点油品油枪 条件通过读取配置判断
    def __init__(self):
        self.member_info = get_member()
        self.grade_info = self.grade_config()
        self.oil = fp_name

    @property
    def get_member_info(self):
        return self.member_info

    def grade_config(self):
        grade_id = self.member_info['HQ_MEMBER_GRADE_ID']
        grade_type = self.member_info['GRADE_TYPE']
        hq_id = self.member_info['HQ_ID']
        station_id = yaml_handle.param_value('stationId')
        station_adv_task = db.select_db(column='advanced.SALE_AMOUNT,advanced.POINT',
                                        table='erp_station.`grade_pr_advanced_config` AS advanced',
                                        join='INNER JOIN (SELECT discount.ID, discount.REF_CONFIG_ID,startion.USABLE_STATION_IDS,startion.RULE_TYPE'
                                             ' FROM erp_station.grade_discount_config AS discount '
                                             'INNER JOIN erp_station.station_grade_config AS startion ON discount.REF_CONFIG_ID = startion.ID '
                                             ') AS discount ON advanced.REF_ID = discount.ID ',
                                        where=f'advanced.GRADE_ID = {grade_id} '
                                              f'AND advanced.PR_NAME = "{fp_name}" '
                                              f'AND discount.USABLE_STATION_IDS LIKE "%{station_id}%"'
                                              f'AND advanced.HQ_ID = {hq_id}')

        station_task = db.select_db(
            column='discount.GAS_POINT,discount.SALE_AMOUNT,discount.DIESEL_POINT,discount.DIESEL_SALE_AMOUNT',
            table='erp_station.grade_discount_config AS discount',
            join='INNER JOIN erp_station.station_grade_config AS startion ON discount.REF_CONFIG_ID = startion.ID ',
            where=f' discount.GRADE_ID = {grade_id} '
                  f'AND startion.USABLE_STATION_IDS LIKE "%{station_id}%"'
                  f'AND discount.HQ_ID = {hq_id}')
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
                    print(member_grade)
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
                        print(member_grade_discount)
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
                        print(point_value)
                        return point_value

            member_grade = grade_discount()

            member_grade[1].update(grade_point())
            member_grade[1].update(
                {'GAS_UPGRADE': grade_task['GAS_UPGRADE'], 'DIESEL_UPGRADE': grade_task['DIESEL_UPGRADE'],
                 'DISCOUNT_TYPE': grade_task['DISCOUNT_TYPE']})
            print(member_grade)
            return member_grade

    def grade_point_count(self, amount):
        if self.grade_info[0] in (1, 3):
            return int(amount * self.grade_info[1]['POINT'])
        elif self.grade_info[0] == 2:
            if self.oil[-2:] == U'汽油':
                return int(amount * self.grade_info[1]['GAS_POINT'])
            elif self.oil[-2:] == U'柴油':
                return int(amount * self.grade_info[1]['DIESEL_POINT'])
        else:
            if self.oil[-2:] == U'汽油':
                return int(amount * self.grade_info[1]['POINT'])
            elif self.oil[-2:] == U'柴油':
                return int(amount * self.grade_info[1]['DIESEL_POINT'])

    def upgrade_count(self, amount):
        if self.oil[-2:] == U'汽油':
            return int(amount * self.grade_info[1]['GAS_UPGRADE'])
        elif self.oil[-2:] == U'柴油':
            return int(amount * self.grade_info[1]['DIESEL_UPGRADE'])
