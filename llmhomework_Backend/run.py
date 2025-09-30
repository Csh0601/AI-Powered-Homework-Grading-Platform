import logging
import os
import sys
import time
import warnings
import subprocess
import requests

# 在导入任何依赖之前显式禁用 Flash Attention/Triton
os.environ.setdefault("PYTORCH_ENABLE_TRITON", "0")
os.environ.setdefault("TORCHINDUCTOR_DISABLE_TRITON", "1")
os.environ.setdefault("FLASH_ATTENTION_FORCE_DISABLED", "1")
os.environ.setdefault("ATTN_IMPLEMENTATION", "eager")
os.environ.setdefault("PYTORCH_NO_FAST_ATTENTION", "1")

print("⚙️ Flash Attention/Triton 已禁用 -> PYTORCH_ENABLE_TRITON=0, TORCHINDUCTOR_DISABLE_TRITON=1, FLASH_ATTENTION_FORCE_DISABLED=1, PYTORCH_NO_FAST_ATTENTION=1")

# 在导入应用之前设置日志级别和警告过滤
logging.basicConfig(level=logging.INFO)

# 完全禁用不需要的服务日志
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ollama").setLevel(logging.ERROR)
logging.getLogger("app.services.qwen_service").setLevel(logging.ERROR)
logging.getLogger("app.services.grading_qwen").setLevel(logging.ERROR)
logging.getLogger("app.services.huggingface_service").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)

# 禁用所有第三方库的警告
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="jieba")
warnings.filterwarnings("ignore", module="pkg_resources")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 现在安全导入应用
from app import create_app
from flask_cors import CORS

def ensure_lora_service_running():
    """确保LoRA服务正在运行"""
    print("🔍 检查LoRA服务状态...")
    
    # 首先检查服务是否已经运行
    try:
        response = requests.get("http://172.31.179.77:8007/health", timeout=5)
        if response.status_code == 200:
            print("✅ LoRA服务已运行")
            return True
    except:
        pass  # 服务未运行，继续启动流程
    
    print("🚀 启动LoRA服务...")
    try:
        # 使用服务器上的自动启动脚本
        result = subprocess.run([
            "ssh", "cshcsh@172.31.179.77", 
            "python3 /home/cshcsh/rag知识系统/auto_start_lora.py"
        ], capture_output=True, text=True, timeout=60, check=True)
        
        print("⏳ 等待LoRA服务启动...")
        time.sleep(30)  # 等待服务启动
        
        # 再次检查服务状态
        try:
            response = requests.get("http://172.31.179.77:8007/health", timeout=30)
            if response.status_code == 200:
                print("✅ LoRA服务启动成功")
                return True
            else:
                print(f"⚠️ LoRA服务启动中，状态码: {response.status_code}")
                return True  # 服务可能还在启动中
        except:
            print("⚠️ LoRA服务可能还在启动中，请稍等...")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ SSH启动失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        print("💡 请手动启动服务器上的LoRA服务:")
        print("   ssh cshcsh@172.31.179.77")
        print("   cd /home/cshcsh/rag知识系统 && python3 auto_start_lora.py")
        return False
    except subprocess.TimeoutExpired:
        print("⏰ SSH连接超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 启动异常: {e}")
        return False

def test_qwen_vl_connection():
    """测试Qwen2.5-VL多模态连接"""
    print("🎯 测试Qwen2.5-VL多模态连接...")
    
    try:
        from app.services.multimodal_client import get_qwen_vl_client
        from app.config import Config
        
        # 获取客户端
        client = get_qwen_vl_client()
        
        # 健康检查
        print("   📡 正在连接服务器...")
        health_status = client.health_check()
        
        if health_status.get('status') == 'healthy':
            server_info = health_status.get('server_info', {})
            model_name = server_info.get('model_name', 'Unknown')
            optimizations = server_info.get('optimizations', [])
            
            print("   ✅ Qwen2.5-VL连接成功！")
            print(f"   🤖 模型: {model_name}")
            print(f"   🌐 服务器: {Config.QWEN_VL_API_URL}")
            print(f"   ⚡ 优化特性: {len(optimizations)} 项")
            for i, opt in enumerate(optimizations[:3], 1):  # 只显示前3个
                print(f"      {i}. {opt}")
            if len(optimizations) > 3:
                print(f"      ... 等{len(optimizations)}项优化")
            print("   🎯 功能: 真正的多模态图像理解，无OCR依赖")
            return True
        else:
            print("   ❌ Qwen2.5-VL连接失败")
            print(f"   💬 错误: {health_status.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"   ❌ 连接测试异常: {e}")
        return False

def print_startup_banner():
    """打印启动横幅"""
    print("\n" + "="*70)
    print("🚀 LLM作业批改系统 - Qwen2.5-VL多模态版本")
    print("="*70)
    
    # 配置信息
    from app.config import Config
    print("📋 系统配置:")
    print(f"   🎯 AI提供商: {Config.LLM_PROVIDER}")
    print(f"   🔄 多模态模式: {'启用' if Config.MULTIMODAL_ENABLED else '禁用'}")
    print(f"   🔄 OCR回退: {'启用' if Config.OCR_FALLBACK_ENABLED else '禁用'}")
    print(f"   ⏱️ 超时时间: {Config.TIMEOUT_SECONDS}秒")
    print(f"   🎫 最大Token: {Config.MAX_TOKENS}")
    print("")
    
    # 测试连接
    qwen_vl_ok = test_qwen_vl_connection()
    
    print("")
    print("🎊 系统状态总结:")
    if qwen_vl_ok:
        print("   ✅ Qwen2.5-VL多模态服务: 连接正常")
        print("   🎯 系统状态: 准备就绪！")
        print("   📱 现在可以启动前端进行测试")
    else:
        print("   ❌ Qwen2.5-VL多模态服务: 连接失败")
        print("   ⚠️ 系统状态: 将使用OCR回退模式")
    
    print("\n" + "="*70)
    print("🌐 Flask服务器启动中...")
    print("   📍 本地地址: http://127.0.0.1:5000")
    print("   📍 网络地址: http://172.29.15.12:5000")
    print("   🔍 多模态健康检查: /health/multimodal")
    print("="*70 + "\n")

app = create_app()
CORS(app)

if __name__ == '__main__':
    # 确保LoRA服务正在运行
    print("🔧 检查LoRA服务状态...")
    ensure_lora_service_running()
    
    # 显示启动信息
    print_startup_banner()
    
    # 配置Flask应用以支持长时间请求（AI批改）
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # 5分钟缓存
    
    # 启动服务器
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
