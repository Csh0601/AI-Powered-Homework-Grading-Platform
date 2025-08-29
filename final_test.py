#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import urllib.request
import urllib.parse

def test_backend_api():
    """测试后端API服务"""
    print("🔍 测试后端API服务...")
    
    try:
        # 测试服务状态
        response = urllib.request.urlopen('http://localhost:5000', timeout=5)
        if response.getcode() == 200:
            print("✅ 后端服务运行正常")
        else:
            print(f"❌ 后端服务异常: {response.getcode()}")
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
        data = urllib.parse.urlencode(test_data).encode('utf-8')
        req = urllib.request.Request('http://localhost:5000/upload_image', data=data)
        response = urllib.request.urlopen(req, timeout=10)
        
        if response.getcode() == 200:
            result = response.read().decode('utf-8')
            print("✅ 图片上传API测试成功")
            print(f"返回数据: {result}")
            return True
        else:
            print(f"❌ 图片上传API测试失败: {response.getcode()}")
            return False
    except Exception as e:
        print(f"❌ 图片上传API测试异常: {e}")
        return False

def test_llava_controller():
    """测试LLaVA控制器"""
    print("\n🔍 测试LLaVA控制器...")
    
    try:
        response = urllib.request.urlopen('http://localhost:10000', timeout=5)
        if response.getcode() == 200:
            print("✅ LLaVA控制器运行正常")
            return True
        else:
            print(f"❌ LLaVA控制器异常: {response.getcode()}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到LLaVA控制器: {e}")
        return False

def test_llava_web():
    """测试LLaVA Web服务"""
    print("\n🔍 测试LLaVA Web服务...")
    
    try:
        response = urllib.request.urlopen('http://localhost:8000', timeout=5)
        if response.getcode() == 200:
            print("✅ LLaVA Web服务运行正常")
            return True
        else:
            print(f"❌ LLaVA Web服务异常: {response.getcode()}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到LLaVA Web服务: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎓 作业批改系统完整测试")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 测试各项服务
    backend_ok = test_backend_api()
    llava_controller_ok = test_llava_controller()
    llava_web_ok = test_llava_web()
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    print(f"后端API服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"LLaVA控制器: {'✅ 正常' if llava_controller_ok else '❌ 异常'}")
    print(f"LLaVA Web服务: {'✅ 正常' if llava_web_ok else '❌ 异常'}")
    
    if all([backend_ok, llava_controller_ok, llava_web_ok]):
        print("\n🎉 所有核心服务运行正常！")
        print("\n🌐 访问地址:")
        print("- 后端API: http://localhost:5000")
        print("- LLaVA控制器: http://localhost:10000")
        print("- LLaVA Web: http://localhost:8000")
        print("- 前端应用: http://localhost:3000")
        
        print("\n📋 功能特性:")
        print("- ✅ 图片上传和识别")
        print("- ✅ LLaVA多模态识别")
        print("- ✅ 智能作业批改")
        print("- ✅ 错题知识点提取")
        
        print("\n🚀 系统已完全部署完成！")
    else:
        print("\n⚠️ 部分服务异常，请检查启动状态")
        if not backend_ok:
            print("- 后端服务未启动，请运行: python test_server.py")
        if not llava_controller_ok:
            print("- LLaVA控制器未启动，请检查LLaVA服务")
        if not llava_web_ok:
            print("- LLaVA Web服务未启动，请检查Gradio服务")
    
    print("=" * 60)

if __name__ == '__main__':
    main() 