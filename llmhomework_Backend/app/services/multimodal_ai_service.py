# -*- coding: utf-8 -*-
"""
多模态AI服务 - 直接图片识别+批改（已弃用）
注意：此服务已被qwen_vl_direct_service替代，请使用新的直接调用LoRA服务
原：支持图片直接发送到Qwen3:30B进行识别和批改，替代传统OCR方案
迁移路径：Qwen3 → Qwen2.5-VL → Qwen2.5-VL-LoRA-Trained（当前）
推荐使用：qwen_vl_direct_service.py 进行直接调用
"""
import base64
import json
import requests
import logging
import uuid
from typing import Dict, Any, Optional
from app.config import Config
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class MultimodalAIService:
    """多模态AI服务 - 图片直接识别+批改"""
    
    def __init__(self):
        """初始化多模态AI服务"""
        # 使用服务器多模态API地址
        self.server_url = "http://172.31.179.77:8007"  # 直接指定多模态服务地址
        self.timeout = Config.TIMEOUT_SECONDS
        self.max_retries = 3
        
        logger.info(f"✅ 多模态AI服务初始化完成")
        logger.info(f"   服务器地址: {self.server_url}")
        logger.info(f"   超时时间: {self.timeout}秒")
    
    def analyze_homework_image(self, image_path: str) -> Dict[str, Any]:
        """
        直接分析作业图片，完成识别+批改
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            包含完整批改结果的字典
        """
        try:
            logger.info(f"🖼️ 开始多模态AI分析: {image_path}")
            
            # 1. 编码图片
            image_base64 = self._encode_image(image_path)
            if not image_base64:
                raise Exception("图片编码失败")
            
            # 2. 构建请求
            payload = self._build_multimodal_request(image_base64)
            
            # 3. 发送到服务器
            result = self._send_to_server(payload)
            
            # 4. 解析结果
            parsed_result = self._parse_ai_response(result)
            
            logger.info(f"✅ 多模态AI分析完成，识别到 {parsed_result.get('question_count', 0)} 道题目")
            return parsed_result
            
        except Exception as e:
            logger.error(f"❌ 多模态AI分析失败: {e}")
            raise Exception(f"多模态AI分析失败: {e}")
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 检查图片大小
            file_size = Path(image_path).stat().st_size
            logger.info(f"📸 图片编码完成，大小: {file_size/1024:.1f}KB")
            
            return encoded
        except Exception as e:
            logger.error(f"❌ 图片编码失败: {e}")
            return None
    
    def _build_multimodal_request(self, image_base64: str) -> Dict[str, Any]:
        """构建多模态请求"""
        # 添加唯一请求ID和时间戳防止缓存
        import time
        request_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000000)  # 微秒时间戳
        
        # 使用format方法避免f-string中的大括号问题
        prompt_template = """请求ID: {request_id}
时间戳: {timestamp}

请作为一名专业的教师，分析这张作业图片并进行详细批改。

请完成以下任务：
1. 识别图片中的所有题目内容（包括题目描述、学生答案）
2. 判断每道题的类型（计算题、应用题、选择题等）
3. 对每道题进行详细批改，包括：
   - 判断答案正确性
   - 给出准确分数
   - 提供标准答案
   - 详细的错误分析和改进建议
4. 分析错题涉及的知识点
5. 提供总体评价和学习建议

请按照以下JSON格式返回结果：
{{
  "questions": [
    {{
      "question_number": "题目编号",
      "question_text": "题目内容",
      "student_answer": "学生答案",
      "question_type": "题目类型",
      "is_correct": true/false,
      "score": "得分",
      "max_score": "满分",
      "correct_answer": "标准答案",
      "explanation": "详细批改说明",
      "error_analysis": "错误分析",
      "knowledge_points": ["相关知识点"]
    }}
  ],
  "overall_summary": {{
    "total_score": "总分",
    "total_possible": "总满分",
    "accuracy_rate": "正确率",
    "wrong_knowledge_points": ["错题知识点"],
    "suggestions": ["学习建议"]
  }}
}}

请确保分析准确、详细，特别注意数学计算的每个步骤。"""
        
        prompt = prompt_template.format(request_id=request_id, timestamp=timestamp)

        return {
            "image": image_base64,
            "prompt": prompt,
            "max_tokens": 200000,
            "temperature": 0.1,
            "request_id": request_id,  # 唯一请求ID
            "timestamp": timestamp,    # 时间戳
            "cache_bust": str(uuid.uuid4())  # 额外的缓存破坏器
        }
    
    def _send_to_server(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到服务器"""
        url = f"{self.server_url}/analyze"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                # 记录请求的详细信息用于调试
                import hashlib
                image_hash = hashlib.md5(payload["image"][:1000].encode()).hexdigest()[:8]  # MD5 hash前1000字符
                logger.info(f"📡 发送多模态请求到服务器 (尝试 {attempt + 1}/{self.max_retries})")
                logger.info(f"🔍 请求详情: request_id={payload['request_id'][:8]}..., image_hash={image_hash}")
                logger.info(f"🔍 图片大小: {len(payload['image'])} 字符")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ 服务器响应成功")
                    return result
                else:
                    raise Exception(f"服务器返回错误: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ 请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise Exception("服务器请求超时")
                time.sleep(2 ** attempt)  # 指数退避
                
            except Exception as e:
                logger.error(f"❌ 请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2)
    
    def _parse_ai_response(self, server_response: Dict[str, Any]) -> Dict[str, Any]:
        """解析AI响应为标准格式"""
        try:
            # 检查服务器响应格式
            if not server_response.get("success", False):
                raise Exception(f"服务器返回失败: {server_response.get('error', '未知错误')}")
            
            # 提取AI生成的内容
            ai_content = server_response.get("response", "")
            logger.info(f"📄 AI响应长度: {len(ai_content)} 字符")
            
            # 记录AI响应的前200字符用于调试
            if ai_content:
                preview = ai_content[:200].replace('\n', ' ')
                logger.info(f"📄 AI响应预览: {preview}...")
            else:
                logger.warning("⚠️ AI响应为空")
            
            # 尝试解析JSON
            if ai_content.strip().startswith("{"):
                try:
                    parsed_json = json.loads(ai_content)
                    logger.info("✅ AI响应JSON解析成功")
                    return self._convert_to_standard_format(parsed_json, server_response)
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON解析失败: {e}，尝试修复JSON")
                    # 尝试修复常见的JSON问题
                    fixed_json = self._fix_json_format(ai_content)
                    if fixed_json:
                        return self._convert_to_standard_format(fixed_json, server_response)
            
            # 如果不是JSON，进行文本解析
            logger.info("📝 使用文本解析模式")
            return self._parse_text_response(ai_content, server_response)
            
        except Exception as e:
            logger.error(f"❌ 响应解析失败: {e}")
            raise Exception(f"AI响应解析失败: {e}")
    
    def _fix_json_format(self, json_str: str) -> Optional[Dict[str, Any]]:
        """尝试修复常见的JSON格式问题"""
        try:
            # 移除可能的前缀文本
            json_start = json_str.find('{')
            if json_start > 0:
                json_str = json_str[json_start:]
            
            # 移除可能的后缀文本
            json_end = json_str.rfind('}')
            if json_end > 0:
                json_str = json_str[:json_end + 1]
            
            # 尝试解析修复后的JSON
            return json.loads(json_str)
        except:
            return None
    
    def _convert_to_standard_format(self, ai_json: Dict[str, Any], server_response: Dict[str, Any] = None) -> Dict[str, Any]:
        """将AI的JSON响应转换为系统标准格式"""
        questions = []
        
        # 调试信息：记录原始AI响应结构
        logger.info(f"🔍 AI原始响应键: {list(ai_json.keys())}")
        if "questions" in ai_json:
            logger.info(f"🔍 识别到题目数量: {len(ai_json['questions'])}")
            for i, q in enumerate(ai_json.get("questions", [])):
                question_preview = str(q.get("question_text", ""))[:50]
                answer_preview = str(q.get("student_answer", ""))[:30]
                logger.info(f"🔍 题目{i+1}: {question_preview}... | 答案: {answer_preview}...")
        else:
            logger.warning("⚠️ AI响应中缺少questions字段")
        
        for q in ai_json.get("questions", []):
            question = {
                "question": q.get("question_text", ""),
                "answer": q.get("student_answer", ""),
                "type": q.get("question_type", "未知题型"),
                "correct": q.get("is_correct", False),
                "score": float(q.get("score", 0)),
                "explanation": q.get("explanation", ""),
                "correct_answer": q.get("correct_answer", ""),
                "question_id": "multimodal_{}_{}_{}".format(int(time.time()), q.get('question_number', '1'), str(uuid.uuid4())[:8])
            }
            questions.append(question)
        
        summary = ai_json.get("overall_summary", {})
        
        result = {
            "success": True,
            "method": "multimodal_ai",
            "questions": questions,
            "summary": {
                "total_score": summary.get("total_score", 0),
                "accuracy_rate": summary.get("accuracy_rate", 0),
                "total_questions": len(questions)
            },
            "knowledge_analysis": {
                "wrong_knowledge_points": summary.get("wrong_knowledge_points", []),
                "suggestions": summary.get("suggestions", [])
            },
            "raw_ai_response": ai_json
        }
        
        # 添加服务器性能信息
        if server_response:
            result["server_info"] = {
                "model_used": server_response.get("model_used", "unknown"),
                "processing_time": server_response.get("processing_time", 0),
                "tokens_used": server_response.get("tokens_used", 0)
            }
        
        return result
    
    def _parse_text_response(self, text_content: str, server_response: Dict[str, Any] = None) -> Dict[str, Any]:
        """解析纯文本AI响应（备用方案）"""
        logger.info("📝 使用文本解析模式")
        
        # 基础解析，返回简化结果
        return {
            "success": True,
            "method": "multimodal_ai_text",
            "questions": [{
                "question": "图片识别题目",
                "answer": "学生答案",
                "type": "识别题型",
                "correct": False,
                "score": 0,
                "explanation": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                "correct_answer": "待分析",
                "question_id": "multimodal_text_{}_{}".format(int(time.time()), str(uuid.uuid4())[:8])
            }],
            "summary": {
                "total_score": 0,
                "accuracy_rate": 0,
                "total_questions": 1
            },
            "knowledge_analysis": {
                "wrong_knowledge_points": ["需要进一步分析"],
                "suggestions": ["建议使用标准答题格式"]
            },
            "raw_ai_response": text_content
        }
    
    def test_connection(self) -> bool:
        """测试与服务器的连接"""
        try:
            logger.info("🔍 测试多模态AI服务连接...")
            
            # 简单的健康检查
            health_url = f"{self.server_url}/health"
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ 多模态AI服务连接正常")
                return True
            else:
                logger.warning(f"⚠️ 服务器响应异常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 多模态AI服务连接失败: {e}")
            return False

# 全局实例
_multimodal_service = None

def get_multimodal_service() -> MultimodalAIService:
    """获取多模态AI服务单例"""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultimodalAIService()
    return _multimodal_service
