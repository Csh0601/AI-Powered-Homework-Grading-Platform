#!/usr/bin/env python3
"""检查最终数据库状态"""

import sqlite3
import os

def check_database():
    db_path = 'llmhomework_Backend/database/knowledge_base.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询表结构和数据量
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print('数据库状态:')
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f'  {table_name}: {count} 条记录')

        # 查看一些示例数据
        print()
        print('示例数据:')

        # 知识点示例
        cursor.execute('SELECT name, subject, grade FROM knowledge_points LIMIT 3')
        kp_samples = cursor.fetchall()
        print('知识点示例:')
        for kp in kp_samples:
            print(f'  {kp[0]} | {kp[1]} | {kp[2]}')

        # 题目示例
        cursor.execute('SELECT question_id, subject, question_type, stem FROM questions LIMIT 3')
        q_samples = cursor.fetchall()
        print()
        print('题目示例:')
        for q in q_samples:
            print(f'  {q[0]} | {q[1]} | {q[2]} | {q[3][:50]}...')

        conn.close()
        print()
        print('数据库验证完成!')
    else:
        print('数据库文件不存在')

if __name__ == "__main__":
    check_database()

