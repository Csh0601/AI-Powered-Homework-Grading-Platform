# -*- coding: utf-8 -*-
"""
Qwen2.5-VL多模态客户端
从Qwen3-30B文本模型迁移到Qwen2.5-VL-32B-Instruct多模态模型
"""
import requests
import base64
import json
import logging
import time
import re
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image
import os

# 确保在客户端层也显式禁用 Flash Attention/Triton，以防服务端未正确设置
os.environ.setdefault("PYTORCH_ENABLE_TRITON", "0")
os.environ.setdefault("TORCHINDUCTOR_DISABLE_TRITON", "1")
os.environ.setdefault("FLASH_ATTENTION_FORCE_DISABLED", "1")
os.environ.setdefault("ATTN_IMPLEMENTATION", "eager")
os.environ.setdefault("PYTORCH_NO_FAST_ATTENTION", "1")

logger = logging.getLogger(__name__)


def clean_json_string(text: str) -> str:
    """
    清理JSON字符串中的非法转义字符（备用方案）
    
    **注意**: 由于服务器端已经处理了JSON转义，这里只作为备用
    
    Args:
        text: 原始JSON字符串
        
    Returns:
        清理后的JSON字符串
    """
    if not text:
        return text
    
    try:
        # 先尝试直接解析
        try:
            json.loads(text)
            return text  # 如果能解析，直接返回
        except json.JSONDecodeError:
            # 只有失败时才修复
            fixed_text = re.sub(
                r'\\(?=[^"\\\/bfnrtu\s])',
                r'\\\\',
                text
            )
            return fixed_text
        
    except Exception as e:
        logger.error(f"❌ JSON清理过程出错: {e}")
        return text

