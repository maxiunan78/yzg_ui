import time
import db_mysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import request

# 连接数据库 需要 配置
db = db_mysql.DB_sql(host="47.97.35.19",
                     port=3306,
                     user="root",
                     password="rain1q2w3e4r5t")
# Chrome 设置代理
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
chrome = webdriver.Chrome(options=options)
# chrome.set_window_size(width, hight)
chrome.maximize_window()
chrome.implicitly_wait(5)
# 设置为手机浏览器模式
elment = chrome.find_element(By.TAG_NAME, 'body')
elment.send_keys(Keys.F12)
elment.send_keys(Keys.CLEAR, Keys.SHIFT, 'm')

# 网站  需要传入hqid，station，recommendType（默认为0） remember，reStationAdminId（默认为空），微信的openID
url = 'https://wx.test.youzhanguanjia.com/web/indexV9.2.html?version=V9.2#/memberRegister?hqId=16548&stationId' \
      '=165481000&recomendType=0&reMemberId=&reStationAdminId=&openId=o3Uia0XxRtKiO4g-3ryMKI1r4NIA'

chrome.get(url)
time.sleep(0.5)
# 页面操作 元素需要封装   输入会员信息 姓名 号码    页面元素变动--填写内容变动 需要获取需要填写的内容
# //*[@id="app"]/section/div[1]/section/div[2]/span    根据text进行输入
chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[1]/section/div[1]/input').send_keys('UItest')
chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[1]/section/div[2]/input').send_keys('13290050487')
# 验证码用接口发送 ，因为无随机码，注册不合法  需要封装请求接口
# chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[1]/section/div[3]/div[2]/button/span[1]').click()
# time.sleep(6)
code_url = 'https://wx.test.youzhanguanjia.com/third/member/getValidateCode'

pars = {
    'hqId': '16548',
    'stationId': '165481000',
    # 'sourceType': '1',
    # 'openId': 'o3Uia0XxRtKiO4g-3ryMKI1r4NIA'
    # 'memberId': '123466020'
    'phoneNum': '13290050487'

}
# res = request.request(method="POST", url=code_url, params=pars)
# # 对返回的接口进行判断
# if res.json()['msg'] == u'操作成功' and res.json()['success'] is True:
#     time.sleep(0.5)
# else:
#     print('一分钟内')
# 数据库查询 需要封装读取
sql = r"SELECT `CODE` FROM weixin.verification_code where PHONE_NUM = '13290050487' ORDER BY SENT_TIME desc LIMIT 1"
c = db.select_db(sql)
# 输入会员信息 手机验证码
chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[1]/section/div[3]/div[1]/input').send_keys(c[0]['CODE'])
# 注册站点
chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[1]/section/div[5]/input').click()
# 滚动选择站点  陈龙测试
target = chrome.find_element(By.XPATH, '//*[@id="app"]/section/div[7]/div/div[5]/p')
chrome.execute_script("arguments[0].scrollIntoView();", target)
target.click()
time.sleep(1)
# 提交注册
chrome.find_element(By.XPATH, '//*[@id="app"]/section/footer/button').click()
time.sleep(3)
print(chrome.current_url)
# 通过查询数据库 查看会员是否生成  目前用姓名和号码  后续用ID和号码
par = request.get_parms(chrome.current_url)
print(par)
time.sleep(0.5)
sql2 = r"select * from  crm.member  where MEMBER_ID = '{}' and PHONE_NUM = '{}' and `STATUS` = 1 ORDER BY ID  DESC " \
       r"LIMIT 1 ".format(par['memberId'], "13290050487")
ac = db.select_db(sql2)
if ac:
    print(ac)
    print("注册成功")
else:
    print('注册失败')
chrome.quit()