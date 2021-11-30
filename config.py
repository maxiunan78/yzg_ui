import os

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYPROGRAM",
    settings_files=[r'config/settings.yaml'],
    environments=True)

os.environ['ENV_FOR_DYNACONF'] = 'test'
