#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：self_to_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
import time

from base import yaml_handle
from page import page_base
from common import custom


class SelfPay(page_base.Base):
    Element = yaml_handle.element_page(u'自助买单')

    def __init__(self):
        super(SelfPay, self).__init__()
        self_pay_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'sourceType', 'openId'),
                                          yaml_handle.param_value('selftopay')
                                          )
        self.open_url(self_pay_url)

    def fp_choose_num(self, fp_num: int):
        """
        油枪选择
        :param fp_num: 选择几号油枪
        :return: 有油枪返回元素 无返回False
        """
        fp_total = len(self.find_elements(('xpath', self.Element[u'油枪选择'])))
        if 0 < fp_num <= fp_total:
            element = ('xpath', self.Element[u'油枪选择'] + '[{}]'.format(fp_num))
            return element
        else:
            return False

    def amt_element(self, key: str) -> str:
        """
        金额选择
        :param key: 键盘输入的按钮
        :return: 返回元素的数据 无元素返回提示
        """
        return self.Element[u'加油金额键盘'].get(key, u'键盘无此按钮')

    def amt_keyboard(self, key):
        if self.amt_element(key) != u'键盘无此按钮':
            return 'xpath', self.amt_element(key)
        else:
            return False

    # def fuelling_confirm(self, num):
    #     """
    #     加油员选择
    #     :param num:
    #     :return:
    #     """
    #     fuelling_items = self.find_elements(('xpath', self.Element[u'加油员列表']))
    #     if 0 < num <= len(fuelling_items):
    #         fuelling_item = ('xpath', self.Element[u'加油员列表'] + '[{}]'.format(num))
    #         print(fuelling_items)
    #         print(fuelling_item)
    #         self.scroll_to(fuelling_item)
    #         return fuelling_item
    #     else:
    #         return False
