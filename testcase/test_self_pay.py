#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：test_self_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/1 
"""
import time

from common.log import Logger
from page.self_to_pay import SelfPay

log = Logger()


class TestSelfPay:
    def setup_class(self):
        self.browser = SelfPay()

    def teardown_class(self):
        self.browser.quit()

    def test_self_to_pay(self):
        log.info(u"确认是否存在加油员")
        if self.browser.is_visibility(('xpath', self.browser.Element[u'请选择加油员'])):
            log.info(u"存在加油员")
            self.browser.click(('xpath', self.browser.Element[u'请选择加油员']))
            # fuel_no = self.browser.fuelling_confirm(1)
            # time.sleep(0.5)
            # self.browser.click(fuel_no)
            time.sleep(0.5)
            self.browser.click(('xpath', self.browser.Element[u'确认加油员']))
        else:
            log.info(u"无加油员")
        log.info(u"油枪选择")
        self.browser.click(('xpath', self.browser.Element[u'请选择油枪']))
        fp_no = self.browser.fp_choose_num(1)
        self.browser.click(fp_no)
        log.info(u'输入金额')
        self.browser.click(('xpath', self.browser.Element[u'请选择金额']))
        self.browser.click(self.browser.amt_keyboard('5'))
        self.browser.click(self.browser.amt_keyboard('5'))
        self.browser.click(self.browser.amt_keyboard(u'确定'))
        time.sleep(1)
        assert self.browser.page_title() == u'确认订单', log.error(u'创建订单失败')




