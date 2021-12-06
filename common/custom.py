#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：custom.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/26 
"""
import requests


def request(method, url, **kwargs):
    """
    接口请求
    :param method: 请求方式
    :param url: 地址
    :param kwargs: 其他参数
    :return: 请求结果
    """
    if method.upper() == "GET":
        return requests.request(method=method, url=url, **kwargs)
    elif method.upper() == 'POST':
        return requests.request(method=method, url=url, **kwargs)
    else:
        return requests.request(method=method, url=url, **kwargs)


# 暂时放在这里 分割url 得到参数 字典 common中的方法

def get_params(url) -> dict:
    """
    获取url中的参数
    :param url: 地址
    :return: 以字典形式保存的参数
    """
    url_params = url.split("?")[-1].split('&')
    params = {}
    for i in url_params:
        params.update({i.split('=')[0]: i.split('=')[1]})
    return params


def post_params(url, params=None, path="") -> str:
    """
    拼接url中参数
    :param url: 环境
    :param params: 参数
    :param path: 接口路径
    :return: 带有参数的url
    """
    if url[-1] == '/' and path[0] == '/':
        url = url[:-1] + path
    elif url[-1] == '/' or path[0] == '/':
        url = url + path
    else:
        url = url + '/' + path
    if params:
        url = url + "?"
        for i, j in params.items():
            url = url + i + '=' + j + '&'
        return url[:-1]
    else:
        return url


def get_sql_value(result, name) -> str:
    """
    获取sql某一项值
    :param result: sql查询的结果
    :param name: 字段名
    :return: str类型的值
    """
    return str(result[name])
