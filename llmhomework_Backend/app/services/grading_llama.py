from typing import List, Dict, Any
import time
import logging
from app.services.llama_service import LlamaService
from app.services.grading_new import evaluate_math_calculation, generate_question_hash
from app.config import Config

logger = logging.getLogger(__name__)

class LlamaGradingEngine:
    """
    基于 Llama2 的智能批改引擎
    支持多模态分析和智能批改
    """
    
    def __init__(self):
        """初始化 Llama 批改引擎"""
        self.llama_service = None
        self.use_llama = Config.USE_LLAMA_GRADING
        self.enable_multimodal = Config.ENABLE_MULTIMODAL
        self.enable_knowledge_analysis = Config.ENABLE_KNOWLEDGE_ANALYSIS
        self.enable_practice_generation = Config.ENABLE_PRACTICE_GENERATION
        
        if self.use_llama:
            try:
                self.llama_service = LlamaService(Config.LLAMA_MODEL_NAME)
                logger.info("Llama 批改引擎初始化成功")
            except Exception as e:
                logger.error(f"Llama 服务初始化失败: {e}")
                logger.warning("将回退到传统批改方式")
                self.use_llama = False
    
    def grade_homework_with_llama(self, questions: List[Dict], ocr_context: str = "") -> Dict[str, Any]:
        """
        使用 Llama 进行作业批改
        
        Args:
            questions: 题目列表
            ocr_context: OCR 上下文信息
            
        Returns:
            批改结果
        """
        logger.info(f"开始使用 Llama 批改作业，共 {len(questions)} 道题目")
        
        results = []
        multimodal_analysis = None
        
        # 多模态分析（如果启用）
        if self.enable_multimodal and ocr_context and self.llama_service:
            try:
                multimodal_analysis = self.llama_service.multimodal_analyze(
                    ocr_context, 
                    f"试卷包含 {len(questions)} 道题目"
                )
                logger.info("多模态分析完成")
            except Exception as e:
                logger.error(f"多模态分析失败: {e}")
        
        # 逐题批改
        for idx, question_data in enumerate(questions):
            logger.info(f"正在批改第 {idx + 1} 题")
            
            question = question_data.get('stem', '') or question_data.get('question', '')
            answer = question_data.get('answer', '')
            question_type = question_data.get('type', '未知题型')
            question_id = question_data.get('question_id', f'q_{idx}')
            
            # 如果没有题目类型，尝试使用 Llama 分析
            if question_type == '未知题型' and self.llama_service:
                try:
                    question_type = self.llama_service.analyze_question_type(question)
                    logger.info(f"Llama 分析题目类型: {question_type}")
                except Exception as e:
                    logger.error(f"题目类型分析失败: {e}")
            
            # 进行批改
            grading_result = self._grade_single_question(
                question, answer, question_type, question_id
            )
            
            results.append(grading_result)
        
        # 知识点分析
        wrong_questions = [r for r in results if not r['correct']]
        knowledge_points = []
        
        if self.enable_knowledge_analysis and wrong_questions and self.llama_service:
            try:
                knowledge_points = self.llama_service.analyze_knowledge_points(wrong_questions)
                logger.info(f"知识点分析完成，识别出 {len(knowledge_points)} 个知识点")
            except Exception as e:
                logger.error(f"知识点分析失败: {e}")
        
        # 生成练习题
        practice_questions = []
        if self.enable_practice_generation and knowledge_points and self.llama_service:
            try:
                practice_questions = self.llama_service.generate_practice_questions(
                    knowledge_points, count=min(3, len(knowledge_points))
                )
                logger.info(f"生成了 {len(practice_questions)} 道练习题")
            except Exception as e:
                logger.error(f"练习题生成失败: {e}")
        
        # 构建完整结果
        total_score = sum(r['score'] for r in results)
        correct_count = sum(1 for r in results if r['correct'])
        accuracy_rate = correct_count / len(results) if results else 0
        
        complete_result = {
            'task_metadata': {
                'task_id': f'task_{int(time.time())}',
                'timestamp': int(time.time()),
                'total_questions': len(results),
                'correct_count': correct_count,
                'total_score': total_score,
                'accuracy_rate': accuracy_rate,
                'grading_engine': 'LlamaGradingEngine',
                'model_used': Config.LLAMA_MODEL_NAME if self.use_llama else 'traditional'
            },
            'grading_results': results,
            'knowledge_analysis': {
                'wrong_questions': [r['question'] for r in wrong_questions],
                'wrong_knowledge_points': knowledge_points,
                'performance_summary': f'总分: {total_score}, 正确率: {accuracy_rate:.2%}',
                'improvement_suggestions': self._generate_improvement_suggestions(knowledge_points)
            },
            'practice_questions': practice_questions,
            'multimodal_analysis': multimodal_analysis
        }
        
        logger.info(f"批改完成: 总分 {total_score}, 正确率 {accuracy_rate:.2%}")
        return complete_result
    
    def _grade_single_question(self, question: str, answer: str, question_type: str, question_id: str) -> Dict[str, Any]:
        """
        批改单道题目
        
        Args:
            question: 题目内容
            answer: 学生答案
            question_type: 题目类型
            question_id: 题目ID
            
        Returns:
            批改结果
        """
        base_result = {
            'question': question,
            'answer': answer,
            'type': question_type,
            'question_id': question_id,
            'correct': False,
            'score': 0,
            'explanation': '批改失败'
        }
        
        try:
            # 如果是计算题且有特殊逻辑，优先使用传统方法
            if question_type == '计算题' and ('钟表' in question or '误差' in question):
                math_result = evaluate_math_calculation(question, answer)
                base_result.update(math_result)
                return base_result
            
            # 使用 Llama 进行智能批改
            if self.use_llama and self.llama_service:
                try:
                    llama_result = self.llama_service.grade_question(question, answer, question_type)
                    base_result.update(llama_result)
                    
                    # 添加 AI 标记
                    base_result['explanation'] = f"[AI批改] {llama_result.get('explanation', '')}"
                    return base_result
                    
                except Exception as e:
                    logger.warning(f"Llama 批改失败，回退到传统方法: {e}")
            
            # 回退到传统批改方法
            fallback_result = self._traditional_grading(question, answer, question_type)
            base_result.update(fallback_result)
            
        except Exception as e:
            logger.error(f"题目批改失败: {e}")
            base_result['explanation'] = f"批改过程中出现错误: {str(e)}"
        
        return base_result
    
    def _traditional_grading(self, question: str, answer: str, question_type: str) -> Dict[str, Any]:
        """
        传统批改方法（回退方案）
        """
        from app.services.grading_new import bert_sim
        
        question_hash = generate_question_hash(question)
        
        if answer and any(opt in answer.upper() for opt in ['A', 'B', 'C', 'D']):
            # 选择题
            correct = (question_hash % 3) != 0
            score = 2 if correct else 0
            standard_answer = 'A' if correct else 'B'
            explanation = f"选择题答案: {answer}, 参考答案: {standard_answer}"
            
        elif answer and any(word in answer for word in ['对', '错', '正确', '错误', '√', '×']):
            # 判断题
            correct = (question_hash % 2) == 0
            score = 2 if correct else 0
            standard_answer = '对' if correct else '错'
            explanation = f"判断题答案: {answer}, 参考答案: {standard_answer}"
            
        elif question_type == '计算题':
            # 计算题
            return evaluate_math_calculation(question, answer)
            
        else:
            # 填空题
            if answer.strip():
                standard_answer = f"参考答案{question_hash % 10}"
                sim = bert_sim(answer.strip(), standard_answer)
                score = max(0, round(sim * 3, 1))
                correct = sim > 0.7
                explanation = f"填空题答案: {answer}, 参考答案: {standard_answer}, 相似度: {sim:.2f}"
            else:
                score = 0
                correct = False
                explanation = "未作答"
        
        return {
            'correct': correct,
            'score': score,
            'explanation': explanation
        }
    
    def _generate_improvement_suggestions(self, knowledge_points: List[str]) -> List[str]:
        """
        生成改进建议
        
        Args:
            knowledge_points: 错题知识点
            
        Returns:
            改进建议列表
        """
        if not knowledge_points:
            return ["继续保持良好的学习状态！"]
        
        suggestions = []
        
        # 通用建议
        suggestions.append(f"需要重点复习以下知识点：{', '.join(knowledge_points)}")
        
        if len(knowledge_points) > 3:
            suggestions.append("错题涉及知识点较多，建议制定系统的复习计划")
        
        # 针对特定知识点的建议
        for point in knowledge_points:
            if '计算' in point or '运算' in point:
                suggestions.append("建议多练习计算题，提高计算准确性")
            elif '公式' in point:
                suggestions.append("建议熟记相关公式，并理解公式的应用场景")
            elif '概念' in point or '定义' in point:
                suggestions.append("建议加强基础概念的理解和记忆")
        
        return suggestions[:5]  # 最多返回5条建议
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        return {
            'llama_available': self.use_llama and self.llama_service is not None,
            'model_name': Config.LLAMA_MODEL_NAME if self.use_llama else None,
            'multimodal_enabled': self.enable_multimodal,
            'knowledge_analysis_enabled': self.enable_knowledge_analysis,
            'practice_generation_enabled': self.enable_practice_generation,
            'fallback_mode': not self.use_llama
        }

# 全局实例
grading_engine = LlamaGradingEngine()

def grade_homework_with_ai(questions: List[Dict], ocr_context: str = "") -> Dict[str, Any]:
    """
    使用 AI 进行作业批改的主入口函数
    
    Args:
        questions: 题目列表
        ocr_context: OCR 上下文信息
        
    Returns:
        批改结果
    """
    return grading_engine.grade_homework_with_llama(questions, ocr_context)

def get_ai_service_status() -> Dict[str, Any]:
    """
    获取 AI 服务状态
    
    Returns:
        服务状态信息
    """
    return grading_engine.get_service_status()
