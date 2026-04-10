#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古诗词问答系统核心模块
包含意图识别、命名实体识别和答案生成
"""

import re
import json
import logging
import jieba
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XiaoShiRobot:
    """古诗词问答机器人"""
    
    def __init__(self):
        """初始化问答机器人"""
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.answer_templates = self._load_answer_templates()
        self.knowledge_graph = None  # 将在运行时注入
        
        # 加载自定义词典
        self._load_custom_dict()
        
        logger.info("古诗词问答机器人初始化完成")
    
    def _load_custom_dict(self):
        """加载自定义词典"""
        # 古诗词相关词汇
        poetry_words = [
            "李白", "杜甫", "苏轼", "李清照", "白居易", "王维", "孟浩然",
            "唐代", "宋代", "元代", "明代", "清代",
            "静夜思", "春望", "水调歌头", "将进酒", "登高",
            "五言绝句", "七言绝句", "五言律诗", "七言律诗", "词",
            "浪漫主义", "现实主义", "豪放派", "婉约派"
        ]
        
        for word in poetry_words:
            jieba.add_word(word)
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """加载意图识别模式"""
        return {
            "dynasty_of_author": [
                ".*(?<!不)是哪个朝代的.*",
                ".*(?<!不)是什么朝代的.*",
                ".*(?<!不)生活在.*朝代.*",
                ".*(?<!不)属于.*朝代.*",
                ".*(?<!不)是哪个时代的.*",
                ".*(?<!不)是什么时代的.*"
            ],
            "works_of_author": [
                ".*(?<!不)有哪些作品.*",
                ".*(?<!不)写了什么诗.*",
                ".*(?<!不)有什么诗.*",
                ".*(?<!不)的代表作.*",
                ".*(?<!不)的著名作品.*",
                ".*(?<!不)的诗作.*"
            ],
            "author_of_work": [
                ".*(?<!不)的作者是谁.*",
                ".*(?<!不)是谁写的.*",
                ".*(?<!不)是谁作的.*",
                ".*(?<!不)的创作者.*",
                ".*(?<!不)是谁创作的.*"
            ],
            "content_of_work": [
                ".*(?<!不)的内容是什么.*",
                ".*(?<!不)的全文.*",
                ".*(?<!不)的诗句.*",
                ".*(?<!不)的原文.*",
                ".*(?<!不)怎么写.*"
            ],
            "theme_of_work": [
                ".*(?<!不)的主题.*",
                ".*(?<!不)表达什么.*",
                ".*(?<!不)的含义.*",
                ".*(?<!不)的意思.*",
                ".*(?<!不)的寓意.*"
            ],
            "style_of_author": [
                ".*(?<!不)的风格.*",
                ".*(?<!不)的特点.*",
                ".*(?<!不)的诗风.*",
                ".*(?<!不)的创作风格.*",
                ".*(?<!不)的艺术特色.*"
            ],
            "famous_sentences": [
                ".*(?<!不)的名句.*",
                ".*(?<!不)的经典诗句.*",
                ".*(?<!不)的著名诗句.*",
                ".*(?<!不)的代表诗句.*"
            ],
            "dynasty_info": [
                ".*(?<!不)是什么朝代.*",
                ".*(?<!不)朝代.*信息.*",
                ".*(?<!不)朝代.*介绍.*",
                ".*(?<!不)朝代.*历史.*"
            ],
            "poetry_knowledge": [
                ".*(?<!不)诗词.*知识.*",
                ".*(?<!不)诗歌.*常识.*",
                ".*(?<!不)文学.*知识.*",
                ".*(?<!不)文化.*知识.*"
            ],
            "greeting": [
                "你好.*", "您好.*", "嗨.*", "哈喽.*", "嗨喽.*",
                "早上好.*", "下午好.*", "晚上好.*"
            ],
            "thanks": [
                "谢谢.*", "感谢.*", "多谢.*", "谢了.*"
            ],
            "goodbye": [
                "再见.*", "拜拜.*", "回见.*", "下次见.*"
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """加载实体识别模式"""
        return {
            "Author": [
                "李白", "杜甫", "苏轼", "李清照", "白居易", "王维", "孟浩然",
                "辛弃疾", "陆游", "欧阳修", "柳宗元", "韩愈", "刘禹锡",
                "陶渊明", "谢灵运", "鲍照", "庾信", "王勃", "杨炯", "卢照邻", "骆宾王",
                "陈子昂", "张九龄", "王之涣", "王昌龄", "高适", "岑参",
                "元稹", "刘禹锡", "李贺", "杜牧", "李商隐", "温庭筠",
                "范仲淹", "晏殊", "欧阳修", "柳永", "王安石", "晏几道",
                "黄庭坚", "秦观", "晁补之", "张耒", "周邦彦", "李清照",
                "岳飞", "张孝祥", "辛弃疾", "陈亮", "刘过", "姜夔",
                "文天祥", "元好问", "马致远", "张养浩", "张可久", "乔吉",
                "高启", "于谦", "王磐", "陈铎", "冯惟敏", "薛论道",
                "李攀龙", "王世贞", "谢榛", "宗臣", "梁有誉", "徐中行", "吴国伦"
            ],
            "Work": [
                "静夜思", "春望", "水调歌头", "将进酒", "登高", "茅屋为秋风所破歌",
                "念奴娇·赤壁怀古", "江城子·密州出猎", "水调歌头·明月几时有",
                "声声慢·寻寻觅觅", "醉花阴·薄雾浓云愁永昼", "如梦令·常记溪亭日暮",
                "琵琶行", "长恨歌", "卖炭翁", "观刈麦", "钱塘湖春行",
                "山居秋暝", "使至塞上", "相思", "送元二使安西",
                "春晓", "过故人庄", "宿建德江", "临洞庭湖赠张丞相",
                "破阵子·为陈同甫赋壮词以寄之", "永遇乐·京口北固亭怀古", "青玉案·元夕",
                "钗头凤·红酥手", "秋夜将晓出篱门迎凉有感二首·其二", "示儿",
                "浪淘沙·九曲黄河万里沙", "陋室铭", "乌衣巷", "竹枝词二首·其一",
                "李凭箜篌引", "雁门太守行", "金铜仙人辞汉歌",
                "阿房宫赋", "赤壁", "泊秦淮", "江南春",
                "锦瑟", "无题·相见时难别亦难", "夜雨寄北", "嫦娥",
                "菩萨蛮·小山重叠金明灭", "望江南·梳洗罢", "更漏子·玉炉香",
                "渔家傲·秋思", "苏幕遮·碧云天", "浣溪沙·一曲新词酒一杯",
                "蝶恋花·槛菊愁烟兰泣露", "踏莎行·候馆梅残", "生查子·元夕",
                "桂枝香·金陵怀古", "泊船瓜洲", "元日", "梅花",
                "临江仙·梦后楼台高锁", "鹧鸪天·彩袖殷勤捧玉钟", "阮郎归·天边金掌露成霜",
                "鹊桥仙·纤云弄巧", "踏莎行·郴州旅舍", "满庭芳·山抹微云",
                "浣溪沙·漠漠轻寒上小楼", "鹧鸪天·重过阊门万事非", "青玉案·凌波不过横塘路",
                "六州歌头·少年侠气", "鹧鸪天·半死桐", "踏莎行·杨柳回塘",
                "兰陵王·柳", "满庭芳·夏日溧水无想山作", "苏幕遮·燎沉香",
                "浣溪沙·翠葆参差竹径成", "鹧鸪天·化度寺作", "西河·金陵怀古",
                "如梦令·昨夜雨疏风骤", "一剪梅·红藕香残玉簟秋", "醉花阴·薄雾浓云愁永昼",
                "武陵春·春晚", "声声慢·寻寻觅觅", "永遇乐·落日熔金",
                "满江红·写怀", "小重山·昨夜寒蛩不住鸣", "池州翠微亭",
                "六州歌头·长淮望断", "念奴娇·过洞庭", "西江月·题溧阳三塔寺",
                "游园不值", "题临安邸", "墨梅", "石灰吟",
                "朝天子·咏喇叭", "水仙子·咏江南", "折桂令·中秋",
                "登太白楼", "石灰吟", "朝天子·咏喇叭", "水仙子·咏江南"
            ],
            "Dynasty": [
                "先秦", "秦朝", "汉朝", "魏晋", "南北朝", "隋朝",
                "唐代", "五代十国", "宋代", "辽代", "金代", "元代",
                "明代", "清代", "民国", "现代"
            ],
            "Theme": [
                "思乡", "爱国", "友情", "爱情", "亲情", "离别",
                "山水", "田园", "边塞", "咏史", "怀古", "哲理",
                "人生", "社会", "政治", "战争", "和平", "自然",
                "季节", "节日", "饮酒", "赏花", "咏月", "咏雪",
                "春天", "夏天", "秋天", "冬天", "早晨", "黄昏",
                "夜晚", "雨天", "晴天", "风", "花", "雪", "月"
            ]
        }
    
    def _load_answer_templates(self) -> Dict[str, List[str]]:
        """加载答案模板"""
        return {
            "dynasty_of_author": [
                "当然知道{name}的所属朝代啦。{pronoun}是{dynasty}的诗词作家呢。",
                "{name}是{dynasty}时期的著名诗人。",
                "据我所知，{name}生活在{dynasty}时期。",
                "{name}是{dynasty}朝代的文学巨匠。"
            ],
            "works_of_author": [
                "{name}的作品有很多，其中比较著名的有：{works}。",
                "{name}一生创作了大量诗词，代表作包括：{works}等。",
                "据我了解，{name}的著名诗作有：{works}。",
                "{name}的诗词作品丰富，如：{works}等都是脍炙人口的佳作。"
            ],
            "author_of_work": [
                "《{title}》的作者是{name}。",
                "据我所知，《{title}》是{name}的作品。",
                "《{title}》这首诗（词）出自{name}之手。",
                "{name}是《{title}》的创作者。"
            ],
            "content_of_work": [
                "《{title}》的全文是：\n\n{content}",
                "这是《{title}》的原文：\n\n{content}",
                "{name}的《{title}》写道：\n\n{content}"
            ],
            "theme_of_work": [
                "《{title}》主要表达了{theme}的主题。",
                "这首诗（词）通过{description}，表达了{theme}的情感。",
                "《{title}》的主题是{theme}，体现了作者{emotion}的情怀。"
            ],
            "style_of_author": [
                "{name}的诗词风格是{style}，{description}。",
                "{name}的创作风格以{style}著称，{description}。",
                "据我了解，{name}的文学风格属于{style}，{description}。"
            ],
            "famous_sentences": [
                "{name}的名句有很多，比如：{sentences}。",
                "我特别喜欢{name}的这些诗句：{sentences}。",
                "{name}留下了许多经典诗句，如：{sentences}等。"
            ],
            "dynasty_info": [
                "{dynasty}是中国历史上的一个重要朝代，{period}，都城在{capital}。",
                "据我了解，{dynasty}时期是{period}，政治中心在{capital}。",
                "{dynasty}朝代{period}，是中国文化发展的重要时期。"
            ],
            "greeting": [
                "您好！我是小诗，很高兴为您服务。请问有什么关于古诗词的问题吗？",
                "你好！我是您的古诗词助手小诗，有什么可以帮助您的吗？",
                "嗨！欢迎来到古诗词问答系统，我是小诗，随时准备回答您的问题。",
                "您好！我是专门回答古诗词相关问题的AI助手小诗，请随意提问。"
            ],
            "thanks": [
                "不客气！很高兴能帮助到您。如果还有其他问题，随时问我哦。",
                "不用谢！这是我应该做的。希望我的回答对您有帮助。",
                "谢谢您的认可！能为您解答古诗词相关的问题是我的荣幸。",
                "您太客气了！如果还有其他想了解的内容，请随时提问。"
            ],
            "goodbye": [
                "再见！希望下次还能为您解答古诗词相关的问题。",
                "拜拜！祝您学习愉快，欢迎下次再来提问。",
                "再见！愿诗词的美好常伴您左右。",
                "回见！期待下次与您一起探讨古诗词的魅力。"
            ],
            "unknown": [
                "抱歉，我暂时无法回答这个问题。您可以尝试询问其他关于古诗词的问题。",
                "这个问题有点难度，我可能需要更多相关知识。您能换个问法吗？",
                "很抱歉，我的知识库中暂时没有相关信息。您可以问我关于诗人、作品、朝代等问题。",
                "这个问题我暂时回答不了，但我会继续学习。您可以尝试询问诗人、诗作、朝代等相关问题。"
            ]
        }
    
    def recognize_intent(self, question: str) -> str:
        """
        识别用户意图
        
        Args:
            question: 用户问题
            
        Returns:
            意图类型
        """
        question = question.strip()
        
        # 检查特殊意图
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    return intent
        
        # 默认返回未知意图
        return "unknown"
    
    def extract_entities(self, question: str) -> Dict[str, List[str]]:
        """
        提取命名实体
        
        Args:
            question: 用户问题
            
        Returns:
            实体字典
        """
        entities = {}
        
        # 使用jieba分词
        words = jieba.lcut(question)
        
        # 提取各类实体
        for entity_type, entity_list in self.entity_patterns.items():
            found_entities = []
            for entity in entity_list:
                if entity in question:
                    found_entities.append(entity)
            
            # 检查分词结果
            for word in words:
                if word in entity_list and word not in found_entities:
                    found_entities.append(word)
            
            if found_entities:
                entities[entity_type] = list(set(found_entities))  # 去重
        
        return entities
    
    def generate_answer(self, intent: str, entities: Dict[str, List[str]], question: str) -> str:
        """
        生成答案
        
        Args:
            intent: 用户意图
            entities: 提取的实体
            question: 用户问题
            
        Returns:
            生成的答案
        """
        try:
            # 特殊意图处理
            if intent == "greeting":
                return random.choice(self.answer_templates["greeting"])
            elif intent == "thanks":
                return random.choice(self.answer_templates["thanks"])
            elif intent == "goodbye":
                return random.choice(self.answer_templates["goodbye"])
            
            # 从kg_modules导入知识图谱
            from kg_modules import poetry_kg
            
            # 根据意图生成答案
            if intent == "dynasty_of_author":
                return self._answer_dynasty_of_author(entities)
            elif intent == "works_of_author":
                return self._answer_works_of_author(entities)
            elif intent == "author_of_work":
                return self._answer_author_of_work(entities)
            elif intent == "content_of_work":
                return self._answer_content_of_work(entities)
            elif intent == "theme_of_work":
                return self._answer_theme_of_work(entities)
            elif intent == "style_of_author":
                return self._answer_style_of_author(entities)
            elif intent == "famous_sentences":
                return self._answer_famous_sentences(entities)
            elif intent == "dynasty_info":
                return self._answer_dynasty_info(entities)
            else:
                return self._answer_unknown_question(entities, question)
                
        except Exception as e:
            logger.error(f"生成答案时出错: {e}")
            return random.choice(self.answer_templates["unknown"])
    
    def _answer_dynasty_of_author(self, entities: Dict[str, List[str]]) -> str:
        """回答诗人朝代问题"""
        if "Author" not in entities or not entities["Author"]:
            return "抱歉，我没有识别出您询问的是哪位诗人。"
        
        author_name = entities["Author"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        author_info = poetry_kg.get_author_info(author_name)
        
        if not author_info:
            return f"抱歉，我的知识库中没有关于{author_name}的信息。"
        
        dynasty = author_info.get("dynasty", "未知")
        gender = author_info.get("gender", "男")
        pronoun = "他" if gender == "男" else "她"
        
        template = random.choice(self.answer_templates["dynasty_of_author"])
        return template.format(name=author_name, dynasty=dynasty, pronoun=pronoun)
    
    def _answer_works_of_author(self, entities: Dict[str, List[str]]) -> str:
        """回答诗人作品问题"""
        if "Author" not in entities or not entities["Author"]:
            return "抱歉，我没有识别出您询问的是哪位诗人。"
        
        author_name = entities["Author"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        works = poetry_kg.get_author_works(author_name)
        
        if not works:
            return f"抱歉，我的知识库中没有找到{author_name}的作品信息。"
        
        # 获取作品标题
        work_titles = [work.get("title", "") for work in works[:5]]  # 最多显示5个
        works_str = "、".join(work_titles)
        
        template = random.choice(self.answer_templates["works_of_author"])
        return template.format(name=author_name, works=works_str)
    
    def _answer_author_of_work(self, entities: Dict[str, List[str]]) -> str:
        """回答作品作者问题"""
        if "Work" not in entities or not entities["Work"]:
            return "抱歉，我没有识别出您询问的是哪部作品。"
        
        work_title = entities["Work"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        work_info = poetry_kg.get_work_info(work_title)
        
        if not work_info:
            return f"抱歉，我的知识库中没有《{work_title}》的信息。"
        
        author = work_info.get("author", "未知")
        
        template = random.choice(self.answer_templates["author_of_work"])
        return template.format(title=work_title, name=author)
    
    def _answer_content_of_work(self, entities: Dict[str, List[str]]) -> str:
        """回答作品内容问题"""
        if "Work" not in entities or not entities["Work"]:
            return "抱歉，我没有识别出您询问的是哪部作品。"
        
        work_title = entities["Work"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        work_info = poetry_kg.get_work_info(work_title)
        
        if not work_info:
            return f"抱歉，我的知识库中没有《{work_title}》的信息。"
        
        content = work_info.get("content", "内容暂无")
        author = work_info.get("author", "未知")
        
        template = random.choice(self.answer_templates["content_of_work"])
        return template.format(title=work_title, content=content, name=author)
    
    def _answer_theme_of_work(self, entities: Dict[str, List[str]]) -> str:
        """回答作品主题问题"""
        if "Work" not in entities or not entities["Work"]:
            return "抱歉，我没有识别出您询问的是哪部作品。"
        
        work_title = entities["Work"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        work_info = poetry_kg.get_work_info(work_title)
        
        if not work_info:
            return f"抱歉，我的知识库中没有《{work_title}》的信息。"
        
        theme = work_info.get("theme", "深刻的主题")
        description = "通过生动的意象和优美的语言"
        
        template = random.choice(self.answer_templates["theme_of_work"])
        return template.format(title=work_title, theme=theme, description=description)
    
    def _answer_style_of_author(self, entities: Dict[str, List[str]]) -> str:
        """回答诗人风格问题"""
        if "Author" not in entities or not entities["Author"]:
            return "抱歉，我没有识别出您询问的是哪位诗人。"
        
        author_name = entities["Author"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        author_info = poetry_kg.get_author_info(author_name)
        
        if not author_info:
            return f"抱歉，我的知识库中没有关于{author_name}的信息。"
        
        style = author_info.get("style", "独特的风格")
        description = "作品充满了艺术魅力和深刻的思想内涵"
        
        template = random.choice(self.answer_templates["style_of_author"])
        return template.format(name=author_name, style=style, description=description)
    
    def _answer_famous_sentences(self, entities: Dict[str, List[str]]) -> str:
        """回答名句问题"""
        author_name = None
        if "Author" in entities and entities["Author"]:
            author_name = entities["Author"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        famous_sentences = poetry_kg.get_famous_sentences(author_name, limit=3)
        
        if not famous_sentences:
            return "抱歉，我的知识库中暂时没有相关的名句信息。"
        
        # 格式化名句
        sentences_list = []
        for fs in famous_sentences:
            content = fs.get("content", "")
            title = fs.get("title", "")
            if title:
                sentences_list.append(f"《{title}》：{content}")
            else:
                sentences_list.append(content)
        
        sentences_str = "\n".join(sentences_list)
        
        if author_name:
            template = random.choice(self.answer_templates["famous_sentences"])
            return template.format(name=author_name, sentences=sentences_str)
        else:
            return f"这里有一些经典的名句：\n\n{sentences_str}"
    
    def _answer_dynasty_info(self, entities: Dict[str, List[str]]) -> str:
        """回答朝代信息问题"""
        if "Dynasty" not in entities or not entities["Dynasty"]:
            return "抱歉，我没有识别出您询问的是哪个朝代。"
        
        dynasty_name = entities["Dynasty"][0]
        
        # 从知识图谱获取信息
        from kg_modules import poetry_kg
        dynasty_info = poetry_kg.get_dynasty_info(dynasty_name)
        
        if not dynasty_info:
            return f"抱歉，我的知识库中没有关于{dynasty_name}的信息。"
        
        period = dynasty_info.get("period", "历史时期")
        capital = dynasty_info.get("capital", "都城")
        
        template = random.choice(self.answer_templates["dynasty_info"])
        return template.format(dynasty=dynasty_name, period=period, capital=capital)
    
    def _answer_unknown_question(self, entities: Dict[str, List[str]], question: str) -> str:
        """回答未知问题"""
        # 尝试基于提取的实体生成相关回答
        if entities:
            # 如果有实体信息，尝试生成相关回答
            entity_info = []
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entity_info.append(f"{entity_type}：{', '.join(entity_list)}")
            
            if entity_info:
                entity_str = '；'.join(entity_info)
                return f"我识别到您的问题中提到了：{entity_str}。但我暂时无法给出具体的答案。您可以尝试更具体地描述您的问题，或者询问其他相关的古诗词知识。"
        
        return random.choice(self.answer_templates["unknown"])
    
    def answer(self, question: str) -> str:
        """
        主问答函数
        
        Args:
            question: 用户问题
            
        Returns:
            答案
        """
        try:
            logger.info(f"收到问题: {question}")
            
            # 意图识别
            intent = self.recognize_intent(question)
            logger.info(f"识别到的意图: {intent}")
            
            # 命名实体识别
            entities = self.extract_entities(question)
            logger.info(f"提取的实体: {entities}")
            
            # 生成答案
            answer = self.generate_answer(intent, entities, question)
            
            logger.info(f"生成的答案: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"问答处理失败: {e}")
            return "抱歉，系统暂时无法处理您的问题。请稍后再试。"


# 全局问答机器人实例
xiaoshi_robot = XiaoShiRobot()


if __name__ == "__main__":
    # 测试问答功能
    test_questions = [
        "李白是哪个朝代的诗人？",
        "杜甫有哪些著名的诗作？",
        "静夜思的作者是谁？",
        "苏轼的词风特点是什么？",
        "你好",
        "谢谢",
        "再见"
    ]
    
    print("测试古诗词问答系统...")
    for question in test_questions:
        print(f"\n问题: {question}")
        answer = xiaoshi_robot.answer(question)
        print(f"答案: {answer}")
    
    print("\n测试完成！")