#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接调试Ollama API响应
"""

import requests
import json

def debug_ollama_api():
    """调试Ollama API"""
    base_url = "http://172.31.179.77:11434"
    
    print("🔍 调试Ollama API响应...")
    
    try:
        # 1. 测试基本连接
        print(f"\n1. 测试版本API...")
        response = requests.get(f"{base_url}/api/version", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        # 2. 测试模型列表API
        print(f"\n2. 测试模型列表API...")
        response = requests.get(f"{base_url}/api/tags", timeout=30)
        print(f"   状态码: {response.status_code}")
        print(f"   原始响应: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   JSON解析结果: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if 'models' in data:
                    models = data['models']
                    print(f"   模型数量: {len(models)}")
                    for i, model in enumerate(models):
                        print(f"   模型{i+1}: {model}")
                        if 'name' in model:
                            print(f"     名称: {model['name']}")
                else:
                    print("   ❌ 响应中没有'models'字段")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON解析失败: {e}")
        
        # 3. 测试生成API
        print(f"\n3. 测试生成API...")
        payload = {
            "model": "qwen3:30B",
            "prompt": "Hi",
            "stream": False,
            "options": {
                "num_predict": 5
            }
        }
        
        response = requests.post(
            f"{base_url}/api/generate", 
            json=payload, 
            timeout=60
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应前100字符: {response.text[:100]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'response' in data:
                    print(f"   ✅ 生成成功: {data['response']}")
                else:
                    print(f"   响应结构: {list(data.keys())}")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON解析失败: {e}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    debug_ollama_api()
