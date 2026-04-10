#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于知识图谱的古诗词问答系统
作者：Inscode AI
来源：https://blog.csdn.net/m0_51072263/article/details/147005072
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import json
import markdown
import jieba
import fasttext
import numpy as np
from py2neo import Graph
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入配置
from config import config

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config['development'])

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Neo4j图数据库连接（暂时禁用，使用模拟数据）
# try:
#     graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
#     logger.info("Neo4j连接成功")
# except Exception as e:
#     logger.error(f"Neo4j连接失败: {e}")
#     graph = None
graph = None  # 暂时使用None，后续可以连接真实Neo4j数据库

# 用户模型
class UserModel(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)

    def get_id(self):
        return str(self.id)

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# 注册路由
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # 获取表单数据
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # 简单验证
        if not all([email, username, password, password_confirm]):
            flash('请填写所有必填字段！')
            return redirect(url_for('register'))
        
        if password != password_confirm:
            flash('两次密码不一致！')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('密码长度至少为6位！')
            return redirect(url_for('register'))
        
        # 检查邮箱是否已存在
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            flash('该邮箱已被注册！')
            return redirect(url_for('register'))
        
        # 创建新用户
        try:
            user = UserModel(
                email=email,
                username=username,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录。')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试！')
            return redirect(url_for('register'))

# 登录路由
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            flash('请填写邮箱和密码！')
            return redirect(url_for('login'))
        
        user = UserModel.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('邮箱或密码错误！')
            return redirect(url_for('login'))

# 登出路由
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 知识图谱问答系统页面
@app.route('/KGQA_Poetry', methods=['GET', 'POST'])
@login_required
def KGQA_Poetry():
    return render_template('KGQA_Poetry.html')

# 基于知识图谱的问答 - 古诗词
@app.route("/KGQA_Poetry_Answer", methods=["POST"])
def KGQA_Poetry_Answer():
    try:
        # 获取前端输入的问题
        question = request.form.get("question", "")
        if not question:
            return jsonify({"error": "请输入问题"}), 400
        
        # 简单的问答逻辑（后续会完善）
        answer = process_question(question)
        
        # 转换为markdown格式
        answer_html = markdown.markdown(answer)
        
        return jsonify({"answer": answer_html})
    except Exception as e:
        logger.error(f"问答处理错误: {e}")
        return jsonify({"error": "处理问题时出现错误"}), 500

# 简单的问答处理函数（后续会完善）
def process_question(question):
    """处理用户问题，返回答案"""
    question = question.strip()
    
    # 示例问题处理
    if "李白" in question and "朝代" in question:
        return "李白是唐代的著名诗人，被后人誉为\"诗仙\"。他的诗歌豪放飘逸，想象丰富，是浪漫主义诗歌的代表人物。"
    
    if "杜甫" in question and "朝代" in question:
        return "杜甫是唐代的伟大诗人，被后人尊称为\"诗圣\"。他的诗歌深刻反映了唐代社会的现实，是现实主义诗歌的杰出代表。"
    
    if "苏轼" in question and "朝代" in question:
        return "苏轼是北宋时期的文学家、书画家。他的诗词豪放洒脱，散文汪洋恣肆，是\"唐宋八大家\"之一。"
    
    # 默认回答
    return "很抱歉，我暂时无法回答这个问题。您可以尝试询问诗人的朝代、代表作品等信息。"

# 创建数据库表
def create_tables():
    with app.app_context():
        db.create_all()
        logger.info("数据库表创建成功")

if __name__ == '__main__':
    # 创建数据库表
    create_tables()
    
    # 启动应用
    logger.info("古诗词问答系统启动...")
    app.run(debug=True, host='0.0.0.0', port=5000)