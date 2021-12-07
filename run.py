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

os.environ['ENV_FOR_DYNACONF'] = 'test'

if __name__ == '__main__':
    pytest.main(['-v', '-q', '-s',  '--alluredir=./result/{}'.format('json')])
