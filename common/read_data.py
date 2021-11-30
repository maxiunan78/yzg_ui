#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：read_data.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
import os
import time

import yaml

from common import log
from config import settings

logger = log.Logger()

base_path = os.path.dirname(os.path.dirname(__file__))
data_list = os.path.join(base_path, 'data')


def load_yaml(file):
    with open(file, encoding='UTF_8') as f:
        data = yaml.safe_load(f)
    return data


class Data:
    def __init__(self):
        data_path = os.path.join(data_list, settings.datapath)
        if not os.path.exists(data_path):
            logger.error('无存放数据')
        self.data = load_yaml(data_path)


