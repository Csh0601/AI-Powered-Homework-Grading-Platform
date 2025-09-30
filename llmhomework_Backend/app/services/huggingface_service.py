"""
HuggingFace服务客户端 - 优先连接服务器HuggingFace模型
智能切换：HuggingFace (主要) → Ollama (备用)
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from app.config import Config

logger = logging.getLogger(__name__)

class HuggingFaceService:
    """智能HuggingFace客户端 - 优先HuggingFace，备用Ollama"""
    
    def __init__(self):
        # 直接调用LoRA服务配置
        self.qwen_vl_url = getattr(Config, 'QWEN_VL_API_URL', 'http://172.31.179.77:8007')
        self.llm_provider = getattr(Config, 'LLM_PROVIDER', 'qwen_vl_lora_direct')
        self.multimodal_enabled = getattr(Config, 'MULTIMODAL_ENABLED', True)
        self.use_direct_service = getattr(Config, 'USE_DIRECT_LORA_SERVICE', True)
        self.bypass_rag = getattr(Config, 'BYPASS_RAG_SERVICE', True)
        
        # 兼容旧配置（如果存在）
        self.huggingface_url = getattr(Config, 'HUGGINGFACE_BASE_URL', self.qwen_vl_url)
        self.huggingface_model = getattr(Config, 'HUGGINGFACE_MODEL', 'Qwen2.5-VL-LoRA')
        self.use_huggingface = getattr(Config, 'USE_HUGGINGFACE', False)
        
        # Ollama配置 (已弃用，保留兼容性)
        self.ollama_url = getattr(Config, 'OLLAMA_BASE_URL', None)
        self.ollama_model = getattr(Config, 'QWEN_MODEL_NAME', None)
        
        # 通用配置
        self.max_tokens = Config.MAX_TOKENS
        self.timeout = Config.TIMEOUT_SECONDS
        self.retry_attempts = Config.RETRY_ATTEMPTS
        
        logger.info(f"AI服务初始化 (直接调用LoRA配置):")
        logger.info(f"  LoRA服务: {self.qwen_vl_url}")
        logger.info(f"  LLM提供商: {self.llm_provider}")
        logger.info(f"  多模态启用: {self.multimodal_enabled}")
        logger.info(f"  直接调用: {self.use_direct_service}")
        logger.info(f"  绕过RAG: {self.bypass_rag}")
        if self.ollama_url:
            logger.info(f"  备用服务: {self.ollama_url} (模型: {self.ollama_model})")
        
    def chat_completion(self, prompt: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """智能聊天完成 - 自动切换服务"""
        if max_tokens is None:
            max_tokens = self.max_tokens
            
        logger.info(f"开始AI对话，Prompt长度: {len(prompt)} 字符")
        
        # 🥇 优先尝试HuggingFace
        if self.use_huggingface:
            try:
                logger.info("🤖 尝试连接HuggingFace Qwen3-30B...")
                response = self._call_huggingface(prompt, max_tokens)
                if response and response.get("success"):
                    logger.info("✅ HuggingFace调用成功")
                    return response
            except Exception as e:
                logger.warning(f"⚠️ HuggingFace调用失败: {e}")
        
        # 🥈 备用Ollama服务 
        try:
            logger.info("🔄 切换到Ollama备用服务...")
            response = self._call_ollama(prompt, max_tokens)
            if response and response.get("success"):
                logger.info("✅ Ollama调用成功")
                return response
        except Exception as e:
            logger.error(f"❌ Ollama调用失败: {e}")
            
        # 🚨 所有服务都失败
        logger.error("❌ 所有LLM服务均不可用")
        return {
            "success": False,
            "error": "所有LLM服务均不可用",
            "response": "抱歉，AI服务暂时不可用，请稍后重试。",
            "model_used": "none"
        }
    
    def _call_huggingface(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """调用HuggingFace服务 - 使用已验证的API格式"""
        # ✅ 使用已验证工作的端点
        url = f"{self.huggingface_url}/api/v1/chat"
        
        # ✅ 使用已验证的请求格式
        payload = {
            "query": prompt,  # 服务器期望的字段名
            "max_new_tokens": max_tokens,
            "temperature": 0.7
        }
        
        logger.debug(f"调用HuggingFace API: {url}")
        logger.debug(f"请求数据: {json.dumps(payload, ensure_ascii=False)[:100]}...")
        
        try:
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
                
                # ✅ 使用已验证的响应格式
                response_text = data.get("response", "")
                
                if response_text and response_text.strip():
                    return {
                        "success": True,
                        "response": response_text,
                        "model_used": f"HuggingFace-{data.get('model', self.huggingface_model)}",
                        "tokens_used": data.get("max_tokens_used", len(response_text.split()))
                    }
                else:
                    return {"success": False, "error": "空响应"}
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            logger.error(f"HuggingFace API调用失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _call_ollama(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """调用Ollama备用服务"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        logger.debug(f"Ollama请求: {url}")
        
        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True, 
            "response": data.get("response", ""),
            "model_used": f"Ollama-{self.ollama_model}",
            "tokens_used": len(data.get("response", "").split()),
            "server_info": {
                "model": data.get("model", ""),
                "created_at": data.get("created_at", "")
            }
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试服务器连接状态"""
        results = {
            "huggingface": {"available": False, "error": None},
            "ollama": {"available": False, "error": None},
            "recommended_service": None
        }
        
        # 测试HuggingFace
        try:
            url = f"{self.huggingface_url}/"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                results["huggingface"]["available"] = True
                results["huggingface"]["status"] = response.json()
                logger.info("✅ HuggingFace服务连接正常")
            else:
                results["huggingface"]["error"] = f"HTTP {response.status_code}"
        except Exception as e:
            results["huggingface"]["error"] = str(e)
            logger.warning(f"❌ HuggingFace连接失败: {e}")
        
        # 测试Ollama
        try:
            url = f"{self.ollama_url}/api/tags"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                results["ollama"]["available"] = True
                results["ollama"]["models"] = response.json()
                logger.info("✅ Ollama服务连接正常")
            else:
                results["ollama"]["error"] = f"HTTP {response.status_code}"
        except Exception as e:
            results["ollama"]["error"] = str(e)
            logger.warning(f"❌ Ollama连接失败: {e}")
        
        # 推荐服务
        if results["huggingface"]["available"]:
            results["recommended_service"] = "huggingface"
        elif results["ollama"]["available"]:
            results["recommended_service"] = "ollama"
        else:
            results["recommended_service"] = "none"
        
        return results

# 全局实例
_huggingface_service = None

def get_huggingface_service() -> HuggingFaceService:
    """获取HuggingFace服务单例"""
    global _huggingface_service
    if _huggingface_service is None:
        _huggingface_service = HuggingFaceService()
    return _huggingface_service

def get_ai_service_status() -> Dict[str, Any]:
    """获取AI服务状态"""
    service = get_huggingface_service()
    return service.test_connection()

# 兼容性函数
def grade_homework_with_ai(questions, ocr_text: str = "") -> Dict[str, Any]:
    """使用AI进行作业批改 - 兼容原接口"""
    service = get_huggingface_service()
    
    # 构建批改提示
    prompt = f"""请作为一名资深教师，对以下学生作业进行详细批改：

OCR识别结果:
{ocr_text}

题目信息:
{json.dumps(questions, ensure_ascii=False, indent=2)}

请提供:
1. 每题的详细批改意见
2. 错误点分析
3. 改进建议
4. 总体评价

请用中文回复，格式清晰。"""
    
    result = service.chat_completion(prompt)
    
    return {
        "knowledge_analysis": result.get("response", ""),
        "practice_questions": "",
        "multimodal_analysis": f"使用模型: {result.get('model_used', 'unknown')}",
        "ai_service_status": result.get("success", False),
        "error": result.get("error", None)
    }
