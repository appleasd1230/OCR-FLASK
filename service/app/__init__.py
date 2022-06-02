# -*- coding:utf-8 -*-
import os

from flask import Flask, Blueprint
# 引用其他相關模組
from .config.config import config

def create_app(config_name):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # 設定 config
    app.config.from_object(config[config_name])

    register_blueprints(app)

    # a simple page that says hello
    @app.route('/')
    def index():
        return 'Hello, Paddle!'

    return app

def register_blueprints(app):
    """Register blueprints with the Flask application."""
    from .view.recognize import recognize
    app.register_blueprint(recognize, url_prefix='/rec')
