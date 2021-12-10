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


# 参数化配置
@allure.title(U'微信自助买单')
@allure.feature(U'微信自助买单')
@allure.description(U'测试微信自助买单功能')
class TestSelfPay:
    tmp = {}

    @pytest.fixture(scope='class')
    def start(self, driver_base):
        self.browser = SelfPay(driver_base)
        self_pay_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'sourceType', 'openId'),
                                          yaml_handle.param_value('selftopay')
                                          )
        self.browser.open_url(self_pay_url)

        return self.browser

    @allure.story(U'自助买单--创建订单')
    @pytest.mark.parametrize('case', [yaml_handle.case_data])
    def test_self_to_pay(self, start, case):
        with allure.step(U'加油员选择'):
            log.info(U'确认是否存在加油员')
            if start.is_visibility(('xpath', start.Element[U'请选择加油员'])):
                log.info(U'存在加油员')
                start.click(('xpath', start.Element[U'请选择加油员']))
                # fuel_no = self.browser.fuelling_confirm(1)
                # time.sleep(0.5)
                # self.browser.click(fuel_no)
                time.sleep(0.5)
                start.click(('xpath', start.Element[U'确认加油员']))
            else:
                log.info(U'无加油员')
        with allure.step(U'油枪选择'):
            # log.info(U'油枪选择')
            start.click(('xpath', start.Element[U'请选择油枪']))
            # 参数化
            fp_no = start.fp_choose_num(case[U'油枪选择'])
            start.click(fp_no)
            TestSelfPay.tmp[U'油品'] = start.get_text(('xpath', start.Element[U'请选择油枪'])).split(' ')[1]
        with allure.step(U'加油金额'):
            # log.info(U'输入金额')
            start.click(('xpath', start.Element[U'请选择金额']))
            # 参数化
            for num in start.amt_input(case[U'金额']):
                start.click(num)
            start.click(start.amt_keyboard(U'确定'))

        with allure.step(U'跳转'):
            TestSelfPay.tmp[U'订单金额'] = float(start.get_text(('xpath', start.Element[U'请选择金额'])))
            time.sleep(1)

            assert start.page_title() == U'确认订单', log.error(U'跳转失败')

    @allure.story(U'自助买单--订单支付')
    def test_order_pay(self, start):
        with allure.step(U'确认订单信息'):
            order_oil = start.get_text(('xpath', start.Element[U'待支付油品']))
            order_amt = float(start.get_text(('xpath', start.Element[U'待支付订单金额'])))
            assert TestSelfPay.tmp[U'油品'] == order_oil, log.error(U'油品错误')
            assert TestSelfPay.tmp[U'订单金额'] == order_amt, log.error(U'金额错误')
        with allure.step(U'确认优惠金额'):
            discount = float(start.get_text(('xpath', start.Element[U'优惠金额'])))
            pay_amt = float(start.get_text(('xpath', start.Element[U'待支付金额'])))
            assert pay_amt == (order_amt - discount), log.error(U'支付金额错误')
        with allure.step(U'支付'):
            start.click(('xpath', start.Element[U'确认支付']))
            time.sleep(1)
            assert start.page_title() == U'付款成功', log.error(U'支付跳转失败')

    @allure.story(U'自助买单--支付完成')
    def test_payment(self, start):
        with allure.step(U'确认支付'):
            pay = ('xpath', start.Element[U'支付成功'])
            log.info(start.get_cur_url())
            TestSelfPay.tmp.update(custom.get_params(start.get_cur_url()))
            assert start.is_visibility(pay) and start.get_text(pay) == U'支付成功', log.error(U'支付失败')
        with allure.step(U'确认油品信息'):
            # 油枪单价
            TestSelfPay.tmp.update(start.pay_oil_info())
            print(TestSelfPay.tmp)
