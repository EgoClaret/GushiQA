#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型
定义用户、验证码等数据库表结构
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class UserModel(db.Model, UserMixin):
    """用户模型"""
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return str(self.id)

class EmailCaptchaModel(db.Model):
    """邮箱验证码模型"""
    __tablename__ = "email_captcha"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    captcha = db.Column(db.String(10), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<EmailCaptcha {self.email}>'

class QueryHistoryModel(db.Model):
    """查询历史模型"""
    __tablename__ = "query_history"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    query_time = db.Column(db.DateTime, default=datetime.now)
    intent = db.Column(db.String(100))  # 用户意图
    entities = db.Column(db.Text)  # 识别的实体，JSON格式
    
    user = db.relationship('UserModel', backref='query_history')
    
    def __repr__(self):
        return f'<QueryHistory {self.id}>'

class PoetryKnowledgeModel(db.Model):
    """古诗词知识模型"""
    __tablename__ = "poetry_knowledge"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    dynasty = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    translation = db.Column(db.Text)
    annotation = db.Column(db.Text)
    background = db.Column(db.Text)
    appreciation = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<PoetryKnowledge {self.title}>'

class AuthorKnowledgeModel(db.Model):
    """诗人知识模型"""
    __tablename__ = "author_knowledge"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    dynasty = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_year = db.Column(db.Integer)
    death_year = db.Column(db.Integer)
    hometown = db.Column(db.String(200))
    description = db.Column(db.Text)
    famous_works = db.Column(db.Text)  # JSON格式存储著名作品
    create_time = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<AuthorKnowledge {self.name}>'

class FamousSentenceModel(db.Model):
    """名句知识模型"""
    __tablename__ = "famous_sentence"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    work = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<FamousSentence {self.content[:20]}...>'

# 创建所有表的函数
def create_tables():
    """创建所有数据库表"""
    with app.app_context():
        db.create_all()
        print("所有数据库表创建完成！")

if __name__ == '__main__':
    from app import app
    create_tables()