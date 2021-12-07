"""
@Project ：yzg_ui
@File    ：config.py
@Author  ：穆崧
@Date    ：创建时间：2021/12/6
"""


from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYPROGRAM",
    settings_files=['settings.yaml'],
    environments=True)


