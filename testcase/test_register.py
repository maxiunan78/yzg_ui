#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author:maxiunan

import time

import allure
import pytest

from base import yaml_handle
from common import custom
from common.log import Logger
from page.register import Register
from common.db_mysql import DB_sql
from time import sleep

log = Logger()


# 参数化配置
@allure.title(U'注册')
@allure.feature(U'注册')
@allure.description(U'测试注册功能')
class TestRegister:
    tmp = {}

    @pytest.fixture(scope='class')
    def start(self, driver_base):
        self.browser = Register(driver_base)
        register_url = custom.post_params(yaml_handle.param_value('url'),
                                          yaml_handle.param_dict('stationId', 'hqId', 'openId'),
                                          yaml_handle.param_value('memberregister')
                                          )
        self.browser.open_url(register_url)

        return self.browser

    @allure.story(U'注册')
    @pytest.mark.parametrize('case', [yaml_handle.case_data])
    def test_register(self, start, case):
        sql = "SELECT * FROM crm.member WHERE phone_num={} and status=1 and MEMBER_TYPE=1".format(case[u'手机号'])
        print(sql)
        result = DB_sql().select_db(sql=sql)
        with allure.step(U'检查是否注册'):
            assert result is None, log.info("已经注册了！不再继续执行注册用例")

        with allure.step(U'填入必填项，会员名、手机号、验证码'):
            start.input_name(case[u'会员名'])
            start.input_phone(case[u'手机号'])
            dict1 = yaml_handle.param_dict('stationId', 'hqId')
            dict1.update({'phoneNum': case[u'手机号']})
            print(dict1)
            code = start.get_code(code_url=yaml_handle.param_value('code_url'), pars=dict1)
            assert code is not None, log.info("发送短信失败")
            start.input_code(code)
            # assert start.find_element(('xpath',start.Element[u'验证码输入框'])).get_attribute("data-index") == code

        with allure.step(u'选择站点'):
            pars = yaml_handle.param_value('pars')
            sql = "SELECT station_name FROM erp_station.station WHERE STATION_ID={}".format(
                yaml_handle.param_value('stationId'))
            result = DB_sql().select_db(sql=sql)
            start.choice_station(result['station_name'])

        with allure.step(u'确认提交'):
            start.submit()
            sleep(0.5)
            sql = "select * from  crm.member  where PHONE_NUM = '{}' and `STATUS` = 1 and MEMBER_TYPE=1 and station_id={} order by created_time DESC LIMIT 1 " \
                .format(case[u'手机号'], yaml_handle.param_value('stationId'))
            result = DB_sql().select_db(sql=sql)
            # 等待0.0秒后数据库里面没有短信，再次等待1秒钟再进行断言
            if result is None:
                sleep(1)
                result = DB_sql().select_db(sql=sql)
            assert result is not None, log.info("注册失败")


if __name__ == "__main__":
    pytest.main(['test_register.py'])
