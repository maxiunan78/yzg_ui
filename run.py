#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：run.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/26 
"""
import argparse
import os
import time

import pytest

def par_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('-e', '--environment', type=str, default='test')
    parse.add_argument('-p', '--path', type=str, default='./testcase/test_self_pay.py')
    parse.add_argument('-w', '--work', type=str, default='./result')
    return parse.parse_args()

def run():
    parse = par_args()
    os.environ['ENV_FOR_DYNACONF'] =parse.environment
    pytest.main(['-v', '-q', '-s', parse.path, r'--alluredir={}\result\allure-results'.format(parse.work)])

if __name__ == '__main__':
     run()

