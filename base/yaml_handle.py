#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：yaml_handle.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
from common.read_data import Data
from common.db_mysql import DB_sql

DATA = Data().data
ELEMENT = Data().element
DATABASE = DB_sql()


def element_page(key) -> dict:
    """
    获取配置文件页面的所有元素
    :param key: 页面
    :return: 配置的页面中所有元素
    """
    return ELEMENT[key]


def element_value(key, value) -> str:
    """
    获取配置文件页面的指定元素数据
    :param value: 定位元素
    :param key: 页面
    :return: 指定的元素数据
    """
    return ELEMENT[key][value]


def param_value(key) -> str:
    """
    取出data文件指定值
    :param key: 指定项
    :return: 指定值
    """

    return DATA[key]


def param_dict(*keys) -> dict:
    """
    获取多项，值的数据
    :param keys: 指定项 （元组形式指定）
    :return: 多项值的数据 （返回的是字典）
    """
    new_dict = {}
    for key in keys:
        new_dict.update({key: param_value(key)})
    return new_dict


def parm_cookies(**keys):
    """
    传入cookies参数
    :param keys: 传参：WX_COOKIE_OP = ’openId‘
    :return: cookie
    """
    cookies = []
    for key, values in keys.items():
        cookie = {}
        cookie.update({
            'name': key,
            'value': param_value(values)
        })
        cookies.append(cookie)
    return cookies


def get_sql_value(result, name):
    """
    获取数据库查询出来的数据
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

# 获取会员信息  crm.member 金额 member_account 成长值 等级 member_account_upgrade_history  erp_hq member_grade_config   积分
