#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：test_self_pay.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/1 
"""
import time

import allure
import pytest

from base import yaml_handle
from common import custom
from common.log import Logger
from page.self_to_pay import SelfPay

log = Logger()


@allure.title(u'微信自助买单')
@allure.feature(u'微信自助买单')
@allure.description(u'测试微信自助买单功能')
class TestSelfPay:
    @pytest.fixture(scope='class')
    def start(self, driver_base):
        self.browser = SelfPay(driver_base)
        self_pay_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'sourceType', 'openId'),
                                          yaml_handle.param_value('selftopay')
                                          )
        self.browser.open_url(self_pay_url)
        return self.browser

    @allure.story(u'自助买单页--创建订单')
    def test_self_to_pay(self, start):

        with allure.step(u'加油员选择'):
            log.info(u"确认是否存在加油员")
            if start.is_visibility(('xpath', start.Element[u'请选择加油员'])):
                log.info(u"存在加油员")
                start.click(('xpath', start.Element[u'请选择加油员']))
                # fuel_no = self.browser.fuelling_confirm(1)
                # time.sleep(0.5)
                # self.browser.click(fuel_no)
                time.sleep(0.5)
                start.click(('xpath', start.Element[u'确认加油员']))
            else:
                log.info(u"无加油员")
        with allure.step(u'油枪选择'):
            log.info(u"油枪选择")
            start.click(('xpath', start.Element[u'请选择油枪']))
            fp_no = start.fp_choose_num(1)
            start.click(fp_no)
        with allure.step(u'加油金额'):
            log.info(u'输入金额')
            start.click(('xpath', start.Element[u'请选择金额']))
            start.click(start.amt_keyboard('5'))
            start.click(start.amt_keyboard('9'))
            start.click(start.amt_keyboard(u'确定'))

        time.sleep(1)
        assert start.page_title() == u'确认订单', log.error(u'创建订单失败')

