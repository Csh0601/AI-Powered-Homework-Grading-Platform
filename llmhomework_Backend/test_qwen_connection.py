#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修复后的Qwen连接
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_qwen_connection():
    """测试Qwen连接"""
    print("🔍 测试修复后的Qwen连接...")
    
    try:
        from app.config import Config
        print(f"✅ 配置加载成功")
        print(f"   服务器: {Config.OLLAMA_BASE_URL}")
        print(f"   模型: {Config.QWEN_MODEL_NAME}")
        
        from app.services.qwen_service import QwenService
        
        print("\n🚀 创建QwenService实例...")
        qwen_service = QwenService(Config.QWEN_MODEL_NAME)
        print("✅ QwenService创建成功！")
        
        print("\n💬 测试简单对话...")
        test_prompt = "你好，请用一句话介绍自己"
        response = qwen_service.generate_response(test_prompt, max_tokens=50)
        
        print(f"问题: {test_prompt}")
        print(f"回答: {response}")
        
        if response and len(response.strip()) > 0:
            print("\n🎉 测试完全成功！Qwen服务正常工作！")
            return True
        else:
            print("\n❌ 模型没有返回有效响应")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qwen_connection()
    if success:
        print("\n✅ 可以启动应用了！")
    else:
        print("\n❌ 需要进一步排查问题")
