#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：run.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/26 
"""

import os
import time

import pytest


if __name__ == '__main__':
    os.environ['ENV_FOR_DYNACONF'] = 'test'
    pytest.main(['-v', '-q', '-s', '/testcase/test_self_pay.py', '--alluredir=./result/{}'.format('json')])
