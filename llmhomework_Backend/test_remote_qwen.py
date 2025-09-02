#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试远程服务器qwen3:30B模型连接
"""

import sys
import os
import requests
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.config import Config

def test_server_connectivity():
    """测试服务器连通性"""
    print("=" * 60)
    print("测试服务器连通性")
    print("=" * 60)
    
    server_url = f"http://{Config.SERVER_HOST}:{Config.OLLAMA_PORT}"
    
    try:
        # 测试基本连接
        print(f"测试服务器地址: {server_url}")
        response = requests.get(f"{server_url}/api/version", timeout=10)
        
        if response.status_code == 200:
            print("✅ 服务器连接成功！")
            version_info = response.json()
            print(f"Ollama版本: {version_info.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请检查：")
        print("1. 服务器IP地址是否正确")
        print("2. 服务器防火墙是否开放11434端口")
        print("3. Ollama服务是否在服务器上运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def test_model_availability():
    """测试模型可用性"""
    print("\n" + "=" * 60)
    print("测试qwen3:30B模型可用性")
    print("=" * 60)
    
    server_url = Config.OLLAMA_BASE_URL
    
    try:
        # 获取模型列表
        print("获取服务器上的模型列表...")
        response = requests.get(f"{server_url}/api/tags", timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model['name'] for model in models_data.get('models', [])]
            
            print(f"服务器上可用的模型: {models}")
            
            # 检查qwen3:30B是否存在
            target_models = ['qwen3:30B', 'qwen3:30b', 'qwen3:30B']
            available_model = None
            
            for model in target_models:
                if model in models:
                    available_model = model
                    break
            
            if available_model:
                print(f"✅ 找到目标模型: {available_model}")
                return available_model
            else:
                print("❌ 未找到qwen3:30B模型")
                print("请在服务器上运行: ollama pull qwen3:30B")
                return None
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 模型检查失败: {e}")
        return None

def test_model_generation():
    """测试模型生成功能"""
    print("\n" + "=" * 60)
    print("测试模型生成功能")
    print("=" * 60)
    
    server_url = Config.OLLAMA_BASE_URL
    model_name = Config.QWEN_MODEL_NAME
    
    try:
        print(f"使用模型: {model_name}")
        print("发送测试请求...")
        
        # 准备请求数据
        data = {
            "model": model_name,
            "prompt": "你好，请简单介绍一下你自己。",
            "stream": False,
            "options": {
                "num_predict": 100,
                "temperature": 0.1
            }
        }
        
        # 发送生成请求
        response = requests.post(
            f"{server_url}/api/generate",
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            print("✅ 模型生成成功！")
            print(f"生成内容: {generated_text}")
            print(f"生成时间: {result.get('total_duration', 0) / 1000000:.2f}ms")
            return True
        else:
            print(f"❌ 生成请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 模型生成测试失败: {e}")
        return False

def test_ollama_client():
    """使用ollama客户端测试连接"""
    print("\n" + "=" * 60)
    print("测试ollama客户端连接")
    print("=" * 60)
    
    try:
        from app.services.qwen_service import QwenService
        
        print(f"正在创建QwenService实例...")
        print(f"目标服务器: {Config.OLLAMA_BASE_URL}")
        print(f"目标模型: {Config.QWEN_MODEL_NAME}")
        
        # 创建服务实例
        qwen_service = QwenService(Config.QWEN_MODEL_NAME)
        print("✅ QwenService创建成功！")
        
        # 测试简单对话
        print("\n测试简单对话...")
        test_prompt = "请用中文回答：1+1等于多少？"
        response = qwen_service.generate_response(test_prompt, max_tokens=50)
        
        print(f"测试问题: {test_prompt}")
        print(f"模型回答: {response}")
        
        if response and len(response.strip()) > 0:
            print("✅ 对话测试成功！")
            return True
        else:
            print("❌ 模型没有返回有效响应")
            return False
            
    except Exception as e:
        print(f"❌ ollama客户端测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试远程qwen3:30B模型连接...")
    print(f"服务器信息:")
    print(f"  IP地址: {Config.SERVER_HOST}")
    print(f"  端口: {Config.OLLAMA_PORT}")
    print(f"  完整URL: {Config.OLLAMA_BASE_URL}")
    print(f"  目标模型: {Config.LLAMA_MODEL_NAME}")
    
    # 步骤1: 测试服务器连通性
    if not test_server_connectivity():
        print("\n❌ 服务器连接失败，请先解决连接问题")
        return
    
    # 步骤2: 测试模型可用性
    available_model = test_model_availability()
    if not available_model:
        print("\n❌ 模型不可用，请先在服务器上安装qwen3:30B")
        return
    
    # 步骤3: 测试模型生成
    if not test_model_generation():
        print("\n❌ 模型生成失败")
        return
    
    # 步骤4: 测试ollama客户端
    if not test_ollama_client():
        print("\n❌ ollama客户端测试失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！远程qwen3:30B模型配置成功！")
    print("=" * 60)
    print("现在可以启动项目使用远程大模型进行作业批改了。")

if __name__ == "__main__":
    main()
