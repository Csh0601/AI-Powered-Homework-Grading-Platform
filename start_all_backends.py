#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全后端启动脚本
同时启动AI后端和OCR后端，并检测启动状态
"""
import subprocess
import sys
import os

# 修复Windows编码问题
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
import time
import requests
import os
import sys
import threading
import signal
from pathlib import Path

class BackendManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ai_backend_path = self.project_root / "llmhomework_Backend"
        self.ocr_backend_path = self.project_root / "My Part" / "backend"
        
        # 进程管理
        self.ai_process = None
        self.ocr_process = None
        self.running = True
        
        # 启动配置
        self.ai_port = 5000
        self.ocr_port = 8002
        
        print("[INIT] 后端管理器初始化完成")
        print(f"   AI后端路径: {self.ai_backend_path}")
        print(f"   OCR后端路径: {self.ocr_backend_path}")
    
    def check_port_available(self, port):
        """检查端口是否可用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def kill_process_on_port(self, port):
        """终止占用指定端口的进程"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                print(f"   终止进程 PID {pid} (端口 {port})")
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
        except Exception as e:
            print(f"   终止端口 {port} 进程失败: {e}")
    
    def start_ai_backend(self):
        """启动AI后端"""
        print("\n[AI] 启动AI后端...")
        
        if not self.check_port_available(self.ai_port):
            print(f"   端口 {self.ai_port} 被占用，尝试释放...")
            self.kill_process_on_port(self.ai_port)
            time.sleep(2)
        
        try:
            # 切换到AI后端目录并启动
            python_exe = "python"
            
            self.ai_process = subprocess.Popen(
                [python_exe, "run.py"],
                cwd=self.ai_backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"   AI后端进程已启动 (PID: {self.ai_process.pid})")
            return True
            
        except Exception as e:
            print(f"   ❌ AI后端启动失败: {e}")
            return False
    
    def start_ocr_backend(self):
        """启动OCR后端"""
        print("\n[OCR] 启动OCR后端...")
        
        if not self.check_port_available(self.ocr_port):
            print(f"   端口 {self.ocr_port} 被占用，尝试释放...")
            self.kill_process_on_port(self.ocr_port)
            time.sleep(2)
        
        try:
            # 激活虚拟环境并启动OCR服务
            venv_python = self.ocr_backend_path / ".venv" / "Scripts" / "python.exe"
            
            if not venv_python.exists():
                print(f"   ❌ 虚拟环境不存在: {venv_python}")
                return False
            
            self.ocr_process = subprocess.Popen(
                [str(venv_python), "-m", "uvicorn", "main:app", 
                 "--host", "127.0.0.1", "--port", str(self.ocr_port), "--reload"],
                cwd=self.ocr_backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"   OCR后端进程已启动 (PID: {self.ocr_process.pid})")
            return True
            
        except Exception as e:
            print(f"   ❌ OCR后端启动失败: {e}")
            return False
    
    def check_ai_backend_health(self):
        """检查AI后端健康状态"""
        try:
            response = requests.get(f"http://127.0.0.1:{self.ai_port}/status", timeout=5)
            if response.status_code == 200:
                return True, "正常运行"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "连接失败"
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except Exception as e:
            return False, str(e)
    
    def check_ocr_backend_health(self):
        """检查OCR后端健康状态"""
        try:
            response = requests.get(f"http://127.0.0.1:{self.ocr_port}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                engine = data.get('engine', 'unknown')
                return True, f"正常运行 (引擎: {engine})"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "连接失败"
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except Exception as e:
            return False, str(e)
    
    def monitor_processes(self):
        """监控进程输出"""
        def monitor_ai():
            if self.ai_process:
                for line in iter(self.ai_process.stdout.readline, ''):
                    if not self.running:
                        break
                    print(f"[AI] {line.strip()}")
        
        def monitor_ocr():
            if self.ocr_process:
                for line in iter(self.ocr_process.stdout.readline, ''):
                    if not self.running:
                        break
                    print(f"[OCR] {line.strip()}")
        
        # 启动监控线程
        if self.ai_process:
            threading.Thread(target=monitor_ai, daemon=True).start()
        if self.ocr_process:
            threading.Thread(target=monitor_ocr, daemon=True).start()
    
    def wait_for_startup(self, max_wait=60):
        """等待服务启动完成"""
        print("\n[WAIT] 等待服务启动...")
        
        ai_ready = False
        ocr_ready = False
        
        for i in range(max_wait):
            if not ai_ready:
                ai_status, ai_msg = self.check_ai_backend_health()
                if ai_status:
                    print(f"[OK] AI后端就绪: {ai_msg}")
                    ai_ready = True
            
            if not ocr_ready:
                ocr_status, ocr_msg = self.check_ocr_backend_health()
                if ocr_status:
                    print(f"[OK] OCR后端就绪: {ocr_msg}")
                    ocr_ready = True
            
            if ai_ready and ocr_ready:
                return True
            
            if i % 5 == 0 and i > 0:
                print(f"   等待中... ({i}/{max_wait}秒)")
            
            time.sleep(1)
        
        print(f"[WARNING] 启动超时 ({max_wait}秒)")
        return False
    
    def show_status(self):
        """显示当前状态"""
        print("\n" + "="*60)
        print("[STATUS] 后端服务状态")
        print("="*60)
        
        # AI后端状态
        ai_status, ai_msg = self.check_ai_backend_health()
        ai_icon = "[OK]" if ai_status else "[ERROR]"
        print(f"{ai_icon} AI后端 (端口 {self.ai_port}): {ai_msg}")
        
        # OCR后端状态
        ocr_status, ocr_msg = self.check_ocr_backend_health()
        ocr_icon = "[OK]" if ocr_status else "[ERROR]"
        print(f"{ocr_icon} OCR后端 (端口 {self.ocr_port}): {ocr_msg}")
        
        print("="*60)
        
        if ai_status and ocr_status:
            print("[SUCCESS] 所有服务已就绪！")
            print(f"[INFO] AI后端访问地址: http://127.0.0.1:{self.ai_port}")
            print(f"[INFO] OCR后端访问地址: http://127.0.0.1:{self.ocr_port}")
            print("\n[TIP] 现在可以启动Flutter前端了!")
        else:
            print("[WARNING] 部分服务未就绪，请检查错误信息")
    
    def shutdown(self):
        """关闭所有服务"""
        print("\n[SHUTDOWN] 正在关闭所有服务...")
        self.running = False
        
        if self.ai_process:
            try:
                self.ai_process.terminate()
                self.ai_process.wait(timeout=5)
                print("   [OK] AI后端已关闭")
            except:
                self.ai_process.kill()
                print("   [FORCE] AI后端已强制关闭")
        
        if self.ocr_process:
            try:
                self.ocr_process.terminate()
                self.ocr_process.wait(timeout=5)
                print("   [OK] OCR后端已关闭")
            except:
                self.ocr_process.kill()
                print("   [FORCE] OCR后端已强制关闭")
    
    def run(self):
        """主运行流程"""
        print("[START] 开始启动所有后端服务...")
        print("="*60)
        
        try:
            # 启动服务
            ai_started = self.start_ai_backend()
            ocr_started = self.start_ocr_backend()
            
            if not (ai_started and ocr_started):
                print("[ERROR] 部分服务启动失败")
                self.shutdown()
                return False
            
            # 开始监控输出
            self.monitor_processes()
            
            # 等待启动完成
            if self.wait_for_startup():
                self.show_status()
                
                # 保持运行状态
                print("\n[CONTROL] 按 Ctrl+C 停止所有服务")
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n[SIGNAL] 收到停止信号...")
            else:
                print("[ERROR] 服务启动超时")
                
        except Exception as e:
            print(f"[ERROR] 启动过程出错: {e}")
        finally:
            self.shutdown()
            print("[DONE] 所有服务已关闭")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n[SIGNAL] 收到终止信号，正在关闭...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("[MANAGER] 全后端启动管理器")
    print("[INFO] 将同时启动AI后端和OCR后端服务")
    print()
    
    manager = BackendManager()
    success = manager.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
