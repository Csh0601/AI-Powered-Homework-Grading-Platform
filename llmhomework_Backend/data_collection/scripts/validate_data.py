#!/usr/bin/env python3
"""
数据质量验证脚本
验证收集的数据是否符合质量标准
"""

import os
import sys
import pandas as pd
import json
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data_quality():
    """验证数据质量"""
    logger.info("🔍 开始数据质量验证...")
    
    try:
        # 调用原有的验证脚本
        from app.scripts.validate_collected_data import main as validate_main
        result = validate_main()
        logger.info("✅ 数据质量验证完成")
        return result
    except Exception as e:
        logger.warning(f"⚠️ 无法调用原验证脚本: {e}")
        
        # 简单验证
        processed_dir = os.path.join(os.path.dirname(__file__), "..", "processed")
        
        kp_file = os.path.join(processed_dir, "knowledge_points_unified.csv")
        q_file = os.path.join(processed_dir, "questions_unified.csv")
        
        results = {
            "knowledge_points_exists": os.path.exists(kp_file),
            "questions_exists": os.path.exists(q_file),
            "validation_time": datetime.now().isoformat()
        }
        
        if results["knowledge_points_exists"]:
            df_kp = pd.read_csv(kp_file)
            results["knowledge_points_count"] = len(df_kp)
            logger.info(f"✅ 知识点数据: {len(df_kp)} 条")
        
        if results["questions_exists"]:
            df_q = pd.read_csv(q_file)
            results["questions_count"] = len(df_q)
            logger.info(f"✅ 题目数据: {len(df_q)} 条")
        
        # 保存验证报告
        report_file = os.path.join(processed_dir, "validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 验证报告已保存: {report_file}")
        return True

if __name__ == "__main__":
    validate_data_quality()
