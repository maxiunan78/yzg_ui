#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：yzg_ui 
@File    ：conftest.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/6 
"""
import os

import pytest
from base import driver
from page import page_base

base_driver = None


@pytest.fixture(scope='session')
def driver_base(request):
    global base_driver
    if base_driver is None:
        base_driver = driver.chrome()
        browser = page_base.Base(base_driver)

    def close():
        browser.quit()

    request.addfinalizer(close)
    return base_driver


def _fail_picture(name):
    browser = page_base.Base(base_driver)
    browser.fail_picture(name)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport():
    '''
    hook pytest失败
    :param item:
    :param call:
    :return:
    '''
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # we only look at actual failing test calls, not setup/teardown
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
        _fail_picture(rep.nodeid.split('::')[-1])
