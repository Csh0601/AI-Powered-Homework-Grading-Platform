#!/usr/bin/env python3
"""
导入爬取的数据到数据库
简化版本，直接使用数据存储服务
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime

# 添加路径
sys.path.append(os.path.dirname(__file__))

# 导入数据存储服务
from app.services.data_storage_service import DataStorageService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_crawled_data():
    """导入爬取的数据"""
    logger.info("🔄 开始导入爬取的数据...")
    
    try:
        # 初始化数据存储服务
        storage = DataStorageService()
        
        # 读取统一后的数据
        knowledge_file = "data_collection/processed/knowledge_points_unified.csv"
        questions_file = "data_collection/processed/questions_unified.csv"
        
        imported_count = 0
        
        # 导入知识点
        if os.path.exists(knowledge_file):
            logger.info(f"📚 导入知识点数据: {knowledge_file}")
            df_kp = pd.read_csv(knowledge_file)
            
            for _, row in df_kp.iterrows():
                kp_data = {
                    'knowledge_point_id': f"crawled_kp_{imported_count + 1}",
                    'name': str(row.get('name', '')),
                    'subject': str(row.get('subject', '综合')),
                    'grade': str(row.get('grade', 'Grade 8')),
                    'chapter': str(row.get('chapter', '未分类')),
                    'description': str(row.get('description', '')),
                    'difficulty_level': int(row.get('difficulty_level', 3)),
                    'importance_level': int(row.get('importance_level', 3)),
                    'keywords': str(row.get('keywords', '')).split('|')[:5],
                    'source': str(row.get('source', '爬虫数据'))
                }
                
                success = storage.save_knowledge_point(kp_data)
                if success:
                    imported_count += 1
            
            logger.info(f"✅ 知识点导入完成: {imported_count} 条")
        
        # 导入题目
        if os.path.exists(questions_file):
            logger.info(f"📝 导入题目数据: {questions_file}")
            df_q = pd.read_csv(questions_file)
            
            question_count = 0
            for _, row in df_q.iterrows():
                q_data = {
                    'question_id': str(row.get('question_id', f'crawled_q_{question_count + 1}')),
                    'stem': str(row.get('stem', '')),
                    'subject': str(row.get('subject', '综合')),
                    'grade': str(row.get('grade', 'Grade 8')),
                    'type': str(row.get('question_type', 'choice')),
                    'difficulty_level': int(row.get('difficulty_level', 3)),
                    'correct_answer': str(row.get('correct_answer', '')),
                    'explanation': str(row.get('explanation', '')),
                    'source': str(row.get('source', '爬虫数据'))
                }
                
                # 处理选项
                options = row.get('options', '')
                if pd.notna(options) and options:
                    try:
                        import json
                        q_data['options'] = json.loads(options)
                    except:
                        q_data['options'] = str(options).split(',')
                
                success = storage.save_question(q_data)
                if success:
                    question_count += 1
            
            logger.info(f"✅ 题目导入完成: {question_count} 条")
        
        # 简单统计
        logger.info("📊 数据库统计:")
        logger.info(f"  - 知识点已导入: {imported_count} 条")
        logger.info(f"  - 题目已导入: {question_count} 条")
        
        logger.info("🎉 数据导入完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据导入失败: {e}")
        return False

if __name__ == "__main__":
    print("🔄 开始导入爬取的数据到数据库...")
    success = import_crawled_data()
    
    if success:
        print("✅ 数据导入成功！")
        print("\n📋 后续操作建议:")
        print("1. 运行 python test_day7_complete.py 测试系统")
        print("2. 启动后端服务 python run.py")
        print("3. 测试知识匹配功能")
    else:
        print("❌ 数据导入失败")
