# -*- coding:utf-8 -*-
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:  # 基本配置
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=14)

class DevelopmentConfig(BaseConfig):
    DEBUG = False

class TestingConfig(BaseConfig):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
