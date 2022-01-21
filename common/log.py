#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：log.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/26 
"""
import inspect
import logging
import os
import time

base_path = os.path.dirname(os.path.dirname(__file__))
log_path = os.path.join(base_path, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)


class Logger:
    func = None

    def __init__(self):
        self.log_name = os.path.join(log_path, 'uiauto_{}.log'.format(time.strftime('%Y%m%d')))

    def log_config(self, level, message):
        """
        log 配置函数
        :param level: 等级
        :param message: 信息
        :return:
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s {} %(levelname)s: %(message)s'.format(self.get_func()),
                                      datefmt='%Y-%m-%d %H:%M:%S')
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
        """
        获取堆栈深度

        :return:
        """
        # 深度
        depth = len(inspect.stack())-30
        # 封装 传入对应函数 行数
        func = inspect.stack()[depth-2][3]
        if func in ['<module>', 'info', 'warning', 'error']:
            func = ''
        line = inspect.stack()[depth-1][-4]
        filename = inspect.stack()[depth-1][-5].split('\\')[-1]
        self.func = filename + " " + func + " " + str(line)
        return self.func

    def debug(self, message, ):
        self.log_config('debug', message)

    def info(self, message):
        self.log_config('info', message)

    def warning(self, message):
        self.log_config('warning', message)

    def error(self, message):
        self.log_config('error', message)
