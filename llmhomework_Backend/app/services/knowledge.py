import jieba
from collections import Counter
from typing import List, Dict, Any
import logging
from app.config import Config

logger = logging.getLogger(__name__)

def summarize_wrong_questions(results):
    """简化的错题知识点提取（传统方法）"""
    wrong_questions = [r['question'] for r in results if not r.get('correct', True)]
    
    if not wrong_questions:
        return []
    
    # 简单的关键词提取
    all_words = []
    for question in wrong_questions:
        words = jieba.cut(question)
        # 过滤掉单字和常见停用词
        meaningful_words = [w for w in words if len(w) > 1 and w not in ['的', '是', '在', '了', '和', '与']]
        all_words.extend(meaningful_words)
    
    # 统计词频，返回前5个最常见的词作为知识点
    counter = Counter(all_words)
    top_words = [word for word, count in counter.most_common(5)]
    
    return top_words

def analyze_knowledge_points_ai(wrong_questions: List[Dict], llama_service=None) -> List[str]:
    """
    使用 AI 进行知识点分析
    
    Args:
        wrong_questions: 错题列表
        llama_service: Llama 服务实例
        
    Returns:
        知识点列表
    """
    if not wrong_questions:
        return []
    
    # 如果有 Llama 服务，使用 AI 分析
    if llama_service and Config.ENABLE_KNOWLEDGE_ANALYSIS:
        try:
            knowledge_points = llama_service.analyze_knowledge_points(wrong_questions)
            if knowledge_points:
                logger.info(f"AI 知识点分析成功，识别出 {len(knowledge_points)} 个知识点")
                return knowledge_points
        except Exception as e:
            logger.error(f"AI 知识点分析失败: {e}")
    
    # 回退到传统方法
    logger.info("使用传统方法进行知识点分析")
    return summarize_wrong_questions([{'question': q.get('question', ''), 'correct': False} for q in wrong_questions])

def generate_knowledge_summary(knowledge_points: List[str], grading_results: List[Dict]) -> Dict[str, Any]:
    """
    生成知识点总结报告
    
    Args:
        knowledge_points: 知识点列表
        grading_results: 批改结果
        
    Returns:
        知识点总结报告
    """
    wrong_results = [r for r in grading_results if not r.get('correct', True)]
    
    summary = {
        'total_knowledge_points': len(knowledge_points),
        'knowledge_points': knowledge_points,
        'wrong_question_count': len(wrong_results),
        'knowledge_distribution': _analyze_knowledge_distribution(knowledge_points, wrong_results),
        'difficulty_analysis': _analyze_difficulty(wrong_results),
        'study_recommendations': _generate_study_recommendations(knowledge_points, wrong_results)
    }
    
    return summary

def _analyze_knowledge_distribution(knowledge_points: List[str], wrong_results: List[Dict]) -> Dict[str, int]:
    """分析知识点分布"""
    distribution = {}
    
    for point in knowledge_points:
        count = 0
        for result in wrong_results:
            question = result.get('question', '').lower()
            if any(keyword in question for keyword in point.lower().split()):
                count += 1
        distribution[point] = count
    
    return distribution

def _analyze_difficulty(wrong_results: List[Dict]) -> Dict[str, Any]:
    """分析题目难度"""
    type_distribution = Counter(r.get('type', '未知') for r in wrong_results)
    avg_score = sum(r.get('score', 0) for r in wrong_results) / len(wrong_results) if wrong_results else 0
    
    difficulty_level = "简单"
    if avg_score < 1:
        difficulty_level = "困难"
    elif avg_score < 2:
        difficulty_level = "中等"
    
    return {
        'difficulty_level': difficulty_level,
        'average_score': round(avg_score, 2),
        'type_distribution': dict(type_distribution),
        'most_difficult_type': type_distribution.most_common(1)[0][0] if type_distribution else None
    }

def _generate_study_recommendations(knowledge_points: List[str], wrong_results: List[Dict]) -> List[str]:
    """生成学习建议"""
    recommendations = []
    
    if not knowledge_points:
        recommendations.append("恭喜！没有发现明显的知识薄弱点，继续保持！")
        return recommendations
    
    # 基于知识点的建议
    for point in knowledge_points:
        if '计算' in point or '运算' in point:
            recommendations.append(f"加强 {point} 的练习，注意计算步骤和准确性")
        elif '公式' in point or '定理' in point:
            recommendations.append(f"重点复习 {point}，理解公式含义和应用条件")
        elif '概念' in point or '定义' in point:
            recommendations.append(f"巩固 {point} 的基础概念，可以通过例题加深理解")
        else:
            recommendations.append(f"针对 {point} 进行专项练习")
    
    # 基于错题类型的建议
    type_counts = Counter(r.get('type', '未知') for r in wrong_results)
    for question_type, count in type_counts.most_common(2):
        if question_type == '计算题':
            recommendations.append("建议多做计算题练习，提高计算速度和准确性")
        elif question_type == '选择题':
            recommendations.append("注意选择题的解题技巧，仔细分析每个选项")
        elif question_type == '填空题':
            recommendations.append("填空题要注意答案的完整性和准确性")
        elif question_type == '判断题':
            recommendations.append("判断题要理解概念的准确含义，避免模糊记忆")
    
    return recommendations[:5]  # 最多返回5条建议

class KnowledgeAnalyzer:
    """知识点分析器"""
    
    def __init__(self, llama_service=None):
        """
        初始化知识点分析器
        
        Args:
            llama_service: Llama 服务实例
        """
        self.llama_service = llama_service
        self.enable_ai = Config.ENABLE_KNOWLEDGE_ANALYSIS
    
    def analyze(self, grading_results: List[Dict]) -> Dict[str, Any]:
        """
        综合分析批改结果
        
        Args:
            grading_results: 批改结果列表
            
        Returns:
            分析报告
        """
        wrong_questions = [r for r in grading_results if not r.get('correct', True)]
        
        # 知识点分析
        knowledge_points = analyze_knowledge_points_ai(wrong_questions, self.llama_service)
        
        # 生成详细报告
        knowledge_summary = generate_knowledge_summary(knowledge_points, grading_results)
        
        # 学习建议
        study_plan = self._generate_study_plan(knowledge_points, wrong_questions)
        
        return {
            'knowledge_analysis': knowledge_summary,
            'study_plan': study_plan,
            'analysis_method': 'AI' if self.enable_ai and self.llama_service else 'Traditional'
        }
    
    def _generate_study_plan(self, knowledge_points: List[str], wrong_questions: List[Dict]) -> Dict[str, Any]:
        """生成学习计划"""
        if not knowledge_points:
            return {
                'priority': 'low',
                'study_time_estimate': '无需额外学习时间',
                'study_sequence': [],
                'practice_suggestions': ["继续保持良好状态"]
            }
        
        # 根据错题数量确定优先级
        priority = 'high' if len(wrong_questions) > 3 else 'medium' if len(wrong_questions) > 1 else 'low'
        
        # 估算学习时间
        study_time_estimate = f"{len(knowledge_points) * 30} 分钟"
        
        # 学习顺序建议
        study_sequence = []
        for i, point in enumerate(knowledge_points[:3], 1):  # 最多3个重点
            study_sequence.append(f"{i}. 复习 {point} - 建议用时 30 分钟")
        
        return {
            'priority': priority,
            'study_time_estimate': study_time_estimate,
            'study_sequence': study_sequence,
            'practice_suggestions': _generate_study_recommendations(knowledge_points, wrong_questions)
        }