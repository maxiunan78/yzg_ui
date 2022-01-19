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

url = ' https://wx.test.youzhanguanjia.com/'
self_pay_path = '/portal/selfPay/toSelfPay'
self_pay_params = {
    # 'appId': 'wx09ab3b9fb3c778aa',
    'hqId': '16548',
    'stationId': '165481041',
    'sourceType': '1',
    'openId': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA'

}
self_pay_url = request.post_parms(url, self_pay_params, self_pay_path)
print(self_pay_url)
chrome.get(self_pay_url)
WebDriverWait(chrome.get(self_pay_url), 2, 0.5)
time.sleep(0.5)

# 油枪选择 1号 需要封装
# 点击元素 需要加入显性等待


print('油枪选择')  # log
WebDriverWait(chrome, 2, 0.5).until(
    EC.visibility_of_element_located((By.XPATH, '//*[@id="fpOrPr"]')))
chrome.find_element(By.XPATH, '//*[@id="fpOrPr"]').click()
WebDriverWait(chrome, 2, 0.5).until(
    EC.visibility_of_element_located((By.XPATH, '//*[@id="js_dialog_1"]/div[2]/div/div[1]')))
chrome.find_element(By.XPATH, '//*[@id="js_dialog_1"]/div[2]/div/div[1]').click()

# 输入金额并确认 需要封装组合
print('输入金额')  # log
chrome.find_element(By.XPATH, '//*[@id="fuelOrderAmt"]').click()
chrome.find_element(By.XPATH, request.get_key(5)).click()
# chrome.find_element(By.XPATH, request.get_key('.')).click()
# chrome.find_element(By.XPATH, request.get_key(0)).click()
chrome.find_element(By.XPATH, request.get_key(5)).click()

# 选择加油员 需要考虑滚动和确认问题 无加油员情况

# chrome.find_element(By.XPATH, '//*[@id="fuelAdmin"]').click()

# if chrome.find_element(By.XPATH, '//*[@id="weui-picker-confirm"]').is_displayed():
#     chrome.find_element(By.XPATH, '//*[@id="weui-picker-confirm"]').click()
# else:
#     time.sleep(0.5)
#     chrome.find_element(By.XPATH, '//*[@id="weui-picker-confirm"]').click()
#
# chrome.find_element(By.XPATH, request.get_key('sumit')).click()
print('选择加油员')
if chrome.find_element(By.XPATH, '//*[@id="fuellingAdmin"]').is_displayed():
    print(U'有加油员')
    try:
        # /html/body/div[2]/div[2]/div[2]/div/div/div[3]
        chrome.find_element(By.XPATH, '//*[@id="fuellingAdmin"]').click()
        time.sleep(0.5)
        WebDriverWait(chrome, 2, 0.5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="weui-picker-confirm"]')))
        chrome.find_element(By.XPATH, '//*[@id="weui-picker-confirm"]').click()

        # 滚动与显示的元素
        # target = chrome.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div/div/div[3]/div[2]')
        #
        # WebDriverWait(chrome, 2, 0.5).until(
        #     EC.visibility_of_element_located((By.XPATH, target)))
        # chrome.execute_script("arguments[0].scrollIntoView();", target)
        # target.click()

        print(U'选择加油员成功')
    except RuntimeError:
        print(U'选择加油员失败')
else:
    print(U'无加油员')
WebDriverWait(chrome, 2, 0.5).until(EC.visibility_of_element_located((By.XPATH, request.get_key('sumit'))))
chrome.find_element(By.XPATH, request.get_key('sumit')).click()

# 需要考虑取优惠券的情况

# 抓取加油优惠金额 和 订单金额 待支付金额
print('计算金额')  # log
receivable_amount = float(
    chrome.find_element(By.XPATH, '/html/body/div/section/div[1]/div/div/div/div[1]/div[2]/span').text)
