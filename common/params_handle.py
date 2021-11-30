#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：params_handle.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
from common.read_data import Data


# 封装成方法
class Params(object):
    # 环境
    URL = Data().data['url']
    # get的接口地址
    SELF_PAY = Data().data['selftopay']
    # 参数
    SELF_PAY_PARAMS = {
        'hqId': Data().data['hqid'],
        'stationId': Data().data['stationid'],
        'sourceType': '1',
        'openId': Data().data['openid']
    }
    # cookies
