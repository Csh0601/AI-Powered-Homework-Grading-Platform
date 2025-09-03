#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库验证脚本
验证知识库数据库的创建和基础数据
"""

import sqlite3
import json
from datetime import datetime

def verify_database():
    """验证数据库结构和基础数据"""
    
    print("🔍 开始验证数据库...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect('knowledge_base.db')
        cursor = conn.cursor()
        
        # 1. 检查表结构
        print("\n📊 检查数据库表结构：")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        expected_tables = [
            'grades', 'subjects', 'chapters', 'knowledge_points',
            'questions', 'question_options', 'question_knowledge_association',
            'knowledge_relationship', 'knowledge_point_keywords',
            'grading_results', 'task_records', 'learning_records', 'user_profiles',
            'tags', 'question_tags', 'textbooks', 'exam_papers', 'question_banks'
        ]
        
        table_names = [table[0] for table in tables]
        
        for table in expected_tables:
            if table in table_names:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - 缺失")
        
        print(f"\n📈 总计：{len(table_names)} 个表（预期：{len(expected_tables)} 个）")
        
        # 2. 检查基础数据
        print("\n📋 检查基础数据：")
        
        # 年级数据
        cursor.execute("SELECT COUNT(*) FROM grades")
        grade_count = cursor.fetchone()[0]
        print(f"  年级数据：{grade_count} 条")
        
        if grade_count > 0:
            cursor.execute("SELECT name, code FROM grades ORDER BY sort_order")
            grades = cursor.fetchall()
            for grade in grades:
                print(f"    - {grade[0]} ({grade[1]})")
        
        # 学科数据
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        print(f"  学科数据：{subject_count} 条")
        
        if subject_count > 0:
            cursor.execute("""
                SELECT s.name, s.code, g.name as grade_name 
                FROM subjects s 
                JOIN grades g ON s.grade_id = g.id 
                ORDER BY g.sort_order, s.name
            """)
            subjects = cursor.fetchall()
            for subject in subjects:
                print(f"    - {subject[2]} - {subject[0]} ({subject[1]})")
        
        # 标签数据
        cursor.execute("SELECT COUNT(*) FROM tags")
        tag_count = cursor.fetchone()[0]
        print(f"  标签数据：{tag_count} 条")
        
        if tag_count > 0:
            cursor.execute("SELECT name, category FROM tags ORDER BY category, name")
            tags = cursor.fetchall()
            for tag in tags:
                print(f"    - {tag[0]} ({tag[1]})")
        
        # 3. 检查表结构详情（示例：knowledge_points表）
        print("\n🏗️ 知识点表结构示例：")
        cursor.execute("PRAGMA table_info(knowledge_points)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
        
        # 4. 测试插入和查询
        print("\n🧪 测试基本操作：")
        
        # 测试插入章节
        test_subject_id = cursor.execute("SELECT id FROM subjects WHERE code='math_grade7'").fetchone()
        if test_subject_id:
            subject_id = test_subject_id[0]
            
            # 插入测试章节
            cursor.execute("""
                INSERT OR IGNORE INTO chapters 
                (subject_id, name, code, description, chapter_number, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (subject_id, "有理数", "chapter_rational_numbers", "有理数的概念和运算", 1, 2))
            
            # 插入测试知识点
            chapter_id = cursor.execute("SELECT id FROM chapters WHERE code='chapter_rational_numbers'").fetchone()
            if chapter_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO knowledge_points
                    (chapter_id, name, code, description, difficulty_level, importance_level, exam_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chapter_id[0], "有理数的概念", "kp_rational_concept", 
                     "理解有理数的定义，掌握正数、负数和零的概念", 2, 4, 0.8))
                
                conn.commit()
                print("  ✅ 成功插入测试数据（章节+知识点）")
        
        # 5. 生成验证报告
        report = {
            "validation_time": datetime.now().isoformat(),
            "database_file": "knowledge_base.db",
            "total_tables": len(table_names),
            "expected_tables": len(expected_tables),
            "missing_tables": [t for t in expected_tables if t not in table_names],
            "basic_data": {
                "grades": grade_count,
                "subjects": subject_count,
                "tags": tag_count
            },
            "status": "success" if len(table_names) == len(expected_tables) else "warning"
        }
        
        # 保存验证报告
        with open('database_validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        conn.close()
        
        print(f"\n🎉 数据库验证完成！")
        print(f"📄 验证报告已保存到: database_validation_report.json")
        
        if report["status"] == "success":
            print("✅ 所有预期表都已成功创建")
        else:
            print(f"⚠️ 有 {len(report['missing_tables'])} 个表缺失")
            
        return report
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    verify_database()
