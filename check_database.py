#!/usr/bin/env python3
import sqlite3
import os

db_path = os.path.join('llmhomework_Backend', 'database', 'knowledge_base.db')

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'  - {table[0]}')

print('\n各表的数据量:')
for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'  {table_name}: {count} 条记录')

# 查看具体数据示例
if tables:
    print('\n查看一些示例数据:')
    for table in tables[:3]:  # 只看前3个表
        table_name = table[0]
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 2')
        rows = cursor.fetchall()
        if rows:
            print(f'\n{table_name}表的前2条记录:')
            for row in rows:
                print(f'  {row}')

conn.close()
print('\n数据库检查完成')
