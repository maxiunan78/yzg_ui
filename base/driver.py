#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：driver.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/24 
"""
import os
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

# 手机模式参数 需要放入配置
UA = settings.UA
# Chrome 浏览器大小，代理，隐形等待 设置

mobileopion = settings.mobileopion


# options = webdriver.ChromeOptions()
# options.add_experimental_option('mobileEmulation', mobileopion)
# options.add_argument('user-agent={}'.format(UA))
# chrome = webdriver.Chrome(options=options)
# # chrome.set_window_size(width, hight)
# chrome.maximize_window()
# chrome.implicitly_wait(5)

# 设置为手机浏览器模式  快捷键
# elment = chrome.find_element(By.TAG_NAME, 'body')
# elment.send_keys(Keys.F12)
# elment.send_keys(Keys.CLEAR, Keys.SHIFT, 'm')
def chrome(option=True):
    if option:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('mobileEmulation', mobileopion)
        options.add_argument('user-agent={}'.format(UA))
        driver = webdriver.Chrome(options=options)
        return driver
    else:
        driver = webdriver.Chrome()
        return driver


class Driver:
    def __init__(self, option=True):
        self.driver = chrome(option)

    def explicit_wait(self, timeout, poll_frequency=0.5):
        """
        显性等待
        :param timeout: 等待时间
        :param poll_frequency: 间隔查询时间
        :return: driver
        """
        return WebDriverWait(self.driver, timeout, poll_frequency)

    def open_url(self, url, timeout=5):
        """
        打开网站
        :param timeout: 超时时间
        :param url: 网站

        """
        self.driver.get(url)
        try:
            self.explicit_wait(timeout, 0.5)
        except Exception as msg:
            print("Error:{}".format(msg))

    def element_locator(self, locator_type, element) -> tuple:
        """
        元素定位方式
        :param locator_type: 元素类型
        :param element: 元素
        :return: 元素类型和元素的元组
        """
        if locator_type.lower() == 'xpath':
            return By.XPATH, element
        elif locator_type.lower() == 'tag_name':
            return By.TAG_NAME, element

    def find_element(self, locator_type, element, timeout=5):
        """
        查找唯一元素
        :param locator_type: 元素类型
        :param element: 元素
        :param timeout: 查询时间
        :return: 元素 或 错误
        """
        try:
            element = self.explicit_wait(timeout, 0.5) \
                .until(EC.visibility_of_element_located(self.element_locator(locator_type, element)))
            return element
        except:
            print(u'页面元素不存在或不可见')

    def find_elements(self, locator_type, element, timeout=5):
        """
        查找元素列表
        :param locator_type: 元素类型
        :param element: 元素
        :param timeout: 查询时间
        :return: 元素 或 错误
        """
        try:
            elements = self.explicit_wait(timeout, 0.5) \
                .until(EC.visibility_of_all_elements_located(self.element_locator(locator_type, element)))
            return elements
        except:
            print(u'页面元素不存在或不可见')

    def is_visibility(self, locator_type, element) -> bool:
        """
        判断元素是否可见
        :param locator_type:
        :param element:
        :return:
        """
        return self.driver.find_element(self.element_locator(locator_type, element)).is_displayed()

    def click(self, locator_type, element):
        """
        点击元素
        :param locator_type: 元素类型
        :param element: 元素
        """
        element = self.find_element(locator_type, element)
        element.click()

    def max(self):
        """
        最大化窗口
        """
        self.driver.maximize_window()

    def min(self):
        """
        最小化窗口

        """
        self.driver.minimize_window()

    def send_keys(self, locator_type, element, *kwargs):
        """
        键盘中按键或对输入框进行输入
        :param locator_type: 元素类型
        :param element: 元素
        :param kwargs:
        :return:
        """
        self.find_element(locator_type, element).send_keys(*kwargs)

    def switch_phone(self):
        """
        切换成手机浏览器模式
        """
        self.send_keys('tag_name', 'body', Keys.F12)
        self.send_keys('tag_name', 'body', Keys.CLEAR, Keys.SHIFT, 'm')

    def implicitly_wait(self, timeout=5):
        """
        隐形等待
        :param timeout: 等待时间

        """
        self.driver.implicitly_wait(timeout)

    def get_cur_url(self):
        """
        获取当前的url
        :return: url
        """
        return self.driver.current_url
