#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoRA服务启动脚本
用于手动启动服务器上的LoRA服务
"""

import subprocess
import sys
import time
import os

# 修复Windows编码问题
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def start_lora_service():
    """启动LoRA服务"""
    print("启动LoRA服务...")
    print("="*50)
    
    try:
        # 使用SSH连接服务器并启动LoRA服务
        result = subprocess.run([
            "ssh", "cshcsh@172.31.179.77", 
            "python3 /home/cshcsh/rag知识系统/auto_start_lora.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[OK] LoRA服务启动命令执行成功")
            print("输出信息:")
            print(result.stdout)
            
            if result.stderr:
                print("警告信息:")
                print(result.stderr)
                
            print("\n等待服务启动...")
            time.sleep(30)
            
            # 检查服务状态
            print("检查服务状态...")
            try:
                import requests
                response = requests.get("http://172.31.179.77:8007/health", timeout=30)
                if response.status_code == 200:
                    print("[OK] LoRA服务启动成功！")
                    print("现在可以启动本地后端服务")
                else:
                    print(f"服务响应异常，状态码: {response.status_code}")
                    print("服务可能还在启动中，请稍等...")
            except ImportError:
                print("无法检查服务状态（缺少requests库）")
                print("请手动检查服务是否启动成功")
            except Exception as e:
                print(f"服务状态检查失败: {e}")
                print("服务可能还在启动中")
                
        else:
            print("[ERROR] LoRA服务启动失败")
            print("错误信息:")
            print(result.stderr)
            print("\n请检查:")
            print("1. SSH连接是否正常")
            print("2. 服务器上的auto_start_lora.py脚本是否存在")
            print("3. 服务器上的Python环境是否正常")
            
    except subprocess.TimeoutExpired:
        print("SSH连接超时")
        print("请检查网络连接和SSH配置")
    except FileNotFoundError:
        print("[ERROR] 找不到SSH命令")
        print("请确保已安装SSH客户端")
    except Exception as e:
        print(f"[ERROR] 启动异常: {e}")
    
    print("="*50)

def main():
    """主函数"""
    print("LoRA服务启动工具")
    print("用于启动服务器上的LoRA多模态服务")
    print()
    
    # 检查SSH连接
    print("检查SSH连接...")
    try:
        result = subprocess.run([
            "ssh", "-o", "ConnectTimeout=5", "cshcsh@172.31.179.77", "echo 'SSH连接正常'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] SSH连接正常")
        else:
            print("[ERROR] SSH连接失败")
            print("请检查SSH配置和网络连接")
            return
            
    except Exception as e:
        print(f"[ERROR] SSH连接测试失败: {e}")
        print("请检查SSH配置")
        return
    
    # 启动LoRA服务
    start_lora_service()

if __name__ == "__main__":
    main()
