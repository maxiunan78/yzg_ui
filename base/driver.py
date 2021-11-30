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




