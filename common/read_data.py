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


def dump_yaml(data, file):
    with open(file, "w+", encoding='UTF_8') as f:
        yaml.safe_dump(data, f)
    return file


class Data:
    def __init__(self):
        data_path = os.path.join(data_list, settings.datapath)
        element_path = os.path.join(data_list, settings.elementpath)
        case_path = os.path.join(data_list, settings.casedatapath)
        if not(os.path.exists(data_path) or os.path.exists(element_path) or os.path.exists(case_path)):
            logger.error(U'无存放数据')
        self.data = load_yaml(data_path)
        self.element = load_yaml(element_path)
        self.case = load_yaml(case_path)

    def write_data(self, data, filename):
        """
        保存所需要的数据
        :param data: 数据
        :param filename:文件名
        :return: 读取 写入的数据的yaml
        """
        file = os.path.join(data_list, filename+'.yaml')
        dump_yaml(data, file)
        if not os.path.exists(file):
            logger.error(U'创建文件失败')
        self.data = load_yaml(file)
        return self.data


