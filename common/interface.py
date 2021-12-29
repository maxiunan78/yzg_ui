#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：test 
@File    ：interface.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/28 
"""
import hashlib
import json
import time
from common import custom
from base import yaml_handle


class Openapi:
    def __init__(self, url=yaml_handle.param_value('openapiurl')):
        self.url = url

    def now_time(self):
        conn = custom.request('GET', url=self.url)
        ltime = time.strptime(conn.headers['Date'][5:25], "%d %b %Y %H:%M:%S")
        ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
        now_time = f'{ttime.tm_year:}-{ttime.tm_mon:0>2d}-{ttime.tm_mday:0>2d} ' \
                   f'{ttime.tm_hour:0>2d}:{ttime.tm_min:0>2d}:{ttime.tm_sec:0>2d} '
        return now_time

    @staticmethod
    def open_api_autograph(body: dict):
        keys = []
        if body != {} and 'app_sign' in body.keys():
            for i in body.keys():
                if i == 'app_sign':
                    continue
                keys.append(str(i) + str(body[i]))
            keys.sort()
            keys = "".join(keys)
            app_sign = 'asdfasdf34123'
            sign = app_sign + keys + app_sign
            md5 = hashlib.md5()
            md5.update(str(sign).encode('utf8'))
            body['app_sign'] = md5.hexdigest().upper()
            return json.dumps(body)
        else:
            print('参数错误')

    def discount_calculation(self, fp_no, hq_id, station_id, amount, member_id):
        body = {
            "appId": "10001",
            "app_key": "10001",
            "signMethod": "md5",
            "stationId": station_id,
            "fpNo": fp_no,
            "orderAmount": amount,
            "payTypeId": "2",
            "memberId": member_id,
            "hqId": hq_id,
            "app_sign": "asdfasdf34123",
            "timestamp": "2020-07-01 12:45:00"
        }
        body = self.open_api_autograph(body)
        heads = {
            'Content-Type': 'application/json'
        }
        url = custom.post_params(self.url, path='/openapi/trade/totalDisAmt')
        conn = custom.request('POST', url=url, headers=heads, data=body)
        return conn.json()['content']


class OilServer:
    def __init__(self, url=yaml_handle.param_value('oilserverurl')):
        self.url = url
        self.cookie = self.login()

    def login(self, user='youzhanggui', password='1111111p'):
        url = custom.post_params(self.url, path='/admin/login')
        param = dict(username=user, password=password)
        res = custom.request('POST', url, params=param)
        return res.cookies.get_dict()

    def charge(self, amount, member_id):
        url = custom.post_params(self.url, path='/crm/member/charge')
        param = dict(paidTypeId=1, paidTypeName='现金', oilCardType=0, amount=amount, reAmount=0, memberId=member_id,
                     chargeStationId=165481001)
        header = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        res = custom.request('POST', url=url, params=param, headers=header, cookies=self.cookie)
        return res.status_code == 200 and True or False

    def get_config(self):
        url = custom.post_params(self.url, path='/memberUp/getGrowupConfig')
        res = custom.request('POST', url=url, cookies=self.cookie)
        if res.status_code == 200:
            return res

    def set_config(self, canUseCashCoupon=1, isBalabceDiscount=1, privilegeType=1,
                   specialDiscountType=1, upgradePointCalculateType=0, useGradeOrSpecialDisAmt=2):
        url = custom.post_params(self.url, path='/memberUp/setMemberUpGrade')
        res = self.get_config().json()['data']
        params = dict(

            # 使用余额支付时是否可使用加油代金券 0：不可以; 1：可以
            oldCanUseCashCoupon=res['canUseCashCoupon'],
            canUseCashCoupon=canUseCashCoupon,
            # 享有会员等级优惠的支付方式设置 1:全部 0:余额 -1:非余额
            oldIsBalabceDiscount=res['isBalabceDiscount'],
            isBalabceDiscount=isBalabceDiscount,
            # 会员等级优惠计算方式。0:按加油升数取整后计算会员优惠;1:按加油实际升数计算会员优惠
            oldPrivilegeType=res['privilegeType'],
            privilegeType=privilegeType,
            # 特惠活动优惠的支付方式 1全部.0余额.2非余额
            oldSpecialDiscountType=res['specialDiscountType'],
            specialDiscountType=specialDiscountType,
            # 加油积分,成长值计算方式 0:按加油实收金额计算;1:按加油实际升数计算
            upgradePointCalculateType=upgradePointCalculateType,
            # 优惠券优惠是否可以和会员等级同时享受  1.不可以 2.可以
            oldUseGradeOrSpecialDisAmt=res['useGradeOrSpecialDisAmt'],
            useGradeOrSpecialDisAmt=useGradeOrSpecialDisAmt,

            fastPayUpgrade=1,
            oldFastPayUpgrade=1,
            fastPayPoint=0,
            oldFastPayPoint=0,
            oldChargePoint=2,
            chargePoint=2,
            isSpecialExpress=1,
            oldIsSpecialExpress=1,
            licensePayStatus=1,
            oldLicensePayStatus=1,
            isWithHold=0,
            oldIsWithHold=0,
            gradeId=32299,
            oldGradeId=32299,
            specialExpressMemberId=32299,
            oldSpecialExpressMemberId=32299,
            oldPrivateCarAccessLevel=7309,
            privateCarAccessLevel=7309,
            oldPrivateCarFailLevel=7332,
            privateCarFailLevel=7332,
            downGaredInform=7,
            oldDownGaredInform=7,
            registerConfig=1122220222,
            oldRegisterConfig=1122220222
        )

        header = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        res = custom.request('POST', url=url, params=params, headers=header, cookies=self.cookie)
        return res.status_code == 200 and res or None

    def growup_config(self, orderMinAmount=0, orderUpgradeScale=6,
                      orderUpgradeScaleDoor=10, monthRechargeCount=2, monthRechargeAmount=3, monthAddValue=4,
                      isPlancePay=0):
        """
        成长值 设置
        :return:
        """
        url = custom.post_params(self.url, path='/memberUp/setGrowupConfig')
        pars = dict(
            # 订单应收金额大于 orderMinAmount 元，才计算成长值。
            orderMinAmount=orderMinAmount,
            # 充值金额大于等于 orderUpgradeScale 元时，按照充值金额的 orderUpgradeScaleDoor 倍比例取整后一次性给予成长值
            orderUpgradeScale=orderUpgradeScale, orderUpgradeScaleDoor=orderUpgradeScaleDoor,
            # 单月达到 monthRechargeCount 次，应收金额在  monthRechargeAmount 元 以上的订单时，额外奖励 monthAddValue 点成长值。
            monthRechargeCount=monthRechargeCount, monthRechargeAmount=monthRechargeAmount, monthAddValue=monthAddValue,
            # 用余额支付的订单，不计算成长值。 0.否 1.是
            isPlancePay=isPlancePay)
        header = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        res = custom.request('POST', url=url, params=pars, headers=header, cookies=self.cookie)
        return res.status_code == 200 and res or None
