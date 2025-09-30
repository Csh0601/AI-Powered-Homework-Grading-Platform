#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接调用Qwen VL LoRA服务
解决structured_output字段无法正确返回的问题
"""
import requests
import json
import base64
import logging
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image
import time

# 配置日志
logger = logging.getLogger(__name__)

class QwenVLDirectService:
    """直接调用Qwen VL LoRA服务的客户端"""
    
    def __init__(self, server_url: str = "http://172.31.179.77:8007"):
        self.server_url = server_url
        self.analyze_endpoint = f"{server_url}/analyze"
        self.upload_endpoint = f"{server_url}/upload"
        self.health_endpoint = f"{server_url}/health"
        logger.info(f"🎯 初始化QwenVL直接服务客户端，API地址: {server_url}")
        
    def get_default_prompt(self) -> str:
        """获取默认的作业批改提示词"""
        return """现在你是一位初中的经验丰富，循循善诱的好老师，请你快速帮学生分析这张作业图片，并完成一些任务。

重要原则：
1. 如果图片是空白、无法识别、没有题目内容或过于模糊，请诚实说明，不要编造内容
2. 只有当你真的能够清晰识别到具体题目和答案时，才进行详细分析
3. 如果无法识别有效内容，请返回包含"error_type": "no_content"的JSON

分析重点（仅在能够识别题目时）：
1. 识别题目和学生答案
2. 判断对错和给分
3. 指出主要错误（如有）
4. 分析涉及的核心知识点和相应的做题方法
5. 不管学生答案是否正确，给出具体的两到三条学习建议，要贴合实际，让学生能快速的掌握类似题型
6. 不管学生答案是否正确，都要生成一道相似的题目，让学生能更好的掌握类似题型，并且生成的题目要比学生发送的题目略微难一些

如果能够识别到有效的题目内容，请返回详细的JSON格式结果：

```json
{
  "questions": [
    {
      "number": "题号（如1、2、3等）",
      "stem": "题目内容", 
      "answer": "学生答案",
      "type": "题目类型（选择题/填空题/计算题/应用题等）",
      "question_id": "题目唯一ID（自动生成如q_001、q_002等）",
      "similar_question": "相似的题目"
    }
  ],
  "grading_result": [
    {
      "question": "题目内容",
      "answer": "学生答案",
      "type": "题目类型",
      "correct": true/false,
      "score": 分数,
      "explanation": "简要说明（错误原因或正确要点）",
      "question_id": "对应的题目ID",
      "knowledge_points": ["相关知识点1", "相关知识点2"],
      "learning_suggestions": ["学习建议1", "学习建议2", "学习建议3"],
      "similar_question": "相似的题目"
    }
  ],
  "summary": {
    "total_questions": 总题数,
    "correct_count": 正确题数,
    "total_score": 总分,
    "accuracy_rate": 正确率,
    "main_issues": ["主要问题1", "主要问题2"],
    "knowledge_points": ["涉及的所有知识点"],
    "learning_suggestions": ["学习建议1", "学习建议2", "学习建议3"],
    "similar_question": "相似的题目"
  }
}
```

如果无法识别有效内容，请返回：
```json
{
  "error_type": "no_content",
  "message": "图片中无法识别到有效的题目内容",
  "questions": [],
  "grading_result": [],
  "summary": {
    "total_questions": 0,
    "correct_count": 0,
    "total_score": 0,
    "accuracy_rate": 0,
    "main_issues": ["图片内容无法识别"],
    "knowledge_points": []
  }
}
```

