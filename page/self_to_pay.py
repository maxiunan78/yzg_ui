#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：self_to_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
import time

from base import yaml_handle
from page import page_base
from common import custom


class SelfPay(page_base.Base):
    Element = yaml_handle.element_page(U'自助买单')

    def __init__(self, browser):
        super(SelfPay, self).__init__(browser)

    def fp_choose_num(self, fp_num: int):
        """
        油枪选择
        :param fp_num: 选择几号油枪
        :return: 有油枪返回元素 无返回False
        """
        fp_total = len(self.find_elements(('xpath', self.Element[U'油枪选择'])))
        if 0 < fp_num <= fp_total:
            element = ('xpath', self.Element[U'油枪选择'] + '[{}]'.format(fp_num))
            return element
        else:
            return False

    def amt_keyboard(self, key):
        """
        金额选择
        :param key: 键盘按钮
        :return: 元素
        """
        if self.Element[U'加油金额键盘'].get(str(key), U'键盘无此按钮') != U'键盘无此按钮':
            return 'xpath', self.Element[U'加油金额键盘'].get(str(key), U'键盘无此按钮')
        else:
            return False

    def amt_input(self, num: float) -> list:
        """
        输入的金额进行分割
        :param num: 金额
        :return: 元素列表
        """
        amt = []
        for i in str(num):
            amt.append(self.amt_keyboard(i))
        return amt

    def pay_oil_info(self):
        """
        获取支付成功后油品信息
        :return:
        """
        oil_info = {}
        div = self.find_elements(('xpath', self.Element[U'订单油品信息']))
        for i in range(1, len(div) + 1):
            p1 = self.get_text(('xpath', self.Element[U'订单油品信息'] + f'[{i}]/div[1]'))
            p2 = self.get_text(('xpath', self.Element[U'订单油品信息'] + f'[{i}]/div[2]'))
            oil_info.update({p1: p2})
        return oil_info
