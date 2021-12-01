#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：self_to_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
from base import yaml_handle
from page import page_base
from common import custom


class SelfPay(page_base.Base):
    Element = yaml_handle.element_page('self_to_pay')

    def __init__(self):
        super(SelfPay, self).__init__()
        self_pay_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'sourceType', 'openId'),
                                          yaml_handle.param_value('selftopay')
                                          )
        self.open_url(self_pay_url)


