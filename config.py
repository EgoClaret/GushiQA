#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含数据库连接、API密钥等配置信息
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:inscode@localhost:3306/poetry_qa?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Neo4j配置
    NEO4J_URI = os.environ.get('NEO4J_URI') or 'bolt://localhost:7687'
    NEO4J_USER = os.environ.get('NEO4J_USER') or 'neo4j'
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD') or 'password'
    
    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 邮件配置（用于验证码）
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.163.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your_email@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your_email_password'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///poetry_qa_dev.db'  # 开发环境使用SQLite


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:inscode@localhost:3306/poetry_qa?charset=utf8mb4'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}