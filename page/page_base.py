#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：WX_youguanjia 
@File    ：page_base.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from base import driver, yaml_handle


class Base(object):
    def __init__(self, browser=driver.chrome()):
        self.browser = browser

        self.implicitly_wait(5)
        self.switch_phone()
        self.max()
        # self.open_url(yaml_handle.param_value('url'))

    def get_browser(self):
        return self.browser

    def explicit_wait(self, timeout, poll_frequency=0.5):
        """
        显性等待
        :param timeout: 等待时间
        :param poll_frequency: 间隔查询时间
        :return: driver
        """
        return WebDriverWait(self.browser, timeout, poll_frequency)

    def open_url(self, url, timeout=5):
        """
        打开网站
        :param timeout: 超时时间
        :param url: 网站

        """
        self.browser.get(url)
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
        return self.browser.find_element(self.element_locator(locator_type, element)).is_displayed()

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
        self.browser.maximize_window()

    def min(self):
        """
        最小化窗口

        """
        self.browser.minimize_window()

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
        self.browser.implicitly_wait(timeout)

    def get_cur_url(self):
        """
        获取当前的url
        :return: url
        """
        return self.browser.current_url

    def get_text(self, locator_type, element):
        """
        获取文本
        :param locator_type: 元素类型
        :param element: 元素
        :return: 文本
        """
        return self.find_element(locator_type, element).text

    def quit(self):
        """
        关闭浏览器
        """
        self.browser.quit()

    def back(self):
        """
        返回
        """
        self.browser.back()

    def forward(self):
        """
        前进
        """
        self.browser.forward()
