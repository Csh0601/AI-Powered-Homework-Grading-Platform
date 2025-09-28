#!/usr/bin/env python3
"""
数据收集系统重置脚本
清除所有现有数据并重新开始收集
"""

import os
import shutil
import sqlite3
from pathlib import Path

def cleanup_all_data():
    """清除所有数据并重置系统"""
    print("🧹 开始全面数据清理...")

    # 1. 清除原始数据目录
    raw_dir = Path("raw")
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
        print("✅ 已删除 raw/ 目录")

    # 2. 清除处理后的数据
    processed_dir = Path("processed")
    if processed_dir.exists():
        shutil.rmtree(processed_dir)
        print("✅ 已删除 processed/ 目录")

    # 3. 清除爬虫数据
    crawled_data_dir = Path("collectors/crawled_data")
    if crawled_data_dir.exists():
        # 保留目录本身，但删除内容
        for item in crawled_data_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print("✅ 已清空 collectors/crawled_data/ 目录")

    # 4. 清除质量种子数据
    quality_dir = Path("quality_seed_data")
    if quality_dir.exists():
        shutil.rmtree(quality_dir)
        print("✅ 已删除 quality_seed_data/ 目录")

    # 5. 清空数据库
    db_paths = [
        "llmhomework_Backend/database/knowledge_base.db",
        "collectors/crawled_data/crawl_progress.db"
    ]

    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"✅ 已删除数据库: {db_path}")
            except Exception as e:
                print(f"⚠️ 删除数据库失败 {db_path}: {e}")

    # 6. 清除缓存文件
    cache_files = [
        "collectors/generated_cache.json",
        "collectors/crawled_data/crawl_metadata_*.json"
    ]

    for cache_pattern in cache_files:
        if "*" in cache_pattern:
            # 查找匹配的文件
            pattern_path = Path(cache_pattern.replace("*", ""))
            if pattern_path.exists():
                for file in pattern_path.parent.glob(cache_pattern.replace("*", "*")):
                    try:
                        file.unlink()
                        print(f"✅ 已删除缓存文件: {file}")
                    except Exception as e:
                        print(f"⚠️ 删除缓存失败 {file}: {e}")
        else:
            cache_path = Path(cache_pattern)
            if cache_path.exists():
                cache_path.unlink()
                print(f"✅ 已删除缓存文件: {cache_path}")

    # 7. 清除临时文件
    temp_files = ["check_db_final.py", "analyze_website.py", "analyze_chinese_page.py"]
    for temp_file in temp_files:
        temp_path = Path(temp_file)
        if temp_path.exists():
            temp_path.unlink()
            print(f"✅ 已删除临时文件: {temp_file}")

    print("\n🎉 数据清理完成!")
    print("系统已重置，可以重新开始数据收集")

def show_cleanup_summary():
    """显示清理后的状态"""
    print("\n📊 清理后的系统状态:")

    # 检查主要目录
    directories = ["raw", "processed", "collectors/crawled_data", "quality_seed_data"]
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            item_count = len(list(path.rglob("*")))
            print(f"  {dir_path}: {item_count} 项")
        else:
            print(f"  {dir_path}: 不存在")

    # 检查数据库
    db_paths = ["llmhomework_Backend/database/knowledge_base.db", "collectors/crawled_data/crawl_progress.db"]
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"  {db_path}: 存在")
        else:
            print(f"  {db_path}: 不存在")

if __name__ == "__main__":
    cleanup_all_data()
    show_cleanup_summary()

