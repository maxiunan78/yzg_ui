#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author:maxiunan

import time

import allure
import pytest

from yzg_ui.base import yaml_handle
from yzg_ui.common import custom
from yzg_ui.common.log import Logger
from yzg_ui.page.register import Register
from yzg_ui.common.db_mysql import DB_sql
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
        sql ="SELECT * FROM crm.member WHERE phone_num={} and status=1 and MEMBER_TYPE=1".format(case[u'手机号'])
        print(sql)
        result = DB_sql().select_db(sql=sql)
        with allure.step(U'检查是否注册'):
            if (result is not None):
                # start.get_browser().execute_script("alert('已经注册了！');")
                log.info("已经注册了！不再继续执行")
                assert "已经注册了！不再继续执行"

        with allure.step(U'填入必填项，会员名、手机号、验证码'):
            start.input_name(case[u'会员名'])
            start.input_phone(case[u'手机号'])
            start.input_code(code_url=yaml_handle.param_value('code_url'),pars=yaml_handle.param_value('pars'))

        with allure.step(u'选择站点'):
            pars = yaml_handle.param_value('pars')
            sql = "SELECT station_name FROM erp_station.station WHERE STATION_ID={}".format(pars['stationId'])
            result = DB_sql().select_db(sql=sql)
            start.choice_station(result['station_name'])


if __name__ == "__main__":
    pytest.main(['test_register.py'])