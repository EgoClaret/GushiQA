#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据脚本
创建示例古诗词数据和知识图谱数据
"""

import json
import os
from datetime import datetime
from app import app, db
from models import UserModel

# 示例古诗词数据
SAMPLE_POETRY_DATA = [
    {
        "title": "静夜思",
        "author": "李白",
        "dynasty": "唐代",
        "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
        "translation": "明亮的月光洒在床前的窗户纸上，好像地上泛起了一层白霜。我禁不住抬起头来，看那天窗外空中的一轮明月，不由得低头沉思，想起远方的家乡。",
        "annotation": "床：今传五种说法。一指井栏。二指井栏。三\"床\"即\"窗\"的通假字。四取本义，即坐卧的器具。五马未都等认为，床应解释为胡床。",
        "background": "李白的《静夜思》创作于唐玄宗开元十四年（726年），当时李白客居扬州。",
        "appreciation": "此诗描写了秋日夜晚，诗人于屋内抬头望月的所感。诗中运用比喻、衬托等手法，表达客居思乡之情。"
    },
    {
        "title": "春晓",
        "author": "孟浩然",
        "dynasty": "唐代",
        "content": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
        "translation": "春天的夜晚睡得很香甜，不知不觉天就亮了，醒来时到处都能听到鸟儿的啼叫声。回想起昨夜听到的风雨声，不知道有多少花朵被打落了。",
        "annotation": "春晓：春天的早晨。不觉晓：不知不觉天就亮了。啼鸟：鸟的啼叫声。",
        "background": "这首诗是孟浩然隐居鹿门山时所作，描写了春天早晨醒来时的情景和感受。",
        "appreciation": "这首诗语言平易自然，意境清新，通过听觉感受描绘了春天的美好，表达了诗人对春天的喜爱之情。"
    },
    {
        "title": "登鹳雀楼",
        "author": "王之涣",
        "dynasty": "唐代",
        "content": "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。",
        "translation": "夕阳依傍着西山慢慢地沉没，滔滔黄河朝着东海汹涌奔流。若想把千里的风光景物看够，那就要登上更高的一层城楼。",
        "annotation": "鹳雀楼：古名鹳鹊楼，因时有鹳鹊栖其上而得名，其故址在永济市境内古蒲州城外西南的黄河岸边。",
        "background": "王之涣是盛唐时期的著名诗人，这首诗写于他登上鹳雀楼远眺时的所见所感。",
        "appreciation": "这首诗写诗人在登高望远中表现出来的不凡的胸襟抱负，反映了盛唐时期人们积极向上的进取精神。"
    },
    {
        "title": "相思",
        "author": "王维",
        "dynasty": "唐代",
        "content": "红豆生南国，春来发几枝。愿君多采撷，此物最相思。",
        "translation": "红豆生长在阳光明媚的南方，每逢春天不知长多少新枝。希望思念的人儿多多采摘，因为它最能寄托相思之情。",
        "annotation": "红豆：又名相思子，一种生在江南地区的植物，结出的籽象豌豆而稍扁，呈鲜红色。",
        "background": "这首诗是王维写给好友李龟年的，借红豆表达深切的思念之情。",
        "appreciation": "全诗洋溢着少年的热情，青春的气息，满腹情思始终未曾直接表白，句句话儿不离红豆，而又超以象外，得其圜中。"
    }
]

# 示例诗人数据
SAMPLE_AUTHORS = [
    {
        "name": "李白",
        "dynasty": "唐代",
        "gender": "男",
        "birth_year": 701,
        "death_year": 762,
        "hometown": "陇西成纪（今甘肃天水）",
        "description": "字太白，号青莲居士，唐代伟大的浪漫主义诗人，被后人誉为'诗仙'。",
        "famous_works": ["静夜思", "将进酒", "蜀道难", "梦游天姥吟留别"]
    },
    {
        "name": "孟浩然",
        "dynasty": "唐代",
        "gender": "男",
        "birth_year": 689,
        "death_year": 740,
        "hometown": "襄州襄阳（今湖北襄阳）",
        "description": "字浩然，号孟山人，唐代著名的山水田园诗人，与王维并称'王孟'。",
        "famous_works": ["春晓", "过故人庄", "宿建德江"]
    },
    {
        "name": "王之涣",
        "dynasty": "唐代",
        "gender": "男",
        "birth_year": 688,
        "death_year": 742,
        "hometown": "晋阳（今山西太原）",
        "description": "字季凌，唐代著名诗人，以描写边塞风光著称。",
        "famous_works": ["登鹳雀楼", "凉州词"]
    },
    {
        "name": "王维",
        "dynasty": "唐代",
        "gender": "男",
        "birth_year": 701,
        "death_year": 761,
        "hometown": "河东蒲州（今山西运城）",
        "description": "字摩诘，号摩诘居士，唐代著名诗人、画家，有'诗佛'之称。",
        "famous_works": ["相思", "山居秋暝", "使至塞上"]
    }
]

# 示例名句数据
SAMPLE_FAMOUS_SENTENCES = [
    {
        "content": "举头望明月，低头思故乡。",
        "author": "李白",
        "work": "静夜思"
    },
    {
        "content": "春眠不觉晓，处处闻啼鸟。",
        "author": "孟浩然",
        "work": "春晓"
    },
    {
        "content": "欲穷千里目，更上一层楼。",
        "author": "王之涣",
        "work": "登鹳雀楼"
    },
    {
        "content": "红豆生南国，春来发几枝。",
        "author": "王维",
        "work": "相思"
    }
]

def create_sample_data():
    """创建示例数据文件"""
    print("创建示例数据文件...")
    
    # 创建数据目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/nodes', exist_ok=True)
    os.makedirs('data/relationships', exist_ok=True)
    
    # 保存示例数据
    with open('data/sample_poetry.json', 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_POETRY_DATA, f, ensure_ascii=False, indent=2)
    
    with open('data/sample_authors.json', 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_AUTHORS, f, ensure_ascii=False, indent=2)
    
    with open('data/sample_sentences.json', 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_FAMOUS_SENTENCES, f, ensure_ascii=False, indent=2)
    
    print("示例数据文件创建完成！")

def create_test_user():
    """创建测试用户"""
    with app.app_context():
        # 检查是否已存在测试用户
        test_user = UserModel.query.filter_by(email='test@example.com').first()
        if not test_user:
            from werkzeug.security import generate_password_hash
            user = UserModel(
                username='测试用户',
                email='test@example.com',
                password=generate_password_hash('123456'),
                join_time=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            print("测试用户创建成功！")
            print("用户名: test@example.com")
            print("密码: 123456")
        else:
            print("测试用户已存在！")

def main():
    """主函数"""
    print("开始初始化数据...")
    
    # 创建示例数据
    create_sample_data()
    
    # 创建数据库表
    print("创建数据库表...")
    with app.app_context():
        db.create_all()
    print("数据库表创建完成！")
    
    # 创建测试用户
    create_test_user()
    
    print("数据初始化完成！")

if __name__ == '__main__':
    main()