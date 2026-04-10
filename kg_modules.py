#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱模块
基于Neo4j图数据库的古诗词知识图谱操作
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from py2neo import Graph, Node, Relationship, NodeMatcher
from py2neo.errors import ConnectionError, DatabaseError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoetryKnowledgeGraph:
    """古诗词知识图谱类"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "password"):
        """
        初始化知识图谱连接
        
        Args:
            uri: Neo4j数据库连接地址
            username: 用户名
            password: 密码
        """
        try:
            self.graph = Graph(uri, auth=(username, password))
            self.matcher = NodeMatcher(self.graph)
            logger.info("成功连接到Neo4j数据库")
        except ConnectionError as e:
            logger.error(f"连接Neo4j数据库失败: {e}")
            # 创建模拟数据用于演示
            self.graph = None
            self.mock_data = self._create_mock_data()
    
    def _create_mock_data(self) -> Dict[str, List[Dict]]:
        """创建模拟数据用于演示"""
        return {
            "authors": [
                {
                    "name": "李白",
                    "dynasty": "唐代",
                    "gender": "男",
                    "birth_year": 701,
                    "death_year": 762,
                    "style": "浪漫主义",
                    "description": "字太白，号青莲居士，唐代伟大的浪漫主义诗人"
                },
                {
                    "name": "杜甫",
                    "dynasty": "唐代",
                    "gender": "男",
                    "birth_year": 712,
                    "death_year": 770,
                    "style": "现实主义",
                    "description": "字子美，自号少陵野老，唐代伟大的现实主义诗人"
                },
                {
                    "name": "苏轼",
                    "dynasty": "宋代",
                    "gender": "男",
                    "birth_year": 1037,
                    "death_year": 1101,
                    "style": "豪放派",
                    "description": "字子瞻，号东坡居士，北宋文学家、书画家"
                }
            ],
            "works": [
                {
                    "title": "静夜思",
                    "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
                    "author": "李白",
                    "dynasty": "唐代",
                    "type": "五言绝句",
                    "theme": "思乡"
                },
                {
                    "title": "春望",
                    "content": "国破山河在，城春草木深。感时花溅泪，恨别鸟惊心。",
                    "author": "杜甫",
                    "dynasty": "唐代",
                    "type": "五言律诗",
                    "theme": "爱国"
                },
                {
                    "title": "水调歌头·明月几时有",
                    "content": "明月几时有？把酒问青天。不知天上宫阙，今夕是何年。",
                    "author": "苏轼",
                    "dynasty": "宋代",
                    "type": "词",
                    "theme": "哲理"
                }
            ],
            "dynasties": [
                {"name": "唐代", "period": "618-907年", "capital": "长安"},
                {"name": "宋代", "period": "960-1279年", "capital": "开封/临安"}
            ]
        }
    
    def get_author_info(self, author_name: str) -> Optional[Dict[str, Any]]:
        """
        获取诗人信息
        
        Args:
            author_name: 诗人姓名
            
        Returns:
            诗人信息字典
        """
        if self.graph:
            try:
                query = """
                MATCH (a:Author {name: $name})
                RETURN a.name as name, a.dynasty as dynasty, a.gender as gender,
                       a.birth_year as birth_year, a.death_year as death_year,
                       a.style as style, a.description as description
                """
                result = self.graph.run(query, name=author_name).data()
                if result:
                    return result[0]
            except DatabaseError as e:
                logger.error(f"查询诗人信息失败: {e}")
        
        # 返回模拟数据
        for author in self.mock_data["authors"]:
            if author["name"] == author_name:
                return author
        return None
    
    def get_author_works(self, author_name: str) -> List[Dict[str, Any]]:
        """
        获取诗人的作品
        
        Args:
            author_name: 诗人姓名
            
        Returns:
            作品列表
        """
        if self.graph:
            try:
                query = """
                MATCH (a:Author {name: $author_name})-[:CREATE]->(w:Work)
                RETURN w.title as title, w.content as content, w.type as type,
                       w.theme as theme, w.dynasty as dynasty
                ORDER BY w.title
                """
                results = self.graph.run(query, author_name=author_name).data()
                return results
            except DatabaseError as e:
                logger.error(f"查询诗人作品失败: {e}")
        
        # 返回模拟数据
        works = []
        for work in self.mock_data["works"]:
            if work["author"] == author_name:
                works.append(work)
        return works
    
    def get_work_info(self, work_title: str) -> Optional[Dict[str, Any]]:
        """
        获取作品信息
        
        Args:
            work_title: 作品标题
            
        Returns:
            作品信息字典
        """
        if self.graph:
            try:
                query = """
                MATCH (w:Work {title: $title})<-[:CREATE]-(a:Author)
                RETURN w.title as title, w.content as content, w.type as type,
                       w.theme as theme, w.dynasty as dynasty,
                       a.name as author, a.dynasty as author_dynasty
                """
                result = self.graph.run(query, title=work_title).data()
                if result:
                    return result[0]
            except DatabaseError as e:
                logger.error(f"查询作品信息失败: {e}")
        
        # 返回模拟数据
        for work in self.mock_data["works"]:
            if work["title"] == work_title:
                return work
        return None
    
    def get_dynasty_authors(self, dynasty_name: str) -> List[Dict[str, Any]]:
        """
        获取朝代的诗人
        
        Args:
            dynasty_name: 朝代名称
            
        Returns:
            诗人列表
        """
        if self.graph:
            try:
                query = """
                MATCH (a:Author {dynasty: $dynasty})
                RETURN a.name as name, a.birth_year as birth_year, 
                       a.death_year as death_year, a.style as style
                ORDER BY a.name
                """
                results = self.graph.run(query, dynasty=dynasty_name).data()
                return results
            except DatabaseError as e:
                logger.error(f"查询朝代诗人失败: {e}")
        
        # 返回模拟数据
        authors = []
        for author in self.mock_data["authors"]:
            if author["dynasty"] == dynasty_name:
                authors.append(author)
        return authors
    
    def get_dynasty_info(self, dynasty_name: str) -> Optional[Dict[str, Any]]:
        """
        获取朝代信息
        
        Args:
            dynasty_name: 朝代名称
            
        Returns:
            朝代信息字典
        """
        if self.graph:
            try:
                query = """
                MATCH (d:Dynasty {name: $name})
                RETURN d.name as name, d.period as period, d.capital as capital
                """
                result = self.graph.run(query, name=dynasty_name).data()
                if result:
                    return result[0]
            except DatabaseError as e:
                logger.error(f"查询朝代信息失败: {e}")
        
        # 返回模拟数据
        for dynasty in self.mock_data["dynasties"]:
            if dynasty["name"] == dynasty_name:
                return dynasty
        return None
    
    def search_poetry_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """
        按主题搜索诗词
        
        Args:
            theme: 主题关键词
            
        Returns:
            相关诗词列表
        """
        if self.graph:
            try:
                query = """
                MATCH (w:Work)
                WHERE w.theme CONTAINS $theme OR w.content CONTAINS $theme
                RETURN w.title as title, w.content as content, w.type as type,
                       w.theme as theme, w.dynasty as dynasty
                LIMIT 10
                """
                results = self.graph.run(query, theme=theme).data()
                return results
            except DatabaseError as e:
                logger.error(f"按主题搜索诗词失败: {e}")
        
        # 返回模拟数据
        works = []
        for work in self.mock_data["works"]:
            if theme in work.get("theme", "") or theme in work.get("content", ""):
                works.append(work)
        return works
    
    def get_famous_sentences(self, author_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取名句
        
        Args:
            author_name: 诗人姓名（可选）
            limit: 返回数量限制
            
        Returns:
            名句列表
        """
        if self.graph:
            try:
                if author_name:
                    query = """
                    MATCH (a:Author {name: $author_name})-[:CREATE]->(fs:FamousSentence)
                    RETURN fs.content as content, fs.title as title
                    LIMIT $limit
                    """
                    results = self.graph.run(query, author_name=author_name, limit=limit).data()
                else:
                    query = """
                    MATCH (fs:FamousSentence)
                    RETURN fs.content as content, fs.title as title
                    LIMIT $limit
                    """
                    results = self.graph.run(query, limit=limit).data()
                return results
            except DatabaseError as e:
                logger.error(f"获取名句失败: {e}")
        
        # 返回模拟数据
        famous_sentences = [
            {"content": "床前明月光，疑是地上霜。", "title": "静夜思"},
            {"content": "举头望明月，低头思故乡。", "title": "静夜思"},
            {"content": "国破山河在，城春草木深。", "title": "春望"},
            {"content": "明月几时有？把酒问青天。", "title": "水调歌头"}
        ]
        return famous_sentences[:limit]
    
    def execute_cypher_query(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        """
        执行自定义Cypher查询
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            
        Returns:
            查询结果列表
        """
        if self.graph:
            try:
                if parameters:
                    results = self.graph.run(query, **parameters).data()
                else:
                    results = self.graph.run(query).data()
                return results
            except DatabaseError as e:
                logger.error(f"Cypher查询执行失败: {e}")
                return []
        
        return []
    
    def get_graph_stats(self) -> Dict[str, int]:
        """
        获取图谱统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "authors": 0,
            "works": 0,
            "dynasties": 0,
            "famous_sentences": 0,
            "relationships": 0
        }
        
        if self.graph:
            try:
                # 统计作者数量
                query = "MATCH (a:Author) RETURN count(a) as count"
                result = self.graph.run(query).data()
                stats["authors"] = result[0]["count"] if result else 0
                
                # 统计作品数量
                query = "MATCH (w:Work) RETURN count(w) as count"
                result = self.graph.run(query).data()
                stats["works"] = result[0]["count"] if result else 0
                
                # 统计朝代数量
                query = "MATCH (d:Dynasty) RETURN count(d) as count"
                result = self.graph.run(query).data()
                stats["dynasties"] = result[0]["count"] if result else 0
                
                # 统计名句数量
                query = "MATCH (fs:FamousSentence) RETURN count(fs) as count"
                result = self.graph.run(query).data()
                stats["famous_sentences"] = result[0]["count"] if result else 0
                
                # 统计关系数量
                query = "MATCH ()-[r]->() RETURN count(r) as count"
                result = self.graph.run(query).data()
                stats["relationships"] = result[0]["count"] if result else 0
                
            except DatabaseError as e:
                logger.error(f"获取图谱统计信息失败: {e}")
        
        else:
            # 使用模拟数据
            stats["authors"] = len(self.mock_data["authors"])
            stats["works"] = len(self.mock_data["works"])
            stats["dynasties"] = len(self.mock_data["dynasties"])
            stats["famous_sentences"] = 4
            stats["relationships"] = 15
        
        return stats


# 全局知识图谱实例
poetry_kg = PoetryKnowledgeGraph()


if __name__ == "__main__":
    # 测试知识图谱功能
    print("测试古诗词知识图谱...")
    
    # 获取统计信息
    stats = poetry_kg.get_graph_stats()
    print(f"图谱统计: {stats}")
    
    # 测试诗人信息查询
    author_info = poetry_kg.get_author_info("李白")
    print(f"李白信息: {author_info}")
    
    # 测试作品查询
    works = poetry_kg.get_author_works("李白")
    print(f"李白作品数量: {len(works)}")
    
    # 测试作品信息查询
    work_info = poetry_kg.get_work_info("静夜思")
    print(f"静夜思信息: {work_info}")
    
    print("测试完成！")