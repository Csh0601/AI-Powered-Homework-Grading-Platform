#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_backend_api():
    """测试后端API服务"""
    print("测试后端API服务...")
    
    # 测试服务状态
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False
    
    # 测试图片上传API
    try:
        # 模拟图片上传请求
        test_data = {
            'file': 'test_image.jpg'
        }
        response = requests.post('http://localhost:5000/upload_image', 
                               data=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 图片上传API测试成功")
            print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 图片上传API测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 图片上传API测试异常: {e}")
        return False

def test_llava_api():
    """测试LLaVA API服务"""
    print("\n测试LLaVA API服务...")
    
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("✅ LLaVA Web服务运行正常")
            return True
        else:
            print(f"❌ LLaVA Web服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到LLaVA Web服务: {e}")
        return False

def test_llava_controller():
    """测试LLaVA控制器"""
    print("\n测试LLaVA控制器...")
    
    try:
        response = requests.get('http://localhost:10000', timeout=5)
        if response.status_code == 200:
            print("✅ LLaVA控制器运行正常")
            return True
        else:
            print(f"❌ LLaVA控制器异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到LLaVA控制器: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("作业批改系统服务测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试各项服务
    backend_ok = test_backend_api()
    llava_web_ok = test_llava_api()
    llava_controller_ok = test_llava_controller()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    print(f"后端API服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"LLaVA Web服务: {'✅ 正常' if llava_web_ok else '❌ 异常'}")
    print(f"LLaVA控制器: {'✅ 正常' if llava_controller_ok else '❌ 异常'}")
    
    if all([backend_ok, llava_web_ok, llava_controller_ok]):
        print("\n🎉 所有服务运行正常！")
        print("\n访问地址:")
        print("- 后端API: http://localhost:5000")
        print("- LLaVA Web: http://localhost:8000")
        print("- LLaVA控制器: http://localhost:10000")
    else:
        print("\n⚠️ 部分服务异常，请检查启动状态")
    
    print("=" * 50)

if __name__ == '__main__':
    main() 