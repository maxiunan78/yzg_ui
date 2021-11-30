#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：page_base.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
from base import driver
from common.params_handle import Params


class Base:
    def __init__(self):
        self.browser = driver.Driver()
        self.browser.implicitly_wait(5)
        self.browser.switch_phone()
        self.browser.max()
        self.browser.open_url(Params.URL)

    def get_browser(self):
        return self.browser

