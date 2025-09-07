#!/usr/bin/env python3
"""
数据统一处理脚本
将不同来源的原始数据统一为标准格式
"""

import os
import sys
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path

# 设置路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def unify_all_data():
    """统一处理所有数据"""
    logger.info("🔄 开始统一处理数据...")
    
    # 调用原有的统一处理脚本
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from unify_generated_data import main as unify_main
    
    try:
        result = unify_main()
        logger.info("✅ 数据统一处理完成")
        return result
    except Exception as e:
        logger.error(f"❌ 数据统一处理失败: {e}")
        return False

if __name__ == "__main__":
    unify_all_data()
