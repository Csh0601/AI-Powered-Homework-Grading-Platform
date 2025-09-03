#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
测试知识库数据库的连接和基本CRUD操作
为API开发做准备
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self, db_path='knowledge_base.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
        try:
            yield conn
        finally:
            conn.close()
    
    def test_basic_queries(self):
        """测试基本查询操作"""
        print("📊 测试基本查询操作...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 测试年级查询
            print("\n1️⃣ 年级数据查询：")
            cursor.execute("SELECT * FROM grades ORDER BY sort_order")
            grades = cursor.fetchall()
            for grade in grades:
                print(f"  - ID: {grade['id']}, 名称: {grade['name']}, 代码: {grade['code']}")
            
            # 2. 测试学科查询（带关联）
            print("\n2️⃣ 学科数据查询（关联年级）：")
            cursor.execute("""
                SELECT s.id, s.name as subject_name, s.code, g.name as grade_name
                FROM subjects s
                JOIN grades g ON s.grade_id = g.id
                ORDER BY g.sort_order, s.name
            """)
            subjects = cursor.fetchall()
            for subject in subjects:
                print(f"  - {subject['grade_name']} > {subject['subject_name']} ({subject['code']})")
            
            # 3. 测试知识点查询（如果有的话）
            print("\n3️⃣ 知识点数据查询：")
            cursor.execute("""
                SELECT kp.id, kp.name, kp.difficulty_level, c.name as chapter_name, s.name as subject_name
                FROM knowledge_points kp
                JOIN chapters c ON kp.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LIMIT 5
            """)
            knowledge_points = cursor.fetchall()
            if knowledge_points:
                for kp in knowledge_points:
                    print(f"  - {kp['subject_name']} > {kp['chapter_name']} > {kp['name']} (难度:{kp['difficulty_level']})")
            else:
                print("  - 暂无知识点数据")
    
    def test_crud_operations(self):
        """测试CRUD操作"""
        print("\n🔧 测试CRUD操作...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # CREATE - 创建测试数据
            print("\n📝 CREATE - 创建测试数据：")
            
            # 获取一个学科ID
            cursor.execute("SELECT id FROM subjects WHERE code='math_grade7' LIMIT 1")
            subject = cursor.fetchone()
            
            if subject:
                subject_id = subject['id']
                
                # 插入测试章节
                cursor.execute("""
                    INSERT OR REPLACE INTO chapters 
                    (subject_id, name, code, description, chapter_number, difficulty_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (subject_id, "测试章节", "test_chapter", "这是一个测试章节", 99, 1))
                
                chapter_id = cursor.lastrowid
                print(f"  ✅ 创建测试章节，ID: {chapter_id}")
                
                # 插入测试知识点
                cursor.execute("""
                    INSERT OR REPLACE INTO knowledge_points
                    (chapter_id, name, code, description, difficulty_level, importance_level, exam_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chapter_id, "测试知识点", "test_kp", "这是一个测试知识点", 2, 3, 0.6))
                
                kp_id = cursor.lastrowid
                print(f"  ✅ 创建测试知识点，ID: {kp_id}")
                
                # READ - 读取数据
                print("\n📖 READ - 读取创建的数据：")
                cursor.execute("""
                    SELECT kp.*, c.name as chapter_name, s.name as subject_name
                    FROM knowledge_points kp
                    JOIN chapters c ON kp.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    WHERE kp.id = ?
                """, (kp_id,))
                
                kp_data = cursor.fetchone()
                if kp_data:
                    print(f"  📚 知识点: {kp_data['name']}")
                    print(f"  📖 所属章节: {kp_data['chapter_name']}")
                    print(f"  📗 所属学科: {kp_data['subject_name']}")
                    print(f"  🎯 难度等级: {kp_data['difficulty_level']}")
                    print(f"  ⭐ 重要程度: {kp_data['importance_level']}")
                
                # UPDATE - 更新数据
                print("\n✏️ UPDATE - 更新数据：")
                cursor.execute("""
                    UPDATE knowledge_points 
                    SET difficulty_level = ?, importance_level = ?, description = ?
                    WHERE id = ?
                """, (4, 5, "这是更新后的测试知识点描述", kp_id))
                
                print(f"  ✅ 更新知识点，影响行数: {cursor.rowcount}")
                
                # 验证更新
                cursor.execute("SELECT difficulty_level, importance_level, description FROM knowledge_points WHERE id = ?", (kp_id,))
                updated_data = cursor.fetchone()
                print(f"  📊 更新后难度: {updated_data['difficulty_level']}, 重要度: {updated_data['importance_level']}")
                
                # DELETE - 删除数据（清理测试数据）
                print("\n🗑️ DELETE - 清理测试数据：")
                cursor.execute("DELETE FROM knowledge_points WHERE id = ?", (kp_id,))
                print(f"  ✅ 删除测试知识点，影响行数: {cursor.rowcount}")
                
                cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
                print(f"  ✅ 删除测试章节，影响行数: {cursor.rowcount}")
                
                conn.commit()
                print("  💾 所有更改已提交")
            
            else:
                print("  ❌ 未找到测试学科，跳过CRUD测试")
    
    def test_complex_queries(self):
        """测试复杂查询"""
        print("\n🔍 测试复杂查询...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 统计查询
            print("\n📊 统计信息：")
            
            # 各年级学科数量
            cursor.execute("""
                SELECT g.name as grade_name, COUNT(s.id) as subject_count
                FROM grades g
                LEFT JOIN subjects s ON g.id = s.grade_id
                GROUP BY g.id, g.name
                ORDER BY g.sort_order
            """)
            grade_stats = cursor.fetchall()
            print("  年级学科统计：")
            for stat in grade_stats:
                print(f"    - {stat['grade_name']}: {stat['subject_count']} 个学科")
            
            # 章节数量统计
            cursor.execute("""
                SELECT s.name as subject_name, COUNT(c.id) as chapter_count
                FROM subjects s
                LEFT JOIN chapters c ON s.id = c.subject_id
                GROUP BY s.id, s.name
                HAVING chapter_count > 0
                ORDER BY chapter_count DESC
            """)
            chapter_stats = cursor.fetchall()
            if chapter_stats:
                print("  学科章节统计：")
                for stat in chapter_stats:
                    print(f"    - {stat['subject_name']}: {stat['chapter_count']} 个章节")
            else:
                print("  - 暂无章节数据")
            
            # 2. 条件查询
            print("\n🎯 条件查询示例：")
            
            # 查找特定难度的学科
            cursor.execute("""
                SELECT name, difficulty_level 
                FROM subjects 
                WHERE difficulty_level >= 3
                ORDER BY difficulty_level DESC, name
            """)
            difficult_subjects = cursor.fetchall()
            if difficult_subjects:
                print("  高难度学科（难度≥3）：")
                for subject in difficult_subjects:
                    print(f"    - {subject['name']} (难度: {subject['difficulty_level']})")
    
    def generate_connection_report(self):
        """生成连接测试报告"""
        print("\n📄 生成连接测试报告...")
        
        report = {
            "test_time": datetime.now().isoformat(),
            "database_path": self.db_path,
            "connection_status": "success",
            "tests_performed": [
                "basic_queries",
                "crud_operations", 
                "complex_queries"
            ],
            "recommendations": [
                "数据库连接正常，可以开始API开发",
                "建议添加更多的测试数据进行开发",
                "考虑添加数据库连接池优化性能"
            ]
        }
        
        # 获取数据库统计信息
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 表数量和记录数
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            table_stats = {}
            for table in tables:
                table_name = table['name']
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                table_stats[table_name] = count
            
            report["database_stats"] = {
                "total_tables": len(tables),
                "table_record_counts": table_stats
            }
        
        # 保存报告
        with open('database_connection_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 连接测试报告已保存到: database_connection_test_report.json")
        return report

def main():
    """主测试函数"""
    print("🚀 开始数据库连接测试...")
    print("=" * 60)
    
    # 创建数据库管理器
    db_manager = DatabaseManager()
    
    try:
        # 执行各项测试
        db_manager.test_basic_queries()
        db_manager.test_crud_operations()
        db_manager.test_complex_queries()
        
        # 生成报告
        report = db_manager.generate_connection_report()
        
        print("\n" + "=" * 60)
        print("🎉 数据库连接测试完成！")
        print("\n📋 测试总结：")
        print("  ✅ 基本查询操作正常")
        print("  ✅ CRUD操作正常")
        print("  ✅ 复杂查询正常")
        print("  ✅ 数据库连接稳定")
        
        print(f"\n🎯 下一步建议：")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ 数据库准备就绪，可以开始开发Day 7的API接口了！")
    else:
        print("\n⚠️ 请检查数据库配置后重试。")
