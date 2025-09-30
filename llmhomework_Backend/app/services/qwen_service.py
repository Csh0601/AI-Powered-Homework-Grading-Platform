import json
import re
import requests
import time
from typing import List, Dict, Any
import logging
from ..config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenService:
    def __init__(self, model_name: str = "qwen2.5-vl"):
        """
        初始化 Qwen 服务（已弃用）- 兼容性保留
        注意：此服务已被QwenVLClient替代，建议使用multimodal_client.py
        
        Args:
            model_name: Qwen 模型名称，默认为 qwen2.5-vl
        """
        self.model_name = model_name
        
        # 🎯 直接调用LoRA配置 - 兼容旧接口（已弃用，建议使用qwen_vl_direct_service）
        self.use_huggingface = getattr(Config, 'USE_HUGGINGFACE', False)
        self.huggingface_url = getattr(Config, 'HUGGINGFACE_BASE_URL', getattr(Config, 'QWEN_VL_API_URL', 'http://172.31.179.77:8007'))
        self.ollama_url = getattr(Config, 'OLLAMA_BASE_URL', None)
        self.timeout = Config.TIMEOUT_SECONDS
        self.use_direct_service = getattr(Config, 'USE_DIRECT_LORA_SERVICE', True)
        
        if self.use_direct_service:
            logger.info(f"✅ 注意：此服务已弃用，建议使用qwen_vl_direct_service进行直接调用")
            logger.info(f"🎯 LoRA服务地址: {self.huggingface_url}")
        elif self.use_huggingface:
            logger.info(f"✅ 优先使用HuggingFace服务: {self.huggingface_url}")
            logger.info(f"🔄 备用Ollama服务: {self.ollama_url}")
        else:
            # 备用：配置Ollama客户端
            import ollama
            import httpx
            self.client = ollama.Client(
                host=self.ollama_url,
                timeout=httpx.Timeout(300.0)  # 设置5分钟超时
            )
            logger.info(f"配置Ollama服务器: {self.ollama_url}")
            
        self._test_connection()
    
    def _test_connection(self):
        """测试AI服务连接"""
        if self.use_huggingface:
            # 测试HuggingFace服务
            try:
                logger.info(f"🔍 测试HuggingFace连接: {self.huggingface_url}")
                
                # 测试健康检查端点
                health_url = f"{self.huggingface_url}/health"
                response = requests.get(health_url, timeout=30)
                
                if response.status_code == 200:
                    logger.info("✅ HuggingFace服务连接正常")
                    
                    # HuggingFace服务健康检查通过，但我们现在使用多模态服务
                    logger.info("✅ HuggingFace服务健康，多模态服务可用")
                    return  # 健康检查通过，无需测试Ollama
                else:
                    logger.warning(f"⚠️ HuggingFace健康检查失败: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ HuggingFace连接失败: {e}")
                logger.info("🔄 将切换到Ollama备用服务")
        
        # 测试Ollama备用服务
        try:
            if not hasattr(self, 'client'):
                import ollama
                import httpx
                self.client = ollama.Client(
                    host=self.ollama_url,
                    timeout=httpx.Timeout(300.0)
                )
            
            logger.info(f"🔍 测试Ollama连接: {self.ollama_url}")
            
            # 尝试获取模型列表
            models = self.client.list()
            logger.info(f"原始模型响应: {models}")
            
            available_models = []
            if 'models' in models and models['models']:
                available_models = [model.get('name', '') for model in models['models']]
                available_models = [name for name in available_models if name.strip()]
                logger.info(f"可用Ollama模型: {available_models}")
            else:
                logger.warning("模型列表为空或格式异常")
                available_models = [self.model_name]  # 假设模型存在
                
            # 检查目标模型是否存在
            if self.model_name not in available_models:
                qwen_models = [name for name in available_models if 'qwen' in name.lower()]
                if qwen_models:
                    logger.warning(f"模型 {self.model_name} 不存在，尝试使用: {qwen_models[0]}")
                    self.model_name = qwen_models[0]
                elif not available_models or available_models == ['']:
                    logger.info(f"模型列表为空，直接尝试使用: {self.model_name}")
                else:
                    logger.error(f"未找到任何qwen模型，可用模型: {available_models}")
                    raise Exception(f"未找到qwen模型")
            
            # 测试模型生成功能
            logger.info(f"测试Ollama模型 {self.model_name} 生成功能...")
            test_response = self.client.generate(
                model=self.model_name,
                prompt="Hi",
                options={'num_predict': 3, 'temperature': 0.1},
                stream=False
            )
            
            if test_response and 'response' in test_response:
                logger.info(f"✅ Ollama备用服务连接成功")
                logger.info(f"测试响应: {test_response['response'][:50]}...")
            else:
                raise Exception(f"Ollama模型响应格式异常")
                
        except Exception as e:
            logger.error(f"❌ 所有AI服务连接失败: {e}")
            if "502" in str(e):
                logger.error("502错误：可能是服务未启动或端口未开放")
            elif "timeout" in str(e).lower():
                logger.error("超时错误：网络连接较慢或模型加载时间过长")
            
            raise Exception(f"无法连接到任何AI服务: {e}")
    
    def generate_response(self, prompt: str, max_tokens: int = 200000) -> str:
        """
        生成文本响应 - 优先HuggingFace，备用Ollama
        
        Args:
            prompt: 输入提示
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本响应
        """
        # 🔄 HuggingFace服务现在专用于多模态分析，直接使用Ollama进行文本生成
        if self.use_huggingface:
            logger.info("🔄 HuggingFace服务专用于多模态分析，使用Ollama进行文本生成")
        
        # 🥈 备用Ollama服务
        try:
            logger.info(f"🔄 使用Ollama备用服务生成响应")
            result = self._call_ollama_api(prompt, max_tokens)
            if result and result.strip():
                logger.info(f"✅ Ollama响应成功，长度: {len(result)} 字符")
                return result
        except Exception as e:
            logger.error(f"❌ Ollama调用失败: {e}")
            
        logger.error("❌ 所有AI服务均不可用")
        return ""
    
    # HuggingFace API现在专用于多模态分析，不再提供单独的文本生成接口
    # 文本生成统一使用Ollama服务
    
    def _call_ollama_api(self, prompt: str, max_tokens: int) -> str:
        """调用Ollama API（备用）"""
        if not hasattr(self, 'client'):
            import ollama
            import httpx
            self.client = ollama.Client(
                host=self.ollama_url,
                timeout=httpx.Timeout(300.0)
            )
        
        # 为批改任务移除stop参数，避免截断完整响应
        options = {
            'num_predict': max_tokens,
            'temperature': 0.1,
            'top_p': 0.9,
        }
        
        # 只在非批改任务中使用stop参数
        if max_tokens <= 100:
            options['stop'] = ['\n\n', '问题:', '题目:']
        
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options=options,
            stream=False
        )
        
        return response['response'].strip()
    
    def analyze_question_type(self, question: str) -> str:
        """
        分析题目类型
        
        Args:
            question: 题目文本
            
        Returns:
            题目类型
        """
        prompt = f"""请分析以下题目的类型，从以下选项中选择最合适的一个：
选择题、判断题、填空题、计算题、应用题、公式题、口算题

题目：{question}

请只回答题目类型，不要包含其他内容。"""
        
        response = self.generate_response(prompt, max_tokens=50)
        
        # 提取题目类型
        valid_types = ['选择题', '判断题', '填空题', '计算题', '应用题', '公式题', '口算题']
        for type_name in valid_types:
            if type_name in response:
                return type_name
        
        return '未知题型'
    
    def grade_question(self, question: str, student_answer: str, question_type: str) -> Dict[str, Any]:
        """
        批改单道题目
        
        Args:
            question: 题目内容
            student_answer: 学生答案
            question_type: 题目类型
            
        Returns:
            批改结果字典
        """
        if question_type == '计算题':
            return self._grade_calculation(question, student_answer)
        elif question_type == '选择题':
            return self._grade_multiple_choice(question, student_answer)
        elif question_type == '判断题':
            return self._grade_true_false(question, student_answer)
        elif question_type == '填空题':
            return self._grade_fill_blank(question, student_answer)
        else:
            return self._grade_general(question, student_answer, question_type)
    
    def _grade_calculation(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改计算题"""
        prompt = f"""作为一名专业的数学老师，请批改以下计算题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-5分
正确答案：[请提供完整的标准答案]
解释：详细的批改说明，包括完整的解题过程、计算步骤和最终答案

请务必：
1. 提供完整的正确解题过程
2. 指出学生答案中的错误（如果有）
3. 给出详细的数学计算步骤
4. 提供最终的正确答案"""

        response = self.generate_response(prompt, max_tokens=200000)  # 最大token数
        return self._parse_grading_response(response)
    
    def _grade_multiple_choice(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改选择题"""
        prompt = f"""作为一名专业老师，请批改以下选择题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-2分（选择题满分2分）
解释：简要说明正确答案和原因

请分析题目中的选项，确定正确答案。"""

        response = self.generate_response(prompt, max_tokens=200000)  # 最大token数
        return self._parse_grading_response(response)
    
    def _grade_true_false(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改判断题"""
        prompt = f"""作为一名专业老师，请批改以下判断题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-2分（判断题满分2分）
解释：简要说明正确答案和判断依据"""

        response = self.generate_response(prompt, max_tokens=200000)  # 最大token数
        return self._parse_grading_response(response)
    
    def _grade_fill_blank(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改填空题"""
        prompt = f"""作为一名专业老师，请批改以下填空题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误/部分正确
分数：0-3分（填空题满分3分）
解释：详细说明正确答案，如果学生答案部分正确则说明哪部分正确"""

        response = self.generate_response(prompt, max_tokens=200000)  # 最大token数
        return self._parse_grading_response(response)
    
    def _grade_general(self, question: str, student_answer: str, question_type: str) -> Dict[str, Any]:
        """通用批改方法"""
        prompt = f"""作为一名专业老师，请批改以下{question_type}：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误/部分正确
分数：0-5分
正确答案：[请提供标准答案]
解释：详细的批改说明，包括解题过程和知识点分析

请务必提供完整的正确答案和详细的解题步骤。"""

        response = self.generate_response(prompt, max_tokens=200000)  # 最大token数
        return self._parse_grading_response(response)
    
    def _parse_grading_response(self, response: str) -> Dict[str, Any]:
        """解析批改响应"""
        try:
            # 提取正确性
            correct = False
            if '正确性：正确' in response or '正确性: 正确' in response:
                correct = True
            elif '正确性：部分正确' in response or '正确性: 部分正确' in response:
                correct = True  # 部分正确也算正确
            
            # 提取分数
            score_match = re.search(r'分数[：:]\s*(\d+(?:\.\d+)?)', response)
            score = float(score_match.group(1)) if score_match else 0
            
            # 提取正确答案
            correct_answer_match = re.search(r'正确答案[：:]\s*(.*?)(?=\n解释|$)', response, re.DOTALL)
            correct_answer = correct_answer_match.group(1).strip() if correct_answer_match else "参考答案"
            
            # 提取解释（包含完整的响应内容）
            explanation_match = re.search(r'解释[：:]\s*(.*)', response, re.DOTALL)
            if explanation_match:
                explanation = explanation_match.group(1).strip()
            else:
                # 如果没有找到"解释"标记，使用整个响应
                explanation = response.strip()
            
            # 确保解释包含正确答案信息
            if correct_answer and correct_answer != "参考答案":
                explanation = f"正确答案：{correct_answer}\n\n{explanation}"
            
            return {
                'correct': correct,
                'score': score,
                'explanation': explanation,
                'correct_answer': correct_answer
            }
        
        except Exception as e:
            logger.error(f"解析批改响应失败: {e}")
            return {
                'correct': False,
                'score': 0,
                'explanation': '批改失败，请重试'
            }
    
    def analyze_knowledge_points(self, wrong_questions: List[Dict]) -> List[str]:
        """
        分析错题知识点
        
        Args:
            wrong_questions: 错题列表
            
        Returns:
            知识点列表
        """
        if not wrong_questions:
            return []
        
        questions_text = "\n".join([f"题目{i+1}: {q.get('question', '')}" 
                                  for i, q in enumerate(wrong_questions)])
        
        prompt = f"""请分析以下错题涉及的主要知识点，适合初中生水平：

{questions_text}

请列出3-5个主要知识点，每个知识点单独一行，格式如下：
1. 知识点名称
2. 知识点名称
...

只返回知识点列表，不要包含其他内容。"""

        response = self.generate_response(prompt, max_tokens=200000)
        
        # 提取知识点
        knowledge_points = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # 移除编号和符号
                point = re.sub(r'^\d+\.\s*|^[•\-]\s*', '', line).strip()
                if point:
                    knowledge_points.append(point)
        
        return knowledge_points[:5]  # 最多返回5个知识点
    
    def generate_practice_questions(self, knowledge_points: List[str], count: int = 3) -> List[Dict]:
        """
        根据知识点生成练习题
        
        Args:
            knowledge_points: 知识点列表
            count: 生成题目数量
            
        Returns:
            练习题列表
        """
        if not knowledge_points:
            return []
        
        knowledge_text = "、".join(knowledge_points)
        
        prompt = f"""基于以下知识点，为初中生生成{count}道练习题：

知识点：{knowledge_text}

要求：
1. 题目应该适合初中生水平
2. 包含不同类型的题目（选择题、填空题、计算题等）
3. 题目要有一定的梯度，从基础到提高

请按照以下格式生成题目：

题目1：
类型：[选择题/填空题/计算题]
题干：题目内容
选项：A. xxx B. xxx C. xxx D. xxx（如果是选择题）
答案：正确答案
解析：简要解析

题目2：
...

只返回题目内容，不要包含其他说明。"""

        response = self.generate_response(prompt, max_tokens=200000)
        
        # 解析生成的题目
        return self._parse_practice_questions(response)
    
    def _parse_practice_questions(self, response: str) -> List[Dict]:
        """解析生成的练习题"""
        questions = []
        
        try:
            # 按题目分割
            question_blocks = re.split(r'题目\d+[：:]', response)
            
            for block in question_blocks[1:]:  # 跳过第一个空块
                question_data = {}
                
                # 提取类型
                type_match = re.search(r'类型[：:]\s*([^\n]+)', block)
                if type_match:
                    question_data['type'] = type_match.group(1).strip()
                
                # 提取题干
                stem_match = re.search(r'题干[：:]\s*([^\n]+)', block)
                if stem_match:
                    question_data['stem'] = stem_match.group(1).strip()
                
                # 提取选项（如果是选择题）
                options_match = re.search(r'选项[：:]\s*([^答]+?)(?=答案|解析|$)', block, re.DOTALL)
                if options_match:
                    question_data['options'] = options_match.group(1).strip()
                
                # 提取答案
                answer_match = re.search(r'答案[：:]\s*([^\n]+)', block)
                if answer_match:
                    question_data['answer'] = answer_match.group(1).strip()
                
                # 提取解析
                explanation_match = re.search(r'解析[：:]\s*([^题]+?)(?=题目|$)', block, re.DOTALL)
                if explanation_match:
                    question_data['explanation'] = explanation_match.group(1).strip()
                
                if question_data.get('stem') and question_data.get('answer'):
                    questions.append(question_data)
        
        except Exception as e:
            logger.error(f"解析练习题失败: {e}")
        
        return questions
    
    def multimodal_analyze(self, image_text: str, question_context: str = "") -> Dict[str, Any]:
        """
        多模态分析：结合图像OCR文本和上下文进行分析
        
        Args:
            image_text: OCR识别的图像文本
            question_context: 题目上下文信息
            
        Returns:
            分析结果
        """
        prompt = f"""作为一名专业的教育AI助手，请分析以下从试卷图片中识别的文本内容：

OCR识别文本：
{image_text}

上下文信息：
{question_context}

请进行以下分析：
1. 文本内容质量评估（识别准确性）
2. 题目结构识别（题干、选项、答案区域）
3. 可能的OCR错误修正建议
4. 题目类型初步判断

请以结构化的方式回答，便于程序处理。"""

        response = self.generate_response(prompt, max_tokens=200000)
        
        return {
            'analysis': response,
            'text_quality': self._assess_text_quality(image_text),
            'structure_detected': self._detect_question_structure(image_text)
        }
    
    def _assess_text_quality(self, text: str) -> str:
        """评估OCR文本质量"""
        if not text or len(text.strip()) < 10:
            return "文本过短，可能识别不完整"
        
        # 检查常见OCR错误模式
        error_indicators = ['？？', '□□', '||', '@@', '##']
        if any(indicator in text for indicator in error_indicators):
            return "检测到可能的OCR错误标记"
        
        # 检查中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        
        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            return "文本质量良好"
        else:
            return "文本可能存在识别问题"
    
    def _detect_question_structure(self, text: str) -> Dict[str, bool]:
        """检测题目结构"""
        return {
            'has_question_number': bool(re.search(r'\d+[．\.\)）]', text)),
            'has_options': bool(re.search(r'[ABCD][\.．\)）]', text)),
            'has_blank': bool(re.search(r'_{2,}|（\s*）', text)),
            'has_calculation': bool(re.search(r'[+\-×÷=]|\d+\s*[+\-×÷]\s*\d+', text))
        }
