#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：self_to_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
from page import page_base
from common import custom
from common.params_handle import Params


class SelfPay(page_base.Base):
    def __init__(self):
        super(SelfPay, self).__init__()
        self_pay_url = custom.post_params(Params.URL, Params.SELF_PAY_PARAMS, Params.SELF_PAY)
        self.open_url(self_pay_url)

