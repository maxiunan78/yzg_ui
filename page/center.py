#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：center.py
@Author  ：穆崧
@Date    ：创建时间：2022/1/5 
"""
import time

from base import yaml_handle
from page import page_base


class Record(page_base.Base):
    Element = yaml_handle.element_page(U'消费记录')

    def __init__(self, browser):
        super(Record, self).__init__(browser)


class Center(page_base.Base):
    Element = yaml_handle.element_page(U'个人中心')

    def __init__(self, browser):
        super(Center, self).__init__(browser)

    def consume_record(self):
        self.click(('xpath', self.Element[U'消费记录']))
        return Record(self.browser)

    def loading(self):
        i = 0
        while self.is_visibility(('xpath', self.Element['数据加载'])):
            time.sleep(1)
            if i == 6:
                page_base.logger.info('超时')
                break
            i = i + 1

