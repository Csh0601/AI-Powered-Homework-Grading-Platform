#!/usr/bin/env python3
"""
创建大规模题目答案数据库
Day 9: 构建大规模题目答案数据库 - 目标1000+题目标准库
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
import json

# 设置路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_question_bank():
    """创建大规模题目答案数据库"""
    logger.info("🚀 开始创建大规模题目答案数据库...")
    
    # 设置路径
    base_dir = Path(__file__).parent
    raw_dir = base_dir / "raw" / "subjects"
    output_dir = base_dir / "data_collection" / "processed"
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_questions = []
    all_knowledge_points = []
    
    # 遍历所有学科目录
    for subject_dir in raw_dir.iterdir():
        if not subject_dir.is_dir():
            continue
            
        subject_name = subject_dir.name
        logger.info(f"📚 处理学科: {subject_name}")
        
        # 处理知识点
        kp_dir = subject_dir / "knowledge_points"
        if kp_dir.exists():
            for kp_file in kp_dir.glob("*.csv"):
                try:
                    df = pd.read_csv(kp_file, encoding='utf-8')
                    df['subject'] = subject_name
                    all_knowledge_points.append(df)
                    logger.info(f"  ✅ 加载知识点: {kp_file.name} ({len(df)}条)")
                except Exception as e:
                    logger.error(f"  ❌ 加载知识点失败: {kp_file.name} - {e}")
        
        # 处理题目
        for question_type in ["exam_questions", "mock_questions"]:
            q_dir = subject_dir / question_type
            if q_dir.exists():
                for q_file in q_dir.glob("*.csv"):
                    try:
                        df = pd.read_csv(q_file, encoding='utf-8')
                        df['subject'] = subject_name
                        df['source_type'] = question_type
                        all_questions.append(df)
                        logger.info(f"  ✅ 加载题目: {q_file.name} ({len(df)}条)")
                    except Exception as e:
                        logger.error(f"  ❌ 加载题目失败: {q_file.name} - {e}")
    
    # 合并所有数据
    if all_questions:
        questions_combined = pd.concat(all_questions, ignore_index=True)
        
        # 数据清洗和标准化
        questions_combined = clean_and_standardize_questions(questions_combined)
        
        # 保存统一题目库
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        questions_file = output_dir / f"question_bank_unified_{timestamp}.csv"
        questions_combined.to_csv(questions_file, index=False, encoding='utf-8')
        
        logger.info(f"✅ 题目库创建完成: {questions_file}")
        logger.info(f"📊 题目统计:")
        logger.info(f"  - 总题目数: {len(questions_combined)}")
        
        # 按学科统计
        subject_stats = questions_combined['subject'].value_counts()
        for subject, count in subject_stats.items():
            logger.info(f"  - {subject}: {count}道题目")
        
        # 按题型统计
        type_stats = questions_combined['question_type'].value_counts()
        for qtype, count in type_stats.items():
            logger.info(f"  - {qtype}: {count}道题目")
        
        # 按难度统计
        if 'difficulty_level' in questions_combined.columns:
            difficulty_stats = questions_combined['difficulty_level'].value_counts()
            for level, count in difficulty_stats.items():
                logger.info(f"  - 难度{level}: {count}道题目")
        
        # 生成统计报告
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(questions_combined),
            "subjects": subject_stats.to_dict(),
            "question_types": type_stats.to_dict(),
            "difficulty_distribution": difficulty_stats.to_dict() if 'difficulty_level' in questions_combined.columns else {},
            "files_processed": len(all_questions),
            "target_achieved": len(questions_combined) >= 1000
        }
        
        stats_file = output_dir / f"question_bank_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📈 统计报告已保存: {stats_file}")
        
        # 检查是否达到1000+目标
        if len(questions_combined) >= 1000:
            logger.info("🎉 恭喜！已达到1000+题目的目标！")
        else:
            logger.info(f"⚠️ 当前题目数量: {len(questions_combined)}，距离1000+目标还差 {1000 - len(questions_combined)}道题目")
        
        return questions_file, stats
    else:
        logger.error("❌ 没有找到任何题目数据")
        return None, None

def clean_and_standardize_questions(df):
    """清洗和标准化题目数据"""
    logger.info("🧹 开始清洗和标准化题目数据...")
    
    # 去重
    initial_count = len(df)
    df = df.drop_duplicates(subset=['question_id'], keep='first')
    logger.info(f"  - 去重: {initial_count} -> {len(df)} (移除{initial_count - len(df)}条重复)")
    
    # 填充缺失值
    df['difficulty_level'] = df['difficulty_level'].fillna(3)  # 默认中等难度
    df['score'] = df['score'].fillna(5)  # 默认5分
    df['time_limit'] = df['time_limit'].fillna(3)  # 默认3分钟
    
    # 标准化题目类型
    type_mapping = {
        'choice': 'multiple_choice',
        'fill_blank': 'fill_blank',
        'calculation': 'calculation',
        'application': 'application',
        'essay': 'essay'
    }
    df['question_type'] = df['question_type'].map(type_mapping).fillna(df['question_type'])
    
    # 标准化学科名称
    subject_mapping = {
        'math': '数学',
        'chinese': '语文',
        'english': '英语',
        'physics': '物理',
        'chemistry': '化学',
        'biology': '生物',
        'history': '历史',
        'geography': '地理',
        'politics': '政治'
    }
    df['subject'] = df['subject'].map(subject_mapping).fillna(df['subject'])
    
    # 添加质量评分
    df['quality_score'] = calculate_quality_score(df)
    
    # 添加答案多样性支持
    df['alternative_answers'] = df.apply(lambda x: generate_alternative_answers(x), axis=1)
    
    logger.info("✅ 数据清洗和标准化完成")
    return df

def calculate_quality_score(row):
    """计算题目质量评分"""
    score = 5.0  # 基础分
    
    # 根据题目长度调整
    if len(str(row.get('stem', ''))) > 50:
        score += 1.0
    
    # 根据解析长度调整
    if len(str(row.get('explanation', ''))) > 20:
        score += 1.0
    
    # 根据选项数量调整（选择题）
    if row.get('question_type') == 'multiple_choice':
        options = str(row.get('options', ''))
        if options and len(options.split('|')) >= 4:
            score += 1.0
    
    # 根据知识点数量调整
    knowledge_points = str(row.get('knowledge_points', ''))
    if knowledge_points and len(knowledge_points.split(',')) >= 2:
        score += 1.0
    
    return min(score, 10.0)  # 最高10分

def generate_alternative_answers(row):
    """生成可接受的替代答案"""
    correct_answer = str(row.get('correct_answer', ''))
    if not correct_answer:
        return []
    
    alternatives = []
    
    # 对于数学题，生成数值相近的答案
    if row.get('subject') == '数学' and correct_answer.replace('.', '').replace('-', '').isdigit():
        try:
            num = float(correct_answer)
            alternatives.append(str(num + 0.1))
            alternatives.append(str(num - 0.1))
        except:
            pass
    
    # 对于选择题，添加其他选项
    if row.get('question_type') == 'multiple_choice':
        options = str(row.get('options', ''))
        if options:
            option_list = options.split('|')
            for option in option_list:
                if option.strip() != correct_answer.strip():
                    alternatives.append(option.strip())
    
    return alternatives[:3]  # 最多3个替代答案

if __name__ == "__main__":
    questions_file, stats = create_question_bank()
    if questions_file:
        logger.info("🎉 大规模题目答案数据库创建完成！")
        logger.info(f"📁 文件位置: {questions_file}")
        if stats and stats['target_achieved']:
            logger.info("✅ 已达到1000+题目的目标！")
    else:
        logger.error("❌ 题目库创建失败")
