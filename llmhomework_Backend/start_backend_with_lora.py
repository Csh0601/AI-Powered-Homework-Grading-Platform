#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键启动后端服务（包含LoRA服务启动）
"""

import subprocess
import sys
import time
import os

def start_lora_service():
    """启动LoRA服务"""
    print("🔧 启动LoRA服务...")
    
    try:
        result = subprocess.run([
            "ssh", "cshcsh@172.31.179.77", 
            "python3 /home/cshcsh/rag知识系统/auto_start_lora.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ LoRA服务启动成功")
            return True
        else:
            print("⚠️ LoRA服务启动可能有问题")
            print("错误信息:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ LoRA服务启动失败: {e}")
        return False

def start_backend_service():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    try:
        # 启动后端服务
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 后端服务已停止")
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")

def main():
    """主函数"""
    print("="*60)
    print("🚀 一键启动后端服务（包含LoRA服务）")
    print("="*60)
    
    # 检查当前目录
    if not os.path.exists("run.py"):
        print("❌ 错误: 找不到run.py文件")
        print("💡 请确保在正确的目录中运行此脚本")
        return
    
    # 启动LoRA服务
    print("步骤 1: 启动LoRA服务")
    lora_success = start_lora_service()
    
    if lora_success:
        print("⏳ 等待LoRA服务完全启动...")
        time.sleep(30)
    
    print("\n步骤 2: 启动后端服务")
    print("="*60)
    
    # 启动后端服务
    start_backend_service()

if __name__ == "__main__":
    main()
