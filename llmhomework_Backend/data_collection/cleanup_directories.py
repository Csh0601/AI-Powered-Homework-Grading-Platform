#!/usr/bin/env python3
"""
清理和整理data_collection目录
"""

import os
import shutil
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_data_collection():
    """清理data_collection目录"""
    logger.info("🧹 开始清理data_collection目录...")
    
    base_dir = os.path.dirname(__file__)
    
    # 清理__pycache__目录
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            logger.info(f"🗑️ 删除缓存目录: {pycache_path}")
            shutil.rmtree(pycache_path, ignore_errors=True)
    
    # 清理临时文件
    temp_dir = os.path.join(base_dir, 'temp')
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            if file.endswith('.tmp') or file.endswith('.temp'):
                file_path = os.path.join(temp_dir, file)
                logger.info(f"🗑️ 删除临时文件: {file_path}")
                os.remove(file_path)
    
    # 整理crawled_data目录
    crawled_dir = os.path.join(base_dir, 'crawled_data')
    if os.path.exists(crawled_dir):
        # 只保留最新的文件
        files = []
        for file in os.listdir(crawled_dir):
            if file.endswith('.csv') or file.endswith('.json'):
                file_path = os.path.join(crawled_dir, file)
                stat = os.stat(file_path)
                files.append((file_path, stat.st_mtime))
        
        # 按时间排序，保留最新的3个文件
        files.sort(key=lambda x: x[1], reverse=True)
        for file_path, _ in files[3:]:
            logger.info(f"🗑️ 删除旧的爬取文件: {file_path}")
            os.remove(file_path)
    
    logger.info("✅ 目录清理完成")

def show_directory_structure():
    """显示目录结构"""
    logger.info("📁 当前目录结构:")
    
    base_dir = os.path.dirname(__file__)
    
    def print_tree(directory, prefix="", level=0):
        if level > 3:  # 限制深度
            return
        
        items = sorted(os.listdir(directory))
        for i, item in enumerate(items):
            if item.startswith('.') or item == '__pycache__':
                continue
            
            item_path = os.path.join(directory, item)
            is_last = i == len(items) - 1
            
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item}")
            
            if os.path.isdir(item_path):
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item_path, next_prefix, level + 1)
    
    print(f"\n📂 {os.path.basename(base_dir)}/")
    print_tree(base_dir)

if __name__ == "__main__":
    print("🧹 Data Collection 目录清理工具")
    print("=" * 40)
    
    choice = input("选择操作 (1: 清理, 2: 查看结构, 3: 全部): ").strip()
    
    if choice in ["1", "3"]:
        cleanup_data_collection()
    
    if choice in ["2", "3"]:
        show_directory_structure()
    
    print("\n✅ 操作完成")
