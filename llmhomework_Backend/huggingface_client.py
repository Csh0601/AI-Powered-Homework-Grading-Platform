# -*- coding: utf-8 -*-
"""
修复版HuggingFace客户端 - 已验证可用（已弃用）
连接服务器172.31.179.77:8007，使用正确的API格式
注意：此客户端已被qwen_vl_direct_service替代，现在直接调用LoRA训练模型
推荐使用：app/services/qwen_vl_direct_service.py
"""
import requests
import json
import sys
import os

# 修复Windows编码问题
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class HuggingFaceClient:
    def __init__(self):
        self.hf_url = "http://172.31.179.77:8007"
        self.ollama_url = "http://172.31.179.77:11434" 
        self.timeout = 300  # 5分钟超时
        
        print("[INFO] HuggingFace客户端已就绪（已弃用，推荐使用qwen_vl_direct_service）")
        print(f"[INFO] 当前服务: {self.hf_url} (现为Qwen2.5-VL-LoRA)")
        print(f"[INFO] 备用服务: {self.ollama_url} (Ollama)")
        print("[WARN] 此客户端已弃用，请使用app/services/qwen_vl_direct_service.py")
    
    def chat_completion(self, prompt: str, max_tokens: int = 200000):
        """智能聊天完成 - 优先HuggingFace，备用Ollama"""
        
        # 🥇 优先HuggingFace (已验证工作!)
        try:
            print("[INFO] 连接HuggingFace Qwen3-30B...")
            response = self._call_huggingface(prompt, max_tokens)
            if response.get("success"):
                print("[OK] HuggingFace调用成功!")
                return response
            else:
                print(f"[WARNING] HuggingFace错误: {response.get('error')}")
        except Exception as e:
            print(f"[ERROR] HuggingFace异常: {e}")
        
        # 🥈 备用Ollama
        try:
            print("[INFO] 切换到Ollama备用服务...")
            response = self._call_ollama(prompt, max_tokens)
            if response.get("success"):
                print("[OK] Ollama调用成功!")
                return response
        except Exception as e:
            print(f"[ERROR] Ollama失败: {e}")
        
        return {
            "success": False,
            "error": "所有服务均不可用",
            "response": "服务暂时不可用，请稍后重试"
        }
    
    def _call_huggingface(self, prompt: str, max_tokens: int):
        """调用HuggingFace服务 - 已验证的API格式"""
        url = f"{self.hf_url}/api/v1/chat"
        
        # ✅ 正确的请求格式 (已验证)
        payload = {
            "query": prompt,  # 服务器期望的字段名
            "max_new_tokens": max_tokens,
            "temperature": 0.7
        }
        
        print(f"[DEBUG] POST {url}")
        print(f"[DEBUG] Data: {json.dumps(payload, ensure_ascii=False)[:100]}...")
        
        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查服务器错误
            if "error" in data:
                return {"success": False, "error": data["error"]}
            
            # ✅ 成功响应格式
            return {
                "success": True,
                "response": data.get("response", ""),
                "model_used": f"HuggingFace-{data.get('model', 'Qwen3-30B')}",
                "tokens_used": data.get("max_tokens_used", 0)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    def _call_ollama(self, prompt: str, max_tokens: int):
        """调用Ollama备用服务"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": "qwen3:30B",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        return {
            "success": True,
            "response": data.get("response", ""),
            "model_used": "Ollama-Qwen3-30B",
            "tokens_used": len(data.get("response", "").split())
        }

# 🧪 完整测试
def comprehensive_test():
    """完整测试HuggingFace连接"""
    print("🚀 HuggingFace服务完整测试")
    print("=" * 60)
    
    client = HuggingFaceClient()
    
    # 测试多个场景
    test_cases = [
        "你好，请简单介绍你自己",
        "请帮我写一首关于春天的诗", 
        "Python中如何读取文件？",
        "解释一下机器学习的基本概念"
    ]
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {prompt}")
        print("-" * 40)
        
        result = client.chat_completion(prompt, max_tokens=200)
        
        print(f"成功: {result['success']}")
        print(f"模型: {result.get('model_used', 'unknown')}")
        if result['success']:
            response = result.get('response', '')
            print(f"回复: {response[:100]}{'...' if len(response) > 100 else ''}")
        else:
            print(f"错误: {result.get('error', 'unknown')}")
        
        print()
    
    print("🎯 测试完成!")

if __name__ == "__main__":
    comprehensive_test()
