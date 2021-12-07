#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：page_base.py
@Author  ：穆崧
@Date    ：创建时间：2021/11/29 
"""
import os
import time

import allure
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from common import log


def element_locator(locator_items: tuple) -> tuple:
    """
    元素定位方式
    :param locator_items: 元素
    :return: 元素类型和元素的元组
    """
    locator_type, element = locator_items
    if locator_type.lower() == 'xpath':
        return By.XPATH, element
    elif locator_type.lower() == 'tag_name':
        return By.TAG_NAME, element


logger = log.Logger()
base_path = os.path.dirname(os.path.dirname(__file__))
screenshot_path = os.path.join(base_path, 'screenshot')
if not os.path.exists(screenshot_path):
    os.mkdir(screenshot_path)


class Base(object):
    def __init__(self, browser):
        self.browser = browser
        self.implicitly_wait(5)
        self.max()
        self.switch_phone()

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
            logger.error("Error:{}".format(msg))

    def find_element(self, locator, timeout=5):
        """
        查找唯一元素
        :param locator: 元素
        :param timeout: 查询时间
        :return: 元素 或 错误
        """
        try:
            self.explicit_wait(timeout, 0.5) \
                .until(EC.visibility_of_element_located(element_locator(locator)))
            by, value = element_locator(locator)
            element = self.browser.find_element(by, value)
            return element
        except Exception as msg:
            logger.error(U'页面元素不存在或不可见, {}'.format(msg), 5)

    def find_elements(self, locator, timeout=5):
        """
        查找元素列表

        :param locator: 元素
        :param timeout: 查询时间
        :return: 元素 或 错误
        """
        try:
            self.explicit_wait(timeout, 0.5) \
                .until(EC.visibility_of_all_elements_located(element_locator(locator)))
            by, value = element_locator(locator)
            elements = self.browser.find_elements(by, value)
            return elements
        except Exception as msg:
            logger.error(U'页面元素不存在或不可见, {}'.format(msg), 5)

    def is_visibility(self, locator) -> bool:
        """
        判断元素是否可见
        :param locator: 元素
        :return:
        """
        by, value = element_locator(locator)
        return self.browser.find_element(by, value).is_displayed()

    def click(self, locator):
        """
        点击元素
        :param locator: 元素

        """
        element = self.find_element(locator)
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

    def send_keys(self, locator, *kwargs):
        """
        键盘中按键
        :param locator: 元素属性
        :param kwargs:
        :return:
        """

        self.find_element(locator).send_keys(*kwargs)

    def input_text(self, locator, text):
        """
        对输入框进行输入
        :param locator: 元素

        :param text: 输入的文本
        :return:
        """
        self.find_element(locator).clear()
        self.find_element(locator).send_keys(text)

    def switch_phone(self):
        """
        切换成手机浏览器模式
        """
        self.send_keys(('tag_name', 'body'), Keys.F12)
        self.send_keys(('tag_name', 'body'), Keys.CLEAR, Keys.SHIFT, 'm')

    def implicitly_wait(self, timeout=5):
        """
        隐形等待
        :param timeout: 等待时间
        """
        self.browser.implicitly_wait(timeout)

    def get_cur_url(self) -> str:
        """
        获取当前的url
        :return: url
        """
        return self.browser.current_url

    def get_text(self, locator) -> str:
        """
        获取文本
        :param locator: 元素
        :return: 文本
        """
        return self.find_element(locator).text

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

    def refresh(self):
        """
        刷新
        """
        self.browser.refresh()

    def scroll_to(self, locator):
        """
        滚动到指定元素可见位置
        :param locator: 元素
        """
        try:
            element = self.find_element(locator)
            self.browser.execute_script("arguments[0].scrollIntoView();", element)
        except Exception as msg:
            logger.error(U'滚动页面失败, {}'.format(msg), 5)

    def page_title(self) -> str:
        """
        获取网页标题
        :return: 网页标题
        """
        return self.browser.title

    def get_screenshot(self, name=""):
        try:
            file_name = os.path.join(screenshot_path, '{}.png'.format(name + str(time.strftime('%Y%m%d%H%M%S'))))
            self.browser.get_screenshot_as_file(file_name)
            time.sleep(0.5)
            return file_name
        except Exception as e:
            logger.error(U'截图失败, {}'.format(e), 5)

    def fail_picture(self, name=''):
        f = self.get_screenshot(name)
        filename = f.split('\\')[-1]
        allure.attach.file(f, U'失败用例截图:{}'.format(filename), allure.attachment_type.PNG)
        time.sleep(0.5)