discount_amount = float(chrome.find_element(By.XPATH, '//*[@id="totalDiscount"]').text)
pay_amount = float(chrome.find_element(By.XPATH, '//*[@id="payAmt2"]').text)
if receivable_amount == discount_amount + pay_amount:
    print(U'支付金额正确')
else:
    print(U'支付金额错误')
time.sleep(0.5)
# 点击支付
chrome.find_element(By.XPATH, '/html/body/div/footer/div/div[2]/span').click()
time.sleep(2)
# 支付完成后需要 获取订单号  封装数据库查询  和页面信息的文本进行对应
# 订单号 需要保存

selfPayOrderId = request.get_parms(chrome.current_url)['selfPayOrderId']
sql = "select table_name from data_dict.self_table_config  where FIND_IN_SET('16548',hq_ids)"
c = db.select_db(sql)
sql2 = "SELECT * FROM trade.2021_{} where ORDER_ID ='{}'".format(str(c['table_name']),
                                                                 str(selfPayOrderId))
d = db.select_db(sql2)
pay_result = db.get_sql_value(d, 'PAY_STATUS')
pay_time = db.get_sql_value(d, 'PAY_TIME')
# assert d[0]['PAY_STATUS'] == 1, '支付失败'
# 获取页面成功的元素的文本
success = chrome.find_element(By.XPATH, '/html/body/div/header/p').text

if pay_result == '1' and success == U'支付成功':
    print('支付成功')
else:
    print('支付失败')
time.sleep(2)
# 个人中心验证 center_url = 'https://wx.test.youzhanguanjia.com/web/indexV9.2.html?version=V9.2#/centerIndex?openId
# =o3Uia0XxRtKiO4g-3ryMKI1r4NIA&hqId=16548&stationId=165481005&hasWXPay=1&isMember=1&memberId=123466864' #
# chrome.get(center_url) for cookie in token_cookie: chrome.add_cookie(cookie)
#
# chrome.get(center_url)
# time.sleep(2)
# 消费记录进行验证
i = 0
while i < 10:
    ref_order_id = db.get_sql_value(db.select_db(sql2), 'REF_FUELLING_ORDER_ID')
    if ref_order_id != "None":
        print('数据库已匹配')
        break
    else:
        time.sleep(5)
    i += 1
expense_record_path = '/web/indexV9.2.html?version=V9.2#/expenseRecord'
expense_record_params = {

    'hqId': '16548',
    'memberId': '123466864',

}

# 跳转消费记录页
expense_record_url = request.post_parms(url, expense_record_params, expense_record_path)
chrome.get(expense_record_url)
time.sleep(0.5)
# //*[@id="expenseRecord"]/div[1]/div/div/div[2]/div/ul/li[1]/div/div[1]/p[1]
# 验证页面是否存在对应的时间
record_pay_time = chrome.find_element(By.XPATH,'//*[@id="expenseRecord"]/div[1]/div/div/div[2]/div/ul/li[1]/div/div[1]/p[1]')
if pay_time == record_pay_time.text:
    print('页面已匹配,加油订单已生成')

record_pay_time.click()
time.sleep(0.5)
# 将消费记录的各项值 保存并对比
div = chrome.find_elements(By.XPATH, '//*[@id="oilExpenseDetail"]/div[2]/div')
ele_dict = {}

for i in range(1, len(div) + 1):
    li = chrome.find_elements(By.XPATH, ('//*[@id="oilExpenseDetail"]/div[2]/div[{}]/ul/li').format(i))
    for j in range(1, len(li) + 1):
        p1 = chrome.find_element(By.XPATH, ('//*[@id="oilExpenseDetail"]/div[2]/div[{}]/ul/li[{}]/p[1]').format(i, j))
        p2 = chrome.find_element(By.XPATH, ('//*[@id="oilExpenseDetail"]/div[2]/div[{}]/ul/li[{}]/p[2]').format(i, j))
        ele_dict.update({p1.text: p2.text})
print(ele_dict)

chrome.quit()
