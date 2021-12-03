#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：log.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/26 
"""
import logging
import os
import sys
import time

base_path = os.path.dirname(os.path.dirname(__file__))
log_path = os.path.join(base_path, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)


class Logger:
    func = None

    def __init__(self):
        self.log_name = os.path.join(log_path, '{}.log'.format(time.strftime('%Y%m%d%H%M%S')))

    def log_config(self, level, message):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s {} %(levelname)s:%(message)s'.format(self.get_func()))
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        if level == 'info':
            logger.info(message)
        elif level == 'debug':
            logger.debug(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
        logger.removeHandler(ch)
        logger.removeHandler(fh)

        fh.close()

    def get_func(self):
        # 封装 传入对应函数 行数
        func = sys._getframe(3).f_code.co_name
        if func == '<module>':
            func = ''
        line = sys._getframe(2).f_back.f_lineno
        filename = sys._getframe(3).f_code.co_filename.split('\\')[-1]
        self.func = filename + " " + func + " " + str(line)
        return self.func

    def debug(self, message):
        self.log_config('debug', message)

    def info(self, message):
        self.log_config('info', message)

    def warning(self, message):
        self.log_config('warning', message)

    def error(self, message):
        self.log_config('error', message)
