#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表单验证模块
定义用户注册、登录等表单验证类
"""

import wtforms
from wtforms.validators import Email, Length, EqualTo, ValidationError
from models import UserModel, EmailCaptchaModel
from datetime import datetime, timedelta

class RegisterForm(wtforms.Form):
    """用户注册表单"""
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    captcha = wtforms.StringField(validators=[Length(min=4, max=6, message="验证码格式错误！")])
    username = wtforms.StringField(validators=[Length(min=3, max=20, message="用户名格式错误！")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误！")])
    password_confirm = wtforms.StringField(validators=[EqualTo("password", message="两次密码不一致！")])
    
    # 自定义验证：邮箱是否已被注册
    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise ValidationError(message="该邮箱已经被注册！")
    
    # 自定义验证：验证码是否正确
    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email, captcha=captcha).first()
        if not captcha_model:
            raise ValidationError(message="邮箱或验证码错误！")
        
        # 检查验证码是否过期（10分钟有效期）
        if datetime.now() - captcha_model.create_time > timedelta(minutes=10):
            raise ValidationError(message="验证码已过期，请重新获取！")

class LoginForm(wtforms.Form):
    """用户登录表单"""
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误！")])
    remember = wtforms.BooleanField(default=False)

class EmailCaptchaForm(wtforms.Form):
    """邮箱验证码表单"""
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])

class QuestionForm(wtforms.Form):
    """问题提交表单"""
    question = wtforms.StringField(validators=[Length(min=2, max=500, message="问题长度应在2-500个字符之间！")])

class FeedbackForm(wtforms.Form):
    """用户反馈表单"""
    content = wtforms.TextAreaField(validators=[Length(min=10, max=1000, message="反馈内容长度应在10-1000个字符之间！")])
    contact = wtforms.StringField(validators=[Length(max=100, message="联系方式长度不能超过100个字符！")])

# 表单验证辅助函数
def validate_email_format(email):
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """验证密码强度"""
    # 至少6个字符，包含字母和数字
    if len(password) < 6:
        return False, "密码长度至少为6位"
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_letter or not has_digit:
        return False, "密码必须包含字母和数字"
    
    return True, "密码强度合格"

def validate_username(username):
    """验证用户名格式"""
    # 3-20个字符，只能包含字母、数字、中文、下划线
    import re
    if len(username) < 3 or len(username) > 20:
        return False, "用户名长度应在3-20个字符之间"
    
    pattern = r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$'
    if not re.match(pattern, username):
        return False, "用户名只能包含字母、数字、中文和下划线"
    
    return True, "用户名格式正确"

# 验证码生成函数
def generate_captcha(length=6):
    """生成随机验证码"""
    import random
    import string
    
    # 生成包含数字和字母的验证码
    characters = string.ascii_uppercase + string.digits
    captcha = ''.join(random.choice(characters) for _ in range(length))
    return captcha

# 表单错误处理函数
def get_form_errors(form):
    """获取表单错误信息"""
    errors = []
    for field_name, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(f"{field_name}: {error}")
    return errors

if __name__ == '__main__':
    # 测试验证码生成
    print("生成的验证码:", generate_captcha())
    
    # 测试邮箱格式验证
    test_emails = ["test@example.com", "invalid.email", "user@domain"]
    for email in test_emails:
        is_valid = validate_email_format(email)
        print(f"邮箱 {email} 格式验证: {'通过' if is_valid else '不通过'}")
    
    # 测试密码强度验证
    test_passwords = ["123456", "abcdef", "abc123", "short"]
    for password in test_passwords:
        is_valid, message = validate_password_strength(password)
        print(f"密码 {password} 强度验证: {message}")
    
    # 测试用户名格式验证
    test_usernames = ["user123", "测试用户", "invalid@user", "ab"]
    for username in test_usernames:
        is_valid, message = validate_username(username)
        print(f"用户名 {username} 格式验证: {message}")