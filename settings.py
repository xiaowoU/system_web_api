'''==================================================
@IDE: PyCharm
@Time : 2021/10/15 15:31
@Author : wyp
@File : settings.py
=================================================='''
import os
from configparser import ConfigParser


# 获取相关配置文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BASE_DIR)
config_file = os.path.join(BASE_DIR, 'conf', 'conf.ini')
cfg = ConfigParser()
cfg.read(config_file)