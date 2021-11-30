import time
from datetime import datetime

import requests


def request(method, url, **kwargs):
    '''
    接口请求
    :param method: 请求方式
    :param url: 地址
    :param kwargs: 其他参数
    :return: 请求结果
    '''
    if method.upper() == "GET":
        return requests.request(method=method, url=url, **kwargs)
    elif method.upper() == 'POST':
        return requests.request(method=method, url=url, **kwargs)
    else:
        return requests.request(method=method, url=url, **kwargs)


# 暂时放在这里 分割url 得到参数 字典 common中的方法

def get_parms(url) -> dict:
    """
    获取url中的参数
    :param url: 地址
    :return: 以字典形式保存的参数
    """
    url_params = url.split("?")[-1].split('&')
    params = {}
    for i in url_params:
        params.update({i.split('=')[0]: i.split('=')[1]})
    return params


def post_parms(url, params=None, path="") -> str:
    """
    拼接url中参数
    :param url: 环境
    :param params: 参数
    :param path: 接口路径
    :return: 带有参数的url
    """
    if url[-1] == '/' and path[0] == '/':
        url = url[:-1] + path
    elif url[-1] == '/' or path[0] == '/':
        url = url + path
    else:
        url = url + '/' + path
    if params:
        url = url + "?"
        for i, j in params.items():
            url = url + i + '=' + j + '&'
        return url[:-1]
    else:
        return url


# url = 'https://wx.test.youzhanguanjia.com'
# # 个人中心验证
# path = 'web/indexV9.2.html?version=V9.2#/centerIndex'
# params = {
#
#     'hqId': '16548',
#     'stationId': '165481003',
#     'hasWXPay': '1',
#     'isMember': '1',
#     'openId': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA'
#
# }

# center_url = 'https://wx.test.youzhanguanjia.com/web/indexV9.2.html?version=V9.2#/centerIndex?openId=o3Uia0XxRtKiO4g-3ryMKI1r4NIA&hqId=16548&stationId=165481005&hasWXPay=1&isMember=1&memberId=123466864'

# print(post_parms(url,params,path))
# 价格100 div恒定4个
# //*[@id="js_dialog_2"]/div[2]/div[1]/div[1]
# 临时封装
def get_key(num):
    weixing_items = {
        1: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[1]/div[1]',
        4: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[1]/div[2]',
        7: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[1]/div[3]',
        '.': '//*[@id="js_dialog_2"]/div[2]/div[2]/div[1]/div[4]',
        2: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[2]/div[1]',
        5: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[2]/div[2]',
        8: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[2]/div[3]',
        0: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[2]/div[4]',
        6: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[3]/div[2]',
        3: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[3]/div[1]',
        9: '//*[@id="js_dialog_2"]/div[2]/div[2]/div[3]/div[3]',
        'del': '//*[@id="js_dialog_2"]/div[2]/div[2]/div[3]/div[4]',
        'sumit': '//*[@id="js_dialog_2"]/div[2]/div[2]/div[4]'
    }
    return str(weixing_items.get(num))


# /html/body/div[2]/div[2]/div[2]/div/div/div[3]
# //*[@id="weui-picker-confirm"]
# 支付订单界面
# toOrderPage?selfPayOrderId=SP1654810011637657711482&orderType=1&openId=o3Uia0XxRtKiO4g-3ryMKI1r4NIA&stationAdminId=1654810000074
# 支付完成
# toPayResultPage?selfPayOrderId=SP1654810011637657711482&hqId=16548&sourceType=1
# /html/body/div/header/p
# 订单金额
# /html/body/div/section/div[1]/div/div/div/div[1]/div[2]/span
# 优惠金额
# //*[@id="totalDiscount"]
# 支付金额
# //*[@id="payAmt2"]

# https://wx.test.youzhanguanjia.com/portal/member/centerIndex?version=V9.2
