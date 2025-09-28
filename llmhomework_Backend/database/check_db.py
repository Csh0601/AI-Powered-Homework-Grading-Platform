#!/usr/bin/env python3
import sqlite3

def check_database():
    """检查数据库状态"""
    try:
        conn = sqlite3.connect('knowledge_base.db')
        cursor = conn.cursor()
        
        # 获取所有表
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("🗄️ 数据库表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查知识点表
        try:
            kp_count = cursor.execute("SELECT COUNT(*) FROM knowledge_points").fetchone()[0]
            print(f"\n📚 知识点总数: {kp_count}")
        except Exception as e:
            print(f"\n⚠️ knowledge_points表错误: {e}")
        
        # 检查题目表
        try:
            q_count = cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
            print(f"📝 题目总数: {q_count}")
        except Exception as e:
            print(f"⚠️ questions表错误: {e}")
        
        conn.close()
        print("\n✅ 数据库检查完成")
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    check_database()
