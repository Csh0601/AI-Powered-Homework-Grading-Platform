#!/usr/bin/env python3
"""
数据库导入脚本
将处理后的数据导入系统数据库
"""

import os
import sys
import logging

# 设置路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_to_database():
    """导入数据到数据库"""
    logger.info("💾 开始导入数据到数据库...")
    
    try:
        # 调用导入脚本
        from import_crawled_data import import_crawled_data
        result = import_crawled_data()
        
        if result:
            logger.info("✅ 数据库导入完成")
        else:
            logger.error("❌ 数据库导入失败")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 导入过程出错: {e}")
        return False

if __name__ == "__main__":
    import_to_database()
