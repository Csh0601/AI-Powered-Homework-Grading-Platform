#!/usr/bin/env python3
"""
简化的数据导入脚本
直接导入生成的数据到数据库
"""

import os
import sys
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simple_import_to_database():
    """简化的数据库导入"""
    logger.info("💾 开始简化数据导入...")

    try:
        # 数据库路径
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "knowledge_base.db")

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查找数据文件
        raw_dir = os.path.join(os.path.dirname(__file__), "..", "collectors", "raw", "subjects")
        subjects = ['math', 'chinese', 'english', 'physics', 'chemistry', 'biology']

        total_imported_kp = 0
        total_imported_q = 0

        for subject in subjects:
            subject_dir = os.path.join(raw_dir, subject)

            # 导入知识点
            kp_dir = os.path.join(subject_dir, "knowledge_points")
            if os.path.exists(kp_dir):
                kp_files = [f for f in os.listdir(kp_dir) if f.endswith('.csv')]
                for kp_file in kp_files:
                    file_path = os.path.join(kp_dir, kp_file)
                    try:
                        df = pd.read_csv(file_path)
                        for _, row in df.iterrows():
                            # 插入知识点
                            cursor.execute("""
                                INSERT OR IGNORE INTO knowledge_points
                                (knowledge_point_id, name, subject, difficulty_level, description)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                f"auto_kp_{total_imported_kp + 1}",
                                str(row.get('name', '')),
                                subject,
                                int(row.get('difficulty_level', 1)),
                                str(row.get('description', ''))
                            ))
                            total_imported_kp += 1

                        logger.info(f"✅ 已导入知识点: {kp_file} ({len(df)} 条)")
                    except Exception as e:
                        logger.error(f"❌ 导入知识点失败 {kp_file}: {e}")

            # 导入题目
            for question_type in ['exam_questions', 'mock_questions']:
                q_dir = os.path.join(subject_dir, question_type)
                if os.path.exists(q_dir):
                    q_files = [f for f in os.listdir(q_dir) if f.endswith('.csv')]
                    for q_file in q_files:
                        file_path = os.path.join(q_dir, q_file)
                        try:
                            df = pd.read_csv(file_path)
                            for _, row in df.iterrows():
                                # 插入题目
                                cursor.execute("""
                                    INSERT OR IGNORE INTO questions
                                    (question_id, subject, number, stem, answer, type, difficulty_level)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    f"auto_q_{total_imported_q + 1}",
                                    subject,
                                    str(row.get('number', total_imported_q + 1)),
                                    str(row.get('stem', '')),
                                    str(row.get('correct_answer', '')),
                                    str(row.get('question_type', 'choice')),
                                    int(row.get('difficulty_level', 1))
                                ))
                                total_imported_q += 1

                            logger.info(f"✅ 已导入题目: {q_file} ({len(df)} 条)")
                        except Exception as e:
                            logger.error(f"❌ 导入题目失败 {q_file}: {e}")

        # 提交事务
        conn.commit()

        # 统计最终结果
        cursor.execute("SELECT COUNT(*) FROM knowledge_points")
        kp_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM questions")
        q_count = cursor.fetchone()[0]

        conn.close()

        logger.info("🎉 数据导入完成！")
        logger.info(f"📊 导入统计:")
        logger.info(f"  - 知识点: {kp_count} 条")
        logger.info(f"  - 题目: {q_count} 条")

        return True

    except Exception as e:
        logger.error(f"❌ 数据导入失败: {e}")
        return False

if __name__ == "__main__":
    simple_import_to_database()

