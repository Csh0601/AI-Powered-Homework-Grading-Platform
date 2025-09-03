"""
AI作业批改系统 - 知识服务优化版本
使用新的数据库模型，支持AI知识点分析、学习推荐等功能
"""

import jieba
from collections import Counter
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.knowledge_base import (
    Base, Grade, Subject, Chapter, KnowledgePoint, Question, 
    QuestionOption, Tag, KnowledgePointKeyword, GradingResult, 
    TaskRecord, LearningRecord, UserProfile, QuestionType, 
    ProcessingStatus, RelationshipType, LearningStyle, ExamType
)
from app.config import Config

logger = logging.getLogger(__name__)

class KnowledgeService:
    """知识服务类"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_knowledge_hierarchy(self, grade_id: Optional[int] = None, 
                               subject_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取知识点层级结构
        
        Args:
            grade_id: 年级ID（可选）
            subject_id: 学科ID（可选）
            
        Returns:
            知识点层级结构
        """
        try:
            query = self.db.query(Grade, Subject, Chapter, KnowledgePoint)
            
            if grade_id:
                query = query.filter(Grade.id == grade_id)
            if subject_id:
                query = query.filter(Subject.id == subject_id)
            
            results = query.filter(
                Grade.is_active == True,
                Subject.is_active == True,
                Chapter.is_active == True,
                KnowledgePoint.is_active == True
            ).all()
            
            hierarchy = self._build_hierarchy(results)
            return {
                'success': True,
                'data': hierarchy,
                'total_count': len(results)
            }
            
        except Exception as e:
            logger.error(f"获取知识点层级失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_knowledge_points(self, keyword: str, subject_id: Optional[int] = None,
                               difficulty_level: Optional[int] = None) -> Dict[str, Any]:
        """
        搜索知识点
        
        Args:
            keyword: 搜索关键词
            subject_id: 学科ID（可选）
            difficulty_level: 难度等级（可选）
            
        Returns:
            搜索结果
        """
        try:
            query = self.db.query(KnowledgePoint).join(Chapter).join(Subject)
            
            # 关键词搜索
            if keyword:
                query = query.filter(
                    (KnowledgePoint.name.contains(keyword)) |
                    (KnowledgePoint.description.contains(keyword)) |
                    (KnowledgePoint.code.contains(keyword))
                )
            
            # 学科过滤
            if subject_id:
                query = query.filter(Subject.id == subject_id)
            
            # 难度过滤
            if difficulty_level:
                query = query.filter(KnowledgePoint.difficulty_level == difficulty_level)
            
            # 只返回活跃的知识点
            query = query.filter(KnowledgePoint.is_active == True)
            
            results = query.all()
            
            return {
                'success': True,
                'data': [self._knowledge_point_to_dict(kp) for kp in results],
                'total_count': len(results)
            }
            
        except Exception as e:
            logger.error(f"搜索知识点失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_questions_by_knowledge_point(self, knowledge_point_id: int, 
                                       difficulty_level: Optional[int] = None,
                                       limit: int = 10) -> Dict[str, Any]:
        """
        根据知识点获取相关题目
        
        Args:
            knowledge_point_id: 知识点ID
            difficulty_level: 难度等级（可选）
            limit: 返回数量限制
            
        Returns:
            题目列表
        """
        try:
            query = self.db.query(Question).join(
                Question.knowledge_points
            ).filter(
                Question.knowledge_points.any(id=knowledge_point_id),
                Question.is_active == True
            )
            
            if difficulty_level:
                query = query.filter(Question.difficulty_level == difficulty_level)
            
            questions = query.limit(limit).all()
            
            return {
                'success': True,
                'data': [self._question_to_dict(q) for q in questions],
                'total_count': len(questions)
            }
            
        except Exception as e:
            logger.error(f"获取知识点相关题目失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_wrong_questions_ai(self, wrong_questions: List[Dict], 
                                  llama_service=None) -> List[str]:
        """
        使用AI分析错题知识点
        
        Args:
            wrong_questions: 错题列表
            llama_service: Llama服务实例
            
        Returns:
            知识点列表
        """
        if not wrong_questions:
            return []
        
        # 如果有Llama服务，使用AI分析
        if llama_service and Config.ENABLE_KNOWLEDGE_ANALYSIS:
            try:
                knowledge_points = llama_service.analyze_knowledge_points(wrong_questions)
                if knowledge_points:
                    logger.info(f"AI知识点分析成功，识别出{len(knowledge_points)}个知识点")
                    return knowledge_points
            except Exception as e:
                logger.error(f"AI知识点分析失败: {e}")
        
        # 回退到传统方法
        logger.info("使用传统方法进行知识点分析")
        return self._summarize_wrong_questions(wrong_questions)
    
    def get_similar_questions(self, question_id: str, similarity_threshold: float = 0.5,
                             limit: int = 5) -> Dict[str, Any]:
        """
        获取相似题目
        
        Args:
            question_id: 题目ID
            similarity_threshold: 相似度阈值
            limit: 返回数量限制
            
        Returns:
            相似题目列表
        """
        try:
            # 获取当前题目的知识点
            current_question = self.db.query(Question).filter(
                Question.question_id == question_id
            ).first()
            
            if not current_question:
                return {
                    'success': False,
                    'error': '题目不存在'
                }
            
            # 查找有共同知识点的题目
            similar_questions = self.db.query(Question).join(
                Question.knowledge_points
            ).filter(
                Question.question_id != question_id,
                Question.is_active == True,
                Question.subject_id == current_question.subject_id
            ).all()
            
            # 计算相似度并排序
            scored_questions = []
            for q in similar_questions:
                common_knowledge_points = set(q.knowledge_points) & set(current_question.knowledge_points)
                similarity_score = len(common_knowledge_points) / max(len(q.knowledge_points), len(current_question.knowledge_points))
                
                if similarity_score >= similarity_threshold:
                    scored_questions.append({
                        'question': self._question_to_dict(q),
                        'similarity_score': similarity_score
                    })
            
            # 按相似度排序
            scored_questions.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return {
                'success': True,
                'data': scored_questions[:limit],
                'total_count': len(scored_questions)
            }
            
        except Exception as e:
            logger.error(f"获取相似题目失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户学习画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户学习画像
        """
        try:
            # 获取用户画像
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                return {
                    'success': False,
                    'error': '用户画像不存在'
                }
            
            # 获取学习记录统计
            learning_stats = self.db.query(LearningRecord).filter(
                LearningRecord.user_id == user_id
            ).all()
            
            # 计算学习统计
            total_attempts = len(learning_stats)
            correct_attempts = len([r for r in learning_stats if r.is_correct])
            accuracy_rate = correct_attempts / total_attempts if total_attempts > 0 else 0
            
            # 计算平均答题时间
            avg_answer_time = sum(r.answer_time or 0 for r in learning_stats) / total_attempts if total_attempts > 0 else 0
            
            return {
                'success': True,
                'data': {
                    'profile': self._user_profile_to_dict(profile),
                    'learning_stats': {
                        'total_attempts': total_attempts,
                        'correct_attempts': correct_attempts,
                        'accuracy_rate': accuracy_rate,
                        'avg_answer_time': avg_answer_time
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户学习画像失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_learning_recommendations(self, user_id: str, subject_id: Optional[int] = None,
                                        limit: int = 10) -> Dict[str, Any]:
        """
        生成学习推荐
        
        Args:
            user_id: 用户ID
            subject_id: 学科ID（可选）
            limit: 推荐数量限制
            
        Returns:
            学习推荐列表
        """
        try:
            # 获取用户学习记录
            learning_records = self.db.query(LearningRecord).filter(
                LearningRecord.user_id == user_id
            )
            
            if subject_id:
                learning_records = learning_records.join(Question).filter(
                    Question.subject_id == subject_id
                )
            
            records = learning_records.all()
            
            # 分析薄弱知识点
            weak_knowledge_points = self._analyze_weak_knowledge_points(records)
            
            # 生成推荐题目
            recommended_questions = []
            for kp in weak_knowledge_points[:limit]:
                questions = self.get_questions_by_knowledge_point(
                    kp['knowledge_point_id'], 
                    difficulty_level=kp['recommended_difficulty'],
                    limit=2
                )
                
                if questions['success']:
                    recommended_questions.extend(questions['data'])
            
            return {
                'success': True,
                'data': {
                    'weak_knowledge_points': weak_knowledge_points[:limit],
                    'recommended_questions': recommended_questions[:limit]
                }
            }
            
        except Exception as e:
            logger.error(f"生成学习推荐失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_hierarchy(self, results: List) -> Dict[str, Any]:
        """构建层级结构"""
        hierarchy = {}
        
        for grade, subject, chapter, kp in results:
            if grade.id not in hierarchy:
                hierarchy[grade.id] = {
                    'id': grade.id,
                    'name': grade.name,
                    'code': grade.code,
                    'subjects': {}
                }
            
            if subject.id not in hierarchy[grade.id]['subjects']:
                hierarchy[grade.id]['subjects'][subject.id] = {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'chapters': {}
                }
            
            if chapter.id not in hierarchy[grade.id]['subjects'][subject.id]['chapters']:
                hierarchy[grade.id]['subjects'][subject.id]['chapters'][chapter.id] = {
                    'id': chapter.id,
                    'name': chapter.name,
                    'code': chapter.code,
                    'knowledge_points': []
                }
            
            hierarchy[grade.id]['subjects'][subject.id]['chapters'][chapter.id]['knowledge_points'].append({
                'id': kp.id,
                'name': kp.name,
                'code': kp.code,
                'difficulty_level': kp.difficulty_level,
                'importance_level': kp.importance_level
            })
        
        return hierarchy
    
    def _knowledge_point_to_dict(self, kp: KnowledgePoint) -> Dict[str, Any]:
        """知识点转字典"""
        return {
            'id': kp.id,
            'name': kp.name,
            'code': kp.code,
            'description': kp.description,
            'difficulty_level': kp.difficulty_level,
            'importance_level': kp.importance_level,
            'exam_frequency': kp.exam_frequency,
            'learning_objectives': kp.learning_objectives,
            'common_mistakes': kp.common_mistakes,
            'learning_tips': kp.learning_tips
        }
    
    def _question_to_dict(self, q: Question) -> Dict[str, Any]:
        """题目转字典"""
        return {
            'question_id': q.question_id,
            'number': q.number,
            'stem': q.stem,
            'type': q.type.value if q.type else None,
            'difficulty_level': q.difficulty_level,
            'source': q.source,
            'source_type': q.source_type,
            'options': [{'key': opt.option_key, 'value': opt.option_value, 'is_correct': opt.is_correct} 
                       for opt in q.options] if q.options else []
        }
    
    def _user_profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """用户画像转字典"""
        return {
            'user_id': profile.user_id,
            'math_level': profile.math_level,
            'chinese_level': profile.chinese_level,
            'english_level': profile.english_level,
            'preferred_difficulty': profile.preferred_difficulty,
            'learning_style': profile.learning_style.value if profile.learning_style else None
        }
    
    def _summarize_wrong_questions(self, wrong_questions: List[Dict]) -> List[str]:
        """简化的错题知识点提取（传统方法）"""
        all_words = []
        
        for question in wrong_questions:
            question_text = question.get('question', '')
            words = jieba.cut(question_text)
            # 过滤掉单字和常见停用词
            meaningful_words = [w for w in words if len(w) > 1 and w not in ['的', '是', '在', '了', '和', '与']]
            all_words.extend(meaningful_words)
        
        # 统计词频，返回前5个最常见的词作为知识点
        counter = Counter(all_words)
        top_words = [word for word, count in counter.most_common(5)]
        
        return top_words
    
    def _analyze_weak_knowledge_points(self, records: List[LearningRecord]) -> List[Dict[str, Any]]:
        """分析薄弱知识点"""
        kp_stats = {}
        
        for record in records:
            kp_id = record.knowledge_point_id
            if kp_id not in kp_stats:
                kp_stats[kp_id] = {
                    'knowledge_point_id': kp_id,
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'avg_answer_time': 0
                }
            
            kp_stats[kp_id]['total_attempts'] += 1
            if record.is_correct:
                kp_stats[kp_id]['correct_attempts'] += 1
            
            if record.answer_time:
                kp_stats[kp_id]['avg_answer_time'] += record.answer_time
        
        # 计算正确率和平均时间
        weak_points = []
        for kp_id, stats in kp_stats.items():
            accuracy = stats['correct_attempts'] / stats['total_attempts']
            avg_time = stats['avg_answer_time'] / stats['total_attempts']
            
            # 判断是否为薄弱知识点
            if accuracy < 0.6 or avg_time > 120:  # 正确率低于60%或平均用时超过2分钟
                weak_points.append({
                    'knowledge_point_id': kp_id,
                    'accuracy': accuracy,
                    'avg_answer_time': avg_time,
                    'recommended_difficulty': max(1, min(5, int(5 - accuracy * 5)))  # 根据正确率推荐难度
                })
        
        # 按薄弱程度排序
        weak_points.sort(key=lambda x: (x['accuracy'], -x['avg_answer_time']))
        
        return weak_points

# 导出服务类
__all__ = ['KnowledgeService']





