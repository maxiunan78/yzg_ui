#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：test
@File    ：center.py
@Author  ：musong
@Date    ：2021/11/24 13:58
"""

import time
import db_mysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db = db_mysql.DB_sql(host="47.97.35.19",
                     port=3306,
                     user="root",
                     password="rain1q2w3e4r5t")

UA = 'Mozilla/5.0 (Linux; Android 7.1.1; Nexus 6 Build/N6F26U) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/75.0.3770.142 Mobile Safari/537.36 wechatdevtools/1.05.2110290 MicroMessenger/8.0.5 ' \
     'webview/1637315156379193 webdebugger port/38472 token/d69dbe30a7e48dbb306c0a9f6d8f821e '
# Chrome 浏览器大小，代理，隐形等待 设置
width = 400
hight = 830
mobile = 3.0
mobileopion = {
    'deviceMetrics': {
        'width': width,
        "hight": hight,
        "pixelRatio": mobile,

    }
}
options = webdriver.ChromeOptions()
options.add_experimental_option('mobileEmulation', mobileopion)
options.add_argument('user-agent={}'.format(UA))
options.add_argument('start-maximized')
chrome = webdriver.Chrome(options=options)
# chrome.set_window_size(width, hight)

chrome.implicitly_wait(5)

# 设置为手机浏览器模式
elment = chrome.find_element(By.TAG_NAME, 'body')
elment.send_keys(Keys.F12)
elment.send_keys(Keys.CLEAR, Keys.SHIFT, 'm')
# 保存cookies  微信id 站点 会员号 参数
cookies_info = [{
    'domain': 'wx.test.youzhanguanjia.com',
    'name': 'WX_COOKIE_OP',
    'value': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA'
}, {
    'domain': 'wx.test.youzhanguanjia.com',
    'name': 'WX_COOKIE_ME',
    'value': '123466864'
}, {
    'domain': 'wx.test.youzhanguanjia.com',
    'name': 'WX_COOKIE_HQ',
    'value': '16548'
},
    # {
    #     'domain': 'wx.test.youzhanguanjia.com',
    #     'name': 'openId',
    #     'value': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA'
    # },
    # {
    #     'domain': 'wx.test.youzhanguanjia.com',
    #     'name': 'token',
    #     'value': 'WX_00119a53edc34a31b74c6431c0b3df92'
    # },

]

url = 'https://wx.test.youzhanguanjia.com'
# 个人中心验证
path = 'web/indexV9.2.html?version=V9.2#/centerIndex'
# new_path = '/portal/member/centerIndex?version=V9.2'
params = {

    'hqId': '16548',
    'stationId': '165481005',
    'hasWXPay': '1',
    'isMember': '1',
    'openId': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA',
    'memberId': '123466864'

}
# center_url = 'https://wx.test.youzhanguanjia.com/web/indexV9.2.html?version=V9.2#/centerIndex?openId=o3Uia0XxRtKiO4g' \
#              '-3ryMKI1r4NIA&hqId=16548&stationId=165481005&hasWXPay=1&isMember=1&memberId=123466864 '

center_url = request.post_parms(url, params, path)

print(center_url)
chrome.delete_all_cookies()
chrome.get(url)
time.sleep(0.5)
for cookie in cookies_info:
    chrome.add_cookie(cookie)

chrome.get(center_url)


time.sleep(2)
chrome.quit()