#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author:maxiunan
from selenium.webdriver.common.by import By

from base import yaml_handle
from common.custom import request
from common import log
from common.db_mysql import DB_sql
from page import page_base

from time import sleep


logger = log.Logger()


class Register(page_base.Base):
    Element = yaml_handle.element_page(U'注册')

    def __init__(self, browser):
        super(Register, self).__init__(browser)

    def input_name(self, name):
        self.input_text(('xpath', self.Element[U'会员名']), name)

    def input_phone(self, phone_num):
        self.input_text(('xpath', self.Element[U'手机号']), phone_num)

    def get_code(self, code_url, pars):
        try:
            re = request("POST", url=code_url, params=pars)
            # re.raise_for_status()
        except Exception as msg:
            logger.error('{}'.format(msg))
        else:
            if re.json()['msg'] == U'操作成功' and re.json()['success'] is True:
                sleep(0.5)
                sql = "SELECT `CODE` FROM weixin.verification_code where PHONE_NUM = {} ORDER BY SENT_TIME desc LIMIT 1".format(
                    yaml_handle.case_data[u'手机号'])
                result = DB_sql().select_db(sql=sql)
                return result['CODE']
            else:
                logger.info('一分钟内不能再发送 or 发送短信达到阀值')

    def input_code(self, code):
        self.input_text(('xpath', self.Element[u'验证码']), code)

    def choice_station(self, station_name):
        self.click(('xpath', self.Element[U'选择油站']))
        element = self.browser.find_element(By.XPATH, '//div/p[text()={}]'.format('\'' + station_name + '\''))
        try:
            self.browser.execute_script("arguments[0].scrollIntoView();", element)
        except Exception as e:
            logger.info(U'滚动页面失败, {}'.format(e))
        element.click()

    def submit(self):
        self.click(('xpath', self.Element[u'确认提交']))

