#!/usr/bin/env python3
"""
简化的数据统一处理脚本
将不同来源的原始数据统一为标准格式
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

# 设置路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def unify_all_data():
    """统一处理所有数据"""
    logger.info("🔄 开始统一处理数据...")
    
    # 设置路径
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "raw" / "subjects"
    processed_dir = base_dir / "processed"
    
    # 确保processed目录存在
    processed_dir.mkdir(exist_ok=True)
    
    all_knowledge_points = []
    all_questions = []
    
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
    if all_knowledge_points:
        kp_combined = pd.concat(all_knowledge_points, ignore_index=True)
        kp_file = processed_dir / f"knowledge_points_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        kp_combined.to_csv(kp_file, index=False, encoding='utf-8')
        logger.info(f"✅ 知识点统一完成: {kp_file} ({len(kp_combined)}条)")
    else:
        kp_file = None
        logger.warning("⚠️ 没有找到知识点数据")
    
    if all_questions:
        q_combined = pd.concat(all_questions, ignore_index=True)
        q_file = processed_dir / f"questions_unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        q_combined.to_csv(q_file, index=False, encoding='utf-8')
        logger.info(f"✅ 题目统一完成: {q_file} ({len(q_combined)}条)")
    else:
        q_file = None
        logger.warning("⚠️ 没有找到题目数据")
    
    # 生成统计报告
    stats = {
        "timestamp": datetime.now().isoformat(),
        "knowledge_points_count": len(kp_combined) if all_knowledge_points else 0,
        "questions_count": len(q_combined) if all_questions else 0,
        "subjects_processed": len([d for d in raw_dir.iterdir() if d.is_dir()]),
        "files_processed": len(all_knowledge_points) + len(all_questions)
    }
    
    stats_file = processed_dir / f"unification_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    logger.info(f"📊 统一处理统计:")
    logger.info(f"  - 知识点: {stats['knowledge_points_count']}条")
    logger.info(f"  - 题目: {stats['questions_count']}条")
    logger.info(f"  - 处理学科: {stats['subjects_processed']}个")
    logger.info(f"  - 处理文件: {stats['files_processed']}个")
    
    return kp_file, q_file

if __name__ == "__main__":
    unify_all_data()
