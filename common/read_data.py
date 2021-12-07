#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：read_data.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
import os

import yaml

from common import log
from config.config import settings

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
        element_path = os.path.join(data_list, settings.elementpath)
        if not os.path.exists(data_path):
            logger.error(U'无存放数据')
        elif not os.path.exists(element_path):
            logger.error(U'无元素数据')
        self.data = load_yaml(data_path)
        self.element = load_yaml(element_path)



