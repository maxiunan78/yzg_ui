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

from base import yaml_handle, discount_rule
from common import custom,interface
from common.log import Logger
from page.center import Center
from page.self_to_pay import SelfPay

log = Logger()


# 参数化配置
@allure.title(U'微信自助买单')
@allure.feature(U'微信自助买单')
@allure.description(U'测试微信自助买单功能')
@pytest.mark.parametrize('case', [yaml_handle.case_data], ids=[f'FR_NO:{yaml_handle.case_data[U"油枪选择"]}'
                                                               f'AMOUNT:{yaml_handle.case_data[U"金额"]}'])
class TestSelfPay:
    tmp = {}

    @pytest.fixture(scope='class', params=yaml_handle.case_data[U'优惠设置'], autouse=True, ids=[j
                    for i in yaml_handle.case_data[U'优惠设置'] for j in i])
    def hq_config(self, request):
        oil_config = interface.OilServer()
        setting, = request.param.values()
        oil_config.set_config(**setting)
        yield
        oil_config.set_config()

    @pytest.fixture(scope='class')
    def self_pay(self, driver_base):
        # 需要配置
        # 初始化
        self.browser = SelfPay(driver_base)
        self_pay_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'sourceType', 'openId'),
                                          yaml_handle.param_value('selftopay')
                                          )
        self.browser.open_url(self_pay_url)

        return self.browser

    @pytest.fixture(scope='class')
    def center(self,driver_base):
        self.browser = Center(driver_base)
        center_url = custom.post_params(yaml_handle.param_value('url'), path=yaml_handle.param_value('center'))
        self.browser.open_url(center_url)
        self.browser.loading()
        return self.browser


    @allure.story(U'自助买单--创建订单')
    # 参数 作用域 需要重新设置
    def test_self_to_pay(self, self_pay, case):
        with allure.step(U'加油员选择'):
            log.info(U'确认是否存在加油员')
            if self_pay.is_visibility(('xpath', self_pay.Element[U'请选择加油员'])):
                log.info(U'存在加油员')
                self_pay.click(('xpath', self_pay.Element[U'请选择加油员']))
                # fuel_no = self.browser.fuelling_confirm(1)
                # time.sleep(0.5)
                # self.browser.click(fuel_no)
                time.sleep(0.5)
                self_pay.click(('xpath', self_pay.Element[U'确认加油员']))
            else:
                log.info(U'无加油员')
        with allure.step(U'油枪选择'):
            # log.info(U'油枪选择')
            self_pay.click(('xpath', self_pay.Element[U'请选择油枪']))
            # 参数化
            fp_no = self_pay.fp_choose_num(case[U'油枪选择'])
            self_pay.click(fp_no)
            TestSelfPay.tmp[U'油品'] = self_pay.get_text(('xpath', self_pay.Element[U'请选择油枪'])).split(' ')[1]
        with allure.step(U'加油金额'):
            # log.info(U'输入金额')
            self_pay.click(('xpath', self_pay.Element[U'请选择金额']))
            # 参数化
            for num in self_pay.amt_input(case[U'金额']):
                self_pay.click(num)
            self_pay.click(self_pay.amt_keyboard(U'确定'))

        with allure.step(U'跳转'):
            TestSelfPay.tmp[U'订单金额'] = float(self_pay.get_text(('xpath', self_pay.Element[U'请选择金额'])))
            time.sleep(1)

            assert self_pay.page_title() == U'确认订单', log.error(U'跳转失败')

    @allure.story(U'自助买单--订单支付')
    def test_order_pay(self, self_pay, case, member_info):
        with allure.step(U'确认订单信息'):
            order_oil = self_pay.get_text(('xpath', self_pay.Element[U'待支付油品']))
            order_amt = float(self_pay.get_text(('xpath', self_pay.Element[U'支付订单金额'])))
            TestSelfPay.tmp.update({U'订单ID': custom.get_params(self_pay.get_cur_url())['selfPayOrderId']})
            assert TestSelfPay.tmp[U'油品'] == order_oil, log.error(U'油品错误')
            assert TestSelfPay.tmp[U'订单金额'] == order_amt, log.error(U'金额错误')
        with allure.step(U'确认优惠金额'):
            dis_rule = discount_rule.Discount(case[U'油枪选择'], case[U'金额'])
            discount = float(self_pay.get_text(('xpath', self_pay.Element[U'优惠金额'])))
            TestSelfPay.tmp.update({U'优惠金额': discount})
            assert discount == float(dis_rule.total_discount()), log.error(U'优惠金额错误')
            pay_amt = float(self_pay.get_text(('xpath', self_pay.Element[U'待支付金额'])))
            TestSelfPay.tmp.update({U'支付金额': pay_amt})
            assert pay_amt == float(dis_rule.pay_amount()), log.error(U'支付金额错误')
        with allure.step(U'确认支付'):
            self_pay.click(('xpath', self_pay.Element[U'确认支付']))
            time.sleep(1)
            assert self_pay.page_title() == U'付款成功', log.error(U'支付跳转失败')
        with allure.step(U'支付完成'):
            point = dis_rule.get_grade_point(pay_amt)
            TestSelfPay.tmp.update({U'积分': point})
            if member_info['GRADE_TYPE'] != 0:
                upgrade = dis_rule.upgrade_count(pay_amt)
                TestSelfPay.tmp.update({U'成长值': upgrade})
            oil_liter = dis_rule.oil_liters()
            print(oil_liter)
            assert pay_amt == float(self_pay.get_text(('xpath', self_pay.Element[U'支付金额'])))
            assert str(oil_liter)+'升' == self_pay.pay_oil_info()[U'升数']
            print(TestSelfPay.tmp)

