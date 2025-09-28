#!/usr/bin/env python3
"""
统一数据收集运行脚本
支持多种收集方式和运行模式
"""

import os
import sys
import logging
from datetime import datetime

# 设置路径
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    print("🚀 启动统一数据收集系统...")
    print("📚 支持AI生成、网站爬虫、PDF处理等多种方式")
    print("⚖️ 严格遵守网站使用条款和robots.txt")
    
    try:
        # 使用统一的数据收集管理器
        from data_collection_manager import DataCollectionManager
        
        manager = DataCollectionManager()
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            method = sys.argv[1]
            
            if method in ['ai', 'crawl', 'pdf', 'all']:
                print(f"\n🎯 使用指定方式收集数据: {method}")
                success = manager.collect_data_by_method(method)
                
                if success:
                    print(f"\n🎉 数据收集 ({method}) 完成!")
                    
                    # 询问是否运行完整处理流程
                    choice = input("是否运行完整处理流程? (y/n) [y]: ").strip().lower()
                    if choice in ['', 'y', 'yes']:
                        print("\n🔄 开始运行完整处理流程...")
                        full_success = manager.run_full_collection_pipeline(include_import=True)
                        if full_success:
                            print("🎉 完整流程执行成功!")
                        else:
                            print("❌ 完整流程执行失败")
                else:
                    print(f"❌ 数据收集 ({method}) 失败")
                    
            elif method == 'full':
                print("\n🔄 运行完整数据收集和处理流程...")
                success = manager.run_full_collection_pipeline(include_import=True)
                if success:
                    print("🎉 完整流程执行成功!")
                else:
                    print("❌ 完整流程执行失败")
                    
            elif method == 'interactive':
                manager.run_interactive_mode()
                
            else:
                print(f"❌ 未知收集方式: {method}")
                print("可用方式: ai, crawl, pdf, all, full, interactive")
        else:
            # 默认交互模式
            print("\n🎯 进入交互模式...")
            manager.run_interactive_mode()
            
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()