class QwenVLClient:
    """Qwen2.5-VL多模态客户端"""
    
    def __init__(self, api_url: str = "http://172.31.179.77:8007"):
        self.api_url = api_url
        self.analyze_endpoint = f"{api_url}/analyze"
        self.health_endpoint = f"{api_url}/health"
        logger.info(f"🎯 初始化QwenVL客户端，API地址: {api_url}")
        
    def encode_image_safe(self, image_data) -> str:
        """安全编码图片为base64 - 修复文件路径问题"""
        try:
            logger.info(f"🔍 输入数据类型: {type(image_data)}")
            logger.info(f"🔍 输入数据内容: {str(image_data)[:100]}...")
            
            # 🔥 关键修复：正确处理文件路径
            if isinstance(image_data, str):
                # 确保是绝对路径且文件存在
                if not os.path.isabs(image_data):
                    image_data = os.path.abspath(image_data)
                    
                if not os.path.exists(image_data):
                    raise ValueError(f"图片文件不存在: {image_data}")
                
                # 🔥 新增: 检查原始文件大小
                original_size = os.path.getsize(image_data)
                logger.info(f"📁 原始文件大小: {original_size} 字节 ({original_size/1024/1024:.2f}MB)")
                
                # 🔥 如果图片过大，进行预处理
                if original_size > 3 * 1024 * 1024:  # 超过3MB
                    logger.warning(f"⚠️ 图片过大({original_size/1024/1024:.2f}MB)，进行压缩处理...")
                    image_bytes = self._compress_image(image_data, max_size_mb=1.0)
                else:
                    with open(image_data, "rb") as f:
                        image_bytes = f.read()
                
                # 验证文件不为空
                if len(image_bytes) == 0:
                    raise ValueError("图片文件为空")
                    
                logger.info(f"📁 读取图片文件: {image_data}")
                logger.info(f"📊 处理后文件大小: {len(image_bytes)} 字节")
                
            elif isinstance(image_data, bytes):
                image_bytes = image_data
                logger.info(f"📊 直接处理字节数据，大小: {len(image_bytes)} 字节")
                
            elif isinstance(image_data, Image.Image):
                buffer = BytesIO()
                image_data.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()
                logger.info(f"📊 PIL图片转换，大小: {len(image_bytes)} 字节")
                
            else:
                raise ValueError(f"不支持的图片格式: {type(image_data)}")
            
            # 编码为base64
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            
            # 验证编码结果
            if len(encoded) < 1000:  # base64图片通常很长
                raise ValueError(f"编码结果异常短: {len(encoded)} 字符")
                
            logger.info(f"✅ 图片编码成功，长度: {len(encoded)} 字符")
            logger.info(f"📤 base64前缀: {encoded[:50]}...")
            return encoded
            
        except Exception as e:
            logger.error(f"❌ 图片编码失败: {e}")
            raise ValueError(f"图片编码失败: {e}")
    
    def encode_image(self, image_path_or_bytes) -> str:
        """将图片编码为base64（兼容旧接口）"""
        return self.encode_image_safe(image_path_or_bytes)
    
    def analyze_homework(self, image_data, prompt: str = "请详细分析这张作业图片，进行批改和评分") -> Dict[str, Any]:
        """分析作业图片 - 增强调试和重试机制"""
        
        max_retries = 2
        original_image_data = image_data
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"🎯 开始多模态作业分析... (尝试 {attempt + 1}/{max_retries + 1})")
                logger.info(f"🔍 输入数据类型: {type(image_data)}")
                logger.info(f"🔍 输入数据预览: {str(image_data)[:100]}...")
                
                # 🔥 修复：始终使用安全编码方法
                image_base64 = self.encode_image_safe(image_data)
                
                # 构建请求
                request_data = {
                    "image": image_base64,
                    "prompt": prompt,
                    "max_tokens": 8000,  # 优化性能
                    "temperature": 0.1   # 降低随机性，提高一致性
                }
                
                logger.info(f"发送请求到: {self.analyze_endpoint}")
                
                # 发送请求 - 增加超时时间应对服务器负载
                response = requests.post(
                    self.analyze_endpoint,
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=300  # 5分钟超时 - 给服务器更多处理时间
                )
                
                logger.info(f"服务器响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        logger.info(f"✅ 多模态分析成功，用时: {result.get('processing_time', 0):.2f}秒")
                        payload = {
                            "success": True,
                            "data": result.get("response"),
                            "processing_time": result.get("processing_time"),
                            "model_used": result.get("model_used", "Qwen2.5-VL-32B-Instruct-LoRA-Trained"),
                            "analysis_type": "true_multimodal",
                        }
                        structured = result.get("structured_output") or {}
                        if structured:
                            payload.update(structured)
                        return payload
                    else:
                        error_msg = result.get('error', '未知错误')
                        logger.error(f"❌ 分析失败: {error_msg}")
                        
                        # 🔥 检查是否是tensor错误，如果是则触发重试机制
                        is_tensor_error = ("probability tensor" in error_msg or 
                                         "inf" in error_msg or 
                                         "nan" in error_msg)
                        
                        if is_tensor_error and attempt < max_retries:
                            logger.warning("⚠️ 检测到tensor错误，分析服务器状态并尝试恢复...")
                            
                            # 🔥 新增：诊断服务器状态
                            server_status = self._diagnose_server_status()
                            logger.info(f"🏥 服务器诊断结果: {server_status}")
                            
                            # 根据诊断结果调整策略
                            if server_status.get("gpu_memory_low", False):
                                logger.warning("⚠️ GPU内存不足，等待30秒让服务器清理内存...")
                                import time
                                time.sleep(30)
                            
                            if isinstance(original_image_data, str):
                                # 使用更激进的压缩
                                max_size = 0.3 if attempt == 1 else 0.1  # 逐步更激进
                                compressed_bytes = self._compress_image(original_image_data, max_size_mb=max_size)
                                # 保存临时压缩文件
                                import tempfile
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                    tmp_file.write(compressed_bytes)
                                    image_data = tmp_file.name
                                logger.info(f"🔄 重试使用超级压缩图片: {len(compressed_bytes)/1024/1024:.2f}MB")
                                continue
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "analysis_type": "true_multimodal"
                        }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ 服务器响应错误: {error_msg}")
                    
                    # 检查是否是服务器问题需要重试
                    should_retry = False
                    retry_delay = 3
                    
                    if "tensor" in response.text or "inf" in response.text or "nan" in response.text:
                        logger.warning("⚠️ HTTP响应中包含tensor错误，尝试重试...")
                        should_retry = True
                    elif "CUDA out of memory" in response.text:
                        logger.warning("⚠️ 服务器GPU内存不足，30秒后重试...")
                        should_retry = True
                        retry_delay = 30
                    elif response.status_code in [502, 503, 504]:
                        logger.warning(f"⚠️ 服务器过载(HTTP {response.status_code})，15秒后重试...")
                        should_retry = True
                        retry_delay = 15
                    
                    if should_retry and attempt < max_retries:
                        import time
                        time.sleep(retry_delay)
                        continue
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "analysis_type": "true_multimodal"
                    }
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    logger.warning(f"⚠️ 请求超时，3秒后重试...")
                    import time
                    time.sleep(3)
                    continue
                else:
                    error_msg = "请求超时，可能是图片太大或服务器繁忙"
                    logger.error(f"❌ {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "analysis_type": "true_multimodal"
                    }
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    logger.warning(f"⚠️ 连接错误，3秒后重试...")
                    import time
                    time.sleep(3)
                    continue
                else:
                    error_msg = "无法连接到多模态服务器"
                    logger.error(f"❌ {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "analysis_type": "true_multimodal"
                    }
            except Exception as e:
                error_str = str(e)
                
                # 检查是否是我们标记的tensor错误
                if "Tensor错误需要重试" in error_str and attempt < max_retries:
                    logger.warning("🔄 tensor错误重试机制触发...")
                    if isinstance(original_image_data, str):
                        # 使用更激进的压缩
                        compressed_bytes = self._compress_image(original_image_data, max_size_mb=0.3)
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                            tmp_file.write(compressed_bytes)
                            image_data = tmp_file.name
                        logger.info(f"🔄 超级压缩重试: {len(compressed_bytes)/1024/1024:.2f}MB")
                        continue
                
                if attempt < max_retries:
                    logger.warning(f"⚠️ 分析异常，3秒后重试: {e}")
                    import time
                    time.sleep(3)
                    continue
                else:
                    error_msg = f"多模态分析异常: {error_str}"
                    logger.error(error_msg, exc_info=True)
                    return {
                        "success": False,
                        "error": error_msg,
                        "analysis_type": "true_multimodal"
                    }
        
        # 如果所有重试都失败了
        logger.error("❌ 所有重试尝试都失败了")
        return {
            "success": False,
            "error": "经过多次重试仍然失败，请检查图片质量或稍后重试",
            "analysis_type": "true_multimodal"
        }
    
    def analyze_homework_with_structured_output(self, image_data) -> Dict[str, Any]:
        """
        分析作业图片并返回结构化输出
        适配现有的grading_result格式
        """
        # 使用与服务器端一致的新提示词模板
        structured_prompt = """现在你是一位初中的经验丰富，循循善诱的好老师，请你快速帮学生分析这张作业图片，并完成一些任务。

重要原则：
1. 如果图片是空白、无法识别、没有题目内容或过于模糊，请诚实说明，不要编造内容
2. 只有当你真的能够清晰识别到具体题目和答案时，才进行详细分析
3. 如果无法识别有效内容，请返回包含"error_type": "no_content"的JSON

分析重点（仅在能够识别题目时）：
1. 识别题目和学生答案
2. 判断对错和给分
3. 指出主要错误（如有）
4. 分析涉及的核心知识点和相应的做题方法
5. 给出具体的两到三条学习建议，要贴合实际，让学生能快速的掌握类似提醒
6. 生成一道相似的题目，让学生能更好的掌握类似题型，并且生成的题目要比学生发送的题目略微难一些

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
```"""
        
        result = self.analyze_homework(image_data, structured_prompt)
        
        if result["success"]:
            try:
                # 尝试解析JSON结构
                response_data = result["data"]
                if isinstance(response_data, str):
                    # 直接尝试解析（服务器端已处理转义）
                    try:
                        parsed_data = json.loads(response_data)
                    except json.JSONDecodeError as e:
                        # 只有失败时才使用清理函数
                        logger.warning(f"⚠️ 直接解析失败，使用清理函数: {e}")
                        cleaned_data = clean_json_string(response_data)
                        parsed_data = json.loads(cleaned_data)
                else:
                    parsed_data = response_data
                
                # 检查是否是错误类型（无内容识别）
                if parsed_data.get("error_type") == "no_content":
                    logger.warning("图片内容无法识别")
                    return {
                        "success": False,
                        "error": parsed_data.get("message", "图片中无法识别到有效的题目内容"),
                        "error_type": "no_content",
                        "questions": [],
                        "grading_result": [],
                        "summary": parsed_data.get("summary", {}),
                        "method": "multimodal_direct",
                        "processing_time": result.get("processing_time"),
                        "model_used": result.get("model_used")
                    }
                
                # 验证并格式化数据
                questions = parsed_data.get("questions", [])
                grading_result = parsed_data.get("grading_result", [])
                summary = parsed_data.get("summary", {})
                
                # 保持向后兼容：如果没有knowledge_analysis，从其他地方提取
                knowledge_analysis = parsed_data.get("knowledge_analysis", {})
                if not knowledge_analysis:
                    # 从grading_result中提取学习建议和知识点
                    all_learning_suggestions = []
                    all_knowledge_points = []
                    for item in grading_result:
                        if item.get("learning_suggestions"):
                            all_learning_suggestions.extend(item["learning_suggestions"])
                        if item.get("knowledge_points"):
                            all_knowledge_points.extend(item["knowledge_points"])
                    
                    knowledge_analysis = {
                        "study_recommendations": list(set(all_learning_suggestions)),
                        "wrong_knowledge_points": []
                    }
                
                return {
                    "success": True,
                    "questions": questions,
                    "grading_result": grading_result,
                    "summary": summary,
                    "knowledge_analysis": knowledge_analysis,
                    "method": "multimodal_direct",
                    "processing_time": result.get("processing_time"),
                    "model_used": result.get("model_used")
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败，返回原始文本: {e}")
                # 如果JSON解析失败，返回原始响应
                return {
                    "success": True,
                    "raw_response": result["data"],
                    "method": "multimodal_raw",
                    "processing_time": result.get("processing_time"),
                    "model_used": result.get("model_used"),
                    "note": "返回原始文本，需要进一步解析"
                }
        else:
            return result
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            logger.info("🔍 检查多模态服务健康状态...")
            response = requests.get(self.health_endpoint, timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ 多模态服务健康")
                return {
                    "status": "healthy",
                    "server_info": health_data,
                    "api_url": self.api_url
                }
            else:
                logger.warning(f"⚠️ 服务器响应异常: HTTP {response.status_code}")
                return {
                    "status": "error", 
                    "message": f"HTTP {response.status_code}",
                    "api_url": self.api_url
                }
        except requests.exceptions.ConnectionError:
            logger.error("❌ 无法连接到多模态服务器")
            return {
                "status": "error", 
                "message": "无法连接到服务器",
                "api_url": self.api_url
            }
        except Exception as e:
            logger.error(f"❌ 健康检查异常: {e}")
            return {
                "status": "error", 
                "message": str(e),
                "api_url": self.api_url
            }
    
    def test_connection(self) -> bool:
        """测试连接（简化版健康检查）"""
        health_status = self.health_check()
        return health_status.get("status") == "healthy"
    
    def _compress_image(self, image_path: str, max_size_mb: float = 1.0) -> bytes:
        """压缩图片文件到指定大小"""
        try:
            img = Image.open(image_path)
            return self._compress_pil_image(img, max_size_mb)
        except Exception as e:
            logger.error(f"❌ 图片压缩失败: {e}")
            # 如果压缩失败，返回原始文件
            with open(image_path, "rb") as f:
                return f.read()
    
    def _compress_pil_image(self, img: Image.Image, max_size_mb: float = 1.0) -> bytes:
        """压缩PIL图片到指定大小"""
        # 首先尝试调整尺寸
        width, height = img.size
        logger.info(f"📐 原始尺寸: {width}x{height}")
        
        # 如果图片过大，先缩放
        if width > 1600 or height > 1600:
            # 保持比例，最大边设为1600
            ratio = min(1600/width, 1600/height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"📐 图片缩放: {width}x{height} -> {new_size[0]}x{new_size[1]}")
        
        # 转换为RGB（如果是RGBA或其他格式）
        if img.mode in ('RGBA', 'LA'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 尝试不同的质量设置
        for quality in [85, 75, 65, 55, 45, 35]:
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            img_bytes = buffer.getvalue()
            
            size_mb = len(img_bytes) / 1024 / 1024
            logger.info(f"🎯 质量{quality}: {size_mb:.2f}MB")
            
            if size_mb <= max_size_mb:
                logger.info(f"✅ 压缩成功: 质量{quality}, 大小{size_mb:.2f}MB")
                return img_bytes
        
        # 如果还是太大，返回最低质量的版本
        logger.warning(f"⚠️ 无法压缩到目标大小，使用最低质量版本")
        return img_bytes
    
    def _diagnose_server_status(self) -> Dict[str, Any]:
        """诊断服务器状态，分析tensor错误原因"""
        diagnosis = {
            "timestamp": time.time(),
            "gpu_memory_low": False,
            "server_overloaded": False,
            "model_state_issue": False,
            "suggestions": []
        }
        
        try:
            # 尝试获取服务器详细状态
            import requests
            
            # 检查健康状态
            health_response = requests.get(
                f"{self.api_url}/health", 
                timeout=30
            )
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                diagnosis["server_healthy"] = True
                diagnosis["health_info"] = health_data
            else:
                diagnosis["server_healthy"] = False
                
            # 尝试发送极简测试请求
            test_image = self._create_minimal_test_image()
            test_response = requests.post(
                self.analyze_endpoint,
                json={
                    "image": test_image,
                    "prompt": "测试",
                    "max_tokens": 50,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                test_result = test_response.json()
                if test_result.get("success"):
                    diagnosis["minimal_test_passed"] = True
                    diagnosis["suggestions"].append("服务器基本功能正常，可能是特定图片问题")
                else:
                    error_msg = test_result.get("error", "")
                    if "memory" in error_msg.lower() or "cuda" in error_msg.lower():
                        diagnosis["gpu_memory_low"] = True
                        diagnosis["suggestions"].append("GPU内存不足，建议等待或联系管理员")
                    elif "tensor" in error_msg:
                        diagnosis["model_state_issue"] = True
                        diagnosis["suggestions"].append("模型状态异常，建议联系管理员重启模型")
            else:
                diagnosis["server_overloaded"] = True
                diagnosis["suggestions"].append("服务器过载，建议稍后重试")
                
        except requests.exceptions.Timeout:
            diagnosis["server_overloaded"] = True
            diagnosis["suggestions"].append("服务器响应超时，负载过重")
        except Exception as e:
            diagnosis["diagnostic_error"] = str(e)
            diagnosis["suggestions"].append("无法完成服务器诊断")
            
        return diagnosis
    
    def _create_minimal_test_image(self) -> str:
        """创建最小测试图片的base64编码"""
        try:
            from PIL import Image, ImageDraw
            import base64
            from io import BytesIO
            
            # 创建最小的测试图片
            img = Image.new('RGB', (100, 50), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "Test", fill='black')
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=50)
            img_bytes = buffer.getvalue()
            
            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"创建测试图片失败: {e}")
            # 返回一个极简的base64图片
            return "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAyAGQDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAxQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//"

# 全局客户端实例
qwen_vl_client = QwenVLClient()

def get_qwen_vl_client() -> QwenVLClient:
    """获取全局QwenVL客户端实例"""
    return qwen_vl_client

# 新增：集成直接调用服务
def get_qwen_vl_direct_service():
    """获取QwenVL直接调用服务实例"""
    try:
        from .qwen_vl_direct_service import get_qwen_vl_direct_service
        return get_qwen_vl_direct_service()
    except ImportError as e:
        logger.error(f"无法导入直接调用服务: {e}")
        return None

def analyze_homework_with_direct_service(image_path: str) -> Dict[str, Any]:
    """
    使用直接调用服务分析作业
    这是新的推荐方式，可以获得完整的structured_output
    """
    try:
        # 获取直接调用服务
        direct_service = get_qwen_vl_direct_service()
        if not direct_service:
            return {
                "success": False,
                "error": "直接调用服务不可用"
            }
        
        # 编码图片为base64
        client = get_qwen_vl_client()
        image_base64 = client.encode_image_safe(image_path)
        
        if not image_base64:
            return {
                "success": False,
                "error": "图片编码失败"
            }
        
        # 调用直接服务进行分析
        from .qwen_vl_direct_service import process_homework_image
        result = process_homework_image(image_base64)
        
        if result["success"]:
            logger.info("✅ 直接调用服务分析成功")
            return {
                "success": True,
                "questions": result["questions"],
                "grading_result": result["grading_result"],
                "summary": result["summary"],
                "knowledge_analysis": result["knowledge_analysis"],
                "learning_suggestions": result["learning_suggestions"],
                "similar_questions": result["similar_questions"],
                "method": "direct_service",
                "processing_time": result["processing_info"]["processing_time"],
                "model_used": result["processing_info"]["model_used"],
                "analysis_type": result["processing_info"]["analysis_type"]
            }
        else:
            logger.error(f"❌ 直接调用服务分析失败: {result['error']}")
            return result
            
    except Exception as e:
        logger.error(f"❌ 直接调用服务异常: {e}")
        return {
            "success": False,
            "error": f"直接调用服务异常: {e}"
        }
