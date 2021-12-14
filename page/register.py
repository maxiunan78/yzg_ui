#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author:maxiunan

from base import yaml_handle
from common.custom import request
from common import log
from page import page_base
import re
import time
from base import driver
from common import custom

logger = log.Logger()

class Register(page_base.Base):
    Element = yaml_handle.element_page(U'注册')

    def __init__(self, browser):
        super(Register, self).__init__(browser)

    def input_name(self, name):
        self.input_text(('xpath', self.Element[U'会员名']), name)

    def input_phone(self, phoneNum):
        self.input_text(('xpath', self.Element[U'手机号']), phoneNum)

    def input_code(self, code_url, pars):
        try:
            re = request("POST", url=code_url, params=pars)
            # re.raise_for_status()
        except Exception as msg:
            logger.error('{}'.format(msg))
        else:
            if re.json()['msg'] == U'操作成功' and re.json()['success'] is True:
                time.sleep(0.5)
            else:logger.info('一分钟内')

    def choice_station(self,stationName):
        self.click(('xpath', self.Element[U'选择油站']))
        self.scroll_to(("xpath",'//div/p[text()={}]'.format(stationName)))
        self.click(("xpath",'//div/p[text()={}]'.format(stationName)))

# if __name__ == "__main__":
#     ch = driver.chrome()
#     r = Register(ch)
#     print(r.Element)
