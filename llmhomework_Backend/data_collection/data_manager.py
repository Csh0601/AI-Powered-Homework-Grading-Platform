#!/usr/bin/env python3
"""
数据管理主工具
统一管理数据收集、处理和导入的完整流程
"""

import os
import sys
import logging
from datetime import datetime

# 设置路径
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        
    def collect_data(self, method="all"):
        """收集数据"""
        logger.info(f"🚀 开始数据收集: {method}")
        
        try:
            if method in ["all", "ai"]:
                logger.info("🤖 运行AI数据生成器...")
                from collectors.smart_data_generator import main as ai_main
                ai_main()
            
            if method in ["all", "crawl"]:
                logger.info("🌐 运行网站爬虫...")
                from collectors.legal_education_crawler import main as crawler_main
                crawler_main()
            
            if method in ["all", "pdf"]:
                logger.info("📄 运行PDF处理器...")
                from collectors.pdf_document_processor import main as pdf_main
                pdf_main()
            
            logger.info("✅ 数据收集完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据收集失败: {e}")
            return False
    
    def process_data(self):
        """处理数据"""
        logger.info("🔄 开始数据处理...")
        
        try:
            # 1. 统一数据格式
            from scripts.unify_data import unify_all_data
            unify_all_data()
            
            # 2. 验证数据质量
            from scripts.validate_data import validate_data_quality
            validate_data_quality()
            
            logger.info("✅ 数据处理完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据处理失败: {e}")
            return False
    
    def import_data(self):
        """导入数据"""
        logger.info("💾 开始数据导入...")
        
        try:
            from scripts.import_to_db import import_to_database
            result = import_to_database()
            return result
            
        except Exception as e:
            logger.error(f"❌ 数据导入失败: {e}")
            return False
    
    def run_full_pipeline(self, collect_method="all"):
        """运行完整数据管道"""
        logger.info("🚀 启动完整数据处理管道...")
        
        steps = [
            ("数据收集", lambda: self.collect_data(collect_method)),
            ("数据处理", self.process_data),
            ("数据导入", self.import_data)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 执行: {step_name}")
            success = step_func()
            
            if not success:
                logger.error(f"❌ {step_name}失败，停止管道执行")
                return False
            
            logger.info(f"✅ {step_name}完成")
        
        logger.info("\n🎉 完整数据处理管道执行完成！")
        return True
    
    def get_data_status(self):
        """获取数据状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "raw_data": {},
            "processed_data": {},
            "database_status": "unknown"
        }
        
        # 检查原始数据
        raw_dir = os.path.join(self.base_dir, "raw", "subjects")
        if os.path.exists(raw_dir):
            for subject in os.listdir(raw_dir):
                subject_dir = os.path.join(raw_dir, subject)
                if os.path.isdir(subject_dir):
                    file_count = sum([len(files) for r, d, files in os.walk(subject_dir)])
                    status["raw_data"][subject] = file_count
        
        # 检查处理后数据
        processed_dir = os.path.join(self.base_dir, "processed")
        kp_file = os.path.join(processed_dir, "knowledge_points_unified.csv")
        q_file = os.path.join(processed_dir, "questions_unified.csv")
        
        status["processed_data"]["knowledge_points_exists"] = os.path.exists(kp_file)
        status["processed_data"]["questions_exists"] = os.path.exists(q_file)
        
        if status["processed_data"]["knowledge_points_exists"]:
            import pandas as pd
            df = pd.read_csv(kp_file)
            status["processed_data"]["knowledge_points_count"] = len(df)
        
        if status["processed_data"]["questions_exists"]:
            import pandas as pd
            df = pd.read_csv(q_file)
            status["processed_data"]["questions_count"] = len(df)
        
        return status

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("📚 AI作业批改系统 - 数据管理工具")
    print("="*60)
    print("1. 🤖 收集数据 (AI生成)")
    print("2. 🌐 收集数据 (网站爬虫)")
    print("3. 📄 收集数据 (PDF处理)")
    print("4. 🔄 收集数据 (全部方式)")
    print("5. ⚙️  处理数据")
    print("6. 💾 导入数据库")
    print("7. 🚀 运行完整管道")
    print("8. 📊 查看数据状态")
    print("9. ❌ 退出")
    print("="*60)

def main():
    """主函数"""
    manager = DataManager()
    
    while True:
        show_menu()
        choice = input("请选择操作 (1-9): ").strip()
        
        if choice == "1":
            manager.collect_data("ai")
        elif choice == "2":
            manager.collect_data("crawl")
        elif choice == "3":
            manager.collect_data("pdf")
        elif choice == "4":
            manager.collect_data("all")
        elif choice == "5":
            manager.process_data()
        elif choice == "6":
            manager.import_data()
        elif choice == "7":
            collect_method = input("选择收集方式 (ai/crawl/pdf/all) [all]: ").strip() or "all"
            manager.run_full_pipeline(collect_method)
        elif choice == "8":
            status = manager.get_data_status()
            print("\n📊 数据状态:")
            print(f"📅 检查时间: {status['timestamp']}")
            print(f"📁 原始数据: {status['raw_data']}")
            print(f"⚙️  处理后数据: {status['processed_data']}")
        elif choice == "9":
            print("👋 退出数据管理工具")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