**CRITICAL: 必须严格返回JSON格式，不要添加任何解释文字，直接返回JSON结构！**"""

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            logger.info("🔍 检查Qwen VL直接服务健康状态...")
            response = requests.get(self.health_endpoint, timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ Qwen VL直接服务健康检查成功")
                return {
                    "status": "healthy",
                    "server_url": self.server_url,
                    "model_name": health_data.get("model_name", "未知"),
                    "model_loaded": health_data.get("model_loaded", False),
                    "details": health_data
                }
            else:
                error_msg = f"健康检查失败: HTTP {response.status_code}"
                logger.error(f"❌ {error_msg}")
                return {"status": "unhealthy", "message": error_msg}
                
        except requests.exceptions.Timeout:
            error_msg = f"健康检查超时: {self.health_endpoint}"
            logger.error(f"❌ {error_msg}")
            return {"status": "unhealthy", "message": error_msg}
        except Exception as e:
            error_msg = f"健康检查异常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"status": "unhealthy", "message": error_msg}

    def analyze_homework_image(self, image_base64: str, custom_prompt: str = None) -> Dict[str, Any]:
        """
        分析作业图片
        
        Args:
            image_base64: base64编码的图片数据
            custom_prompt: 自定义提示词（可选）
            
        Returns:
            包含structured_output的完整响应
        """
        prompt = custom_prompt or self.get_default_prompt()
        
        payload = {
            "image": image_base64,
            "prompt": prompt,
            "max_tokens": 8000,
            "temperature": 0.1
        }
        
        try:
            logger.info("🚀 开始调用Qwen VL直接分析接口...")
            response = requests.post(
                self.analyze_endpoint,
                json=payload,
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Qwen VL直接分析成功，用时: {result.get('processing_time', 0):.2f}秒")
                
                # 检查响应结构
                if result.get("success"):
                    # 尝试解析response字段中的JSON
                    response_text = result.get("response", "")
                    
                    try:
                        # 尝试解析JSON结构
                        if isinstance(response_text, str):
                            # 清理可能的额外文本，提取JSON部分
                            import re
                            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group()
                                structured_data = json.loads(json_str)
                            else:
                                # 如果没有找到JSON，尝试直接解析
                                structured_data = json.loads(response_text)
                        else:
                            structured_data = response_text
                        
                        # 验证必要字段
                        if isinstance(structured_data, dict):
                            return {
                                "success": True,
                                "structured_output": structured_data,
                                "raw_response": response_text,
                                "processing_time": result.get("processing_time", 0),
                                "model_used": result.get("model_used", "Qwen2.5-VL-32B-Instruct-LoRA-Trained"),
                                "analysis_type": result.get("analysis_type", "lora_multimodal")
                            }
                        else:
                            logger.warning("⚠️ 解析的数据不是字典格式")
                            return {
                                "success": False,
                                "error": "解析的结构化数据格式错误",
                                "raw_response": response_text,
                                "details": structured_data
                            }
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ JSON解析失败: {e}")
                        return {
                            "success": False,
                            "error": f"JSON解析失败: {e}",
                            "raw_response": response_text
                        }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "服务器返回失败状态"),
                        "details": result
                    }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Qwen VL直接分析失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.Timeout:
            error_msg = "请求超时，服务器处理时间过长"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"请求异常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }

    def test_connection(self) -> bool:
        """测试连接"""
        health = self.health_check()
        return health.get("status") == "healthy"

def robust_analyze_homework(image_base64: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    带重试机制的作业分析
    """
    service = QwenVLDirectService()
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试分析作业 (第{attempt + 1}/{max_retries}次)")
            
            result = service.analyze_homework_image(image_base64)
            
            if result["success"]:
                logger.info("✅ 作业分析成功")
                return result
            else:
                last_error = result.get("error", "未知错误")
                logger.warning(f"⚠️ 分析失败: {last_error}")
                
                # 如果是结构化输出问题，可以尝试重新请求
                if "解析" in last_error and attempt < max_retries - 1:
                    logger.info("🔄 检测到解析问题，准备重试...")
                    continue
                    
        except Exception as e:
            last_error = str(e)
            logger.error(f"❌ 分析异常: {last_error}")
            
        # 如果不是最后一次尝试，等待一段时间再重试
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 指数退避
    
    return {
        "success": False,
        "error": f"多次尝试后仍然失败: {last_error}",
        "attempts": max_retries
    }

def process_homework_image(image_base64: str) -> Dict[str, Any]:
    """处理作业图片的主函数"""
    result = robust_analyze_homework(image_base64)
    
    if result["success"] and "structured_output" in result:
        # 成功获得结构化输出
        structured_data = result["structured_output"]
        
        # 提取关键信息
        questions = structured_data.get("questions", [])
        grading_results = structured_data.get("grading_result", [])
        summary = structured_data.get("summary", {})
        
        # 处理学习建议和相似题目
        learning_suggestions = []
        similar_questions = []
        
        # 从grading_result中收集
        for grade_result in grading_results:
            if "learning_suggestions" in grade_result and isinstance(grade_result["learning_suggestions"], list):
                learning_suggestions.extend(grade_result["learning_suggestions"])
            if "similar_question" in grade_result and grade_result["similar_question"]:
                similar_questions.append({
                    "question_id": grade_result.get("question_id", "unknown"),
                    "original_question": grade_result.get("question", ""),
                    "similar_question": grade_result["similar_question"],
                    "type": grade_result.get("type", "")
                })
        
        # 从summary中收集
        if "learning_suggestions" in summary and isinstance(summary["learning_suggestions"], list):
            learning_suggestions.extend(summary["learning_suggestions"])
        if "similar_question" in summary and summary["similar_question"]:
            similar_questions.append({
                "question_id": "summary",
                "original_question": "整体练习",
                "similar_question": summary["similar_question"],
                "type": "综合练习"
            })
        
        # 去重
        learning_suggestions = list(set(learning_suggestions))
        
        return {
            "success": True,
            "questions": questions,
            "grading_result": grading_results,
            "summary": summary,
            "learning_suggestions": learning_suggestions,
            "similar_questions": similar_questions,
            "knowledge_analysis": {
                "study_recommendations": learning_suggestions,
                "wrong_knowledge_points": []  # 可以从错题中提取
            },
            "processing_info": {
                "model_used": result["model_used"],
                "processing_time": result["processing_time"],
                "analysis_type": result.get("analysis_type", "lora_multimodal")
            }
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "未知错误"),
            "raw_response": result.get("raw_response", "")
        }

# 全局实例
qwen_vl_direct_service = QwenVLDirectService()

def get_qwen_vl_direct_service() -> QwenVLDirectService:
    """获取全局QwenVL直接服务实例"""
    return qwen_vl_direct_service
