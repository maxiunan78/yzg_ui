#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：conftest.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/6 
"""

import pytest
from base import driver
from base.preconditions import Precondition
from page import page_base

base_driver = None


@pytest.fixture(scope='session')
def driver_base(request):
    """
    初始化driver
    :param request:
    :return:
    """
    global base_driver
    if base_driver is None:
        base_driver = driver.chrome()
        browser = page_base.Base(base_driver)

    def close():
        browser.quit()

    request.addfinalizer(close)
    return base_driver


def _fail_picture(name):
    """
    截图
    :param name:
    :return:
    """
    browser = page_base.Base(base_driver)
    browser.fail_picture(name)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport():
    """
    用例失败自动截图
    :return:
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        # mode = "a" if os.path.exists("failures") else "w"
        # with open("failures", mode) as f:
        #     # let's also access a fixture for the fun of it
        # if "tmpdir" in item.fixturenames:
        #     extra = " (%s)" % item.funcargs["tmpdir"]
        #     print(extra)
        # else:
        #     extra = ""
        #     f.write(rep.nodeid + extra + "\n")

        _fail_picture(rep.nodeid.split('::')[-1].split('[')[0])


@pytest.fixture(scope='class')
def member_info():
    member_info = Precondition.get_member()
    return member_info
