"""
AI作业批改系统 - 大规模题目数据库模型
Day 9: 构建大规模题目答案数据库 - 目标1000+题目标准库

主要功能：
1. 标准化题目数据模型
2. 题目难度评估体系
3. 答案多样性支持
4. 题目质量控制
5. 批量题目导入和管理
6. 快速查询和检索优化
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, Index, SmallInteger, JSON, Enum, 
    UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMTEXT, LONGTEXT
from app.models.knowledge_base import Base, BaseModel, HierarchyMixin
import enum
import json
import hashlib
import re


class QuestionType(enum.Enum):
    """题目类型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"     # 选择题
    SINGLE_CHOICE = "single_choice"         # 单选题
    TRUE_FALSE = "true_false"               # 判断题
    FILL_BLANK = "fill_blank"               # 填空题
    SHORT_ANSWER = "short_answer"           # 简答题
    ESSAY = "essay"                         # 论述题
    CALCULATION = "calculation"             # 计算题
    PROOF = "proof"                         # 证明题
    ANALYSIS = "analysis"                   # 分析题
    SYNTHESIS = "synthesis"                 # 综合题


class DifficultyLevel(enum.Enum):
    """难度等级枚举"""
    VERY_EASY = 1      # 非常简单
    EASY = 2           # 简单
    MEDIUM = 3         # 中等
    HARD = 4           # 困难
    VERY_HARD = 5      # 非常困难


class QuestionSource(enum.Enum):
    """题目来源枚举"""
    TEXTBOOK = "textbook"               # 教材
    EXAM_PAPER = "exam_paper"           # 真题
    SIMULATION = "simulation"           # 模拟题
    PRACTICE = "practice"               # 练习题
    COMPETITION = "competition"         # 竞赛题
    GENERATED = "generated"             # AI生成
    CROWDSOURCE = "crowdsource"         # 众包
    MANUAL = "manual"                   # 人工录入


class AnswerFormat(enum.Enum):
    """答案格式枚举"""
    SINGLE_VALUE = "single_value"       # 单一值
    MULTIPLE_VALUES = "multiple_values" # 多个值
    RANGE = "range"                     # 范围
    EXPRESSION = "expression"           # 表达式
    TEXT = "text"                       # 文本
    JSON = "json"                       # JSON格式


class QuestionStatus(enum.Enum):
    """题目状态枚举"""
    DRAFT = "draft"                     # 草稿
    PENDING_REVIEW = "pending_review"   # 待审核
    APPROVED = "approved"               # 已审核
    REJECTED = "rejected"               # 已拒绝
    ARCHIVED = "archived"               # 已归档
    PUBLISHED = "published"             # 已发布


# ========================================
# 核心题目模型
# ========================================

class StandardQuestion(Base, BaseModel):
    """标准题目模型 - 支持1000+题目的大规模数据库"""
    
    __tablename__ = 'standard_questions'
    __table_args__ = {'extend_existing': True}
    
    # 基础信息
    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增主键')
    question_id = Column(String(100), unique=True, nullable=False, comment='业务主键')
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='学科ID')
    grade_level = Column(String(20), nullable=False, comment='年级')
    
    # 题目内容
    title = Column(String(200), comment='题目标题')
    stem = Column(LONGTEXT, nullable=False, comment='题目主干')
    question_type = Column(Enum(QuestionType), nullable=False, comment='题目类型')
    
    # 答案相关
    correct_answer = Column(LONGTEXT, nullable=False, comment='标准答案')
    answer_format = Column(Enum(AnswerFormat), default=AnswerFormat.SINGLE_VALUE, comment='答案格式')
    alternative_answers = Column(JSON, comment='可接受的替代答案')
    
    # 解析和提示
    explanation = Column(LONGTEXT, comment='详细解析')
    hint = Column(Text, comment='提示信息')
    solution_steps = Column(JSON, comment='解题步骤')
    
    # 难度和质量
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM, comment='难度等级')
    quality_score = Column(Float, default=0.0, comment='质量评分(0.0-10.0)')
    complexity_score = Column(Float, default=0.0, comment='复杂度评分(0.0-10.0)')
    
    # 统计信息
    usage_count = Column(Integer, default=0, comment='使用次数')
    correct_rate = Column(Float, default=0.0, comment='正确率(0.0-1.0)')
    average_time = Column(Float, default=0.0, comment='平均完成时间(秒)')
    
    # 来源和状态
    source = Column(Enum(QuestionSource), default=QuestionSource.MANUAL, comment='题目来源')
    source_reference = Column(String(500), comment='来源引用')
    status = Column(Enum(QuestionStatus), default=QuestionStatus.DRAFT, comment='题目状态')
    
    # 扩展信息
    extra_metadata = Column(JSON, comment='扩展元数据')
    tags = Column(JSON, comment='标签列表')
    keywords = Column(JSON, comment='关键词列表')
    
    # 审核信息
    created_by = Column(String(100), comment='创建者')
    reviewed_by = Column(String(100), comment='审核者')
    reviewed_at = Column(DateTime, comment='审核时间')
    
    # 版本控制
    version = Column(SmallInteger, default=1, comment='版本号')
    parent_question_id = Column(String(100), comment='父题目ID(用于变体)')
    
    # 关联关系
    subject = relationship("Subject", back_populates="standard_questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    knowledge_points = relationship("KnowledgePoint", 
                                  secondary="question_knowledge_association",
                                  back_populates="questions")
    
    # 索引优化
    __table_args__ = (
        Index('idx_sq_subject_grade', 'subject_id', 'grade_level'),
        Index('idx_sq_type_difficulty', 'question_type', 'difficulty_level'),
        Index('idx_sq_quality_score', 'quality_score'),
        Index('idx_sq_status', 'status'),
        Index('idx_sq_source', 'source'),
        Index('idx_sq_usage', 'usage_count'),
        Index('idx_sq_correct_rate', 'correct_rate'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 10.0', name='ck_quality_score'),
        CheckConstraint('correct_rate >= 0.0 AND correct_rate <= 1.0', name='ck_correct_rate'),
        CheckConstraint('complexity_score >= 0.0 AND complexity_score <= 10.0', name='ck_complexity_score'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.question_id:
            self.question_id = self.generate_question_id()
    
    def generate_question_id(self) -> str:
        """生成唯一的题目ID"""
        content_hash = hashlib.md5(f"{self.stem}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
        return f"Q_{self.question_type.value}_{content_hash}"
    
    def add_alternative_answer(self, answer: str, confidence: float = 1.0):
        """添加可接受的替代答案"""
        if not self.alternative_answers:
            self.alternative_answers = []
        
        self.alternative_answers.append({
            "answer": answer,
            "confidence": confidence,
            "added_at": datetime.utcnow().isoformat()
        })
    
    def calculate_difficulty_score(self) -> float:
        """基于统计数据计算难度分数"""
        if self.usage_count < 10:
            return float(self.difficulty_level.value)
        
        # 基于正确率计算实际难度
        if self.correct_rate >= 0.9:
            return 1.0  # 很简单
        elif self.correct_rate >= 0.7:
            return 2.0  # 简单
        elif self.correct_rate >= 0.5:
            return 3.0  # 中等
        elif self.correct_rate >= 0.3:
            return 4.0  # 困难
        else:
            return 5.0  # 很困难
    
    def update_statistics(self, is_correct: bool, time_spent: float):
        """更新题目统计信息"""
        self.usage_count += 1
        
        # 更新正确率
        if self.usage_count == 1:
            self.correct_rate = 1.0 if is_correct else 0.0
        else:
            total_correct = int(self.correct_rate * (self.usage_count - 1))
            if is_correct:
                total_correct += 1
            self.correct_rate = total_correct / self.usage_count
        
        # 更新平均时间
        if self.usage_count == 1:
            self.average_time = time_spent
        else:
            self.average_time = ((self.average_time * (self.usage_count - 1)) + time_spent) / self.usage_count
    
    def to_dict(self, include_statistics: bool = False) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        
        # 转换枚举值
        result['question_type'] = self.question_type.value
        result['difficulty_level'] = self.difficulty_level.value
        result['answer_format'] = self.answer_format.value
        result['source'] = self.source.value
        result['status'] = self.status.value
        
        # 添加关联数据
        if hasattr(self, 'options') and self.options:
            result['options'] = [opt.to_dict() for opt in self.options]
        
        if not include_statistics:
            # 移除统计信息
            for field in ['usage_count', 'correct_rate', 'average_time']:
                result.pop(field, None)
        
        return result


class QuestionOption(Base, BaseModel):
    """题目选项模型"""
    
    __tablename__ = 'question_options_extended'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(100), ForeignKey('standard_questions.question_id', ondelete='CASCADE'), 
                        nullable=False, comment='题目ID')
    option_key = Column(String(10), nullable=False, comment='选项键(A,B,C,D等)')
    option_value = Column(Text, nullable=False, comment='选项内容')
    is_correct = Column(Boolean, default=False, comment='是否为正确答案')
    explanation = Column(Text, comment='选项解析')
    
    # 关联关系
    question = relationship("StandardQuestion", back_populates="options")
    
    # 约束
    __table_args__ = (
        UniqueConstraint('question_id', 'option_key', name='uk_question_option_key'),
        Index('idx_qo_question', 'question_id'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'option_key': self.option_key,
            'option_value': self.option_value,
            'is_correct': self.is_correct,
            'explanation': self.explanation
        }


class QuestionBank(Base, BaseModel):
    """题库模型 - 组织和管理题目集合"""
    
    __tablename__ = 'question_banks'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment='题库名称')
    description = Column(Text, comment='题库描述')
    category = Column(String(100), comment='题库分类')
    
    # 统计信息
    total_questions = Column(Integer, default=0, comment='题目总数')
    difficulty_distribution = Column(JSON, comment='难度分布统计')
    type_distribution = Column(JSON, comment='题型分布统计')
    quality_average = Column(Float, default=0.0, comment='平均质量分')
    
    # 配置信息
    is_public = Column(Boolean, default=True, comment='是否公开')
    is_active = Column(Boolean, default=True, comment='是否启用')
    access_level = Column(String(50), default='public', comment='访问级别')
    
    # 创建者信息
    created_by = Column(String(100), comment='创建者')
    
    # 索引
    __table_args__ = (
        Index('idx_qb_category', 'category'),
        Index('idx_qb_public', 'is_public'),
        Index('idx_qb_active', 'is_active'),
    )


# ========================================
# 题目导入和批量处理工具
# ========================================

class QuestionBankManager:
    """题库管理器 - 提供题目的批量操作功能"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def import_questions_from_csv(self, file_path: str, subject_id: int) -> Dict[str, Any]:
        """从CSV文件导入题目"""
        import pandas as pd
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            results = {
                'total': len(df),
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for index, row in df.iterrows():
                try:
                    question = self._create_question_from_row(row, subject_id)
                    self.session.add(question)
                    results['success'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Row {index}: {str(e)}")
            
            self.session.commit()
            return results
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"导入失败: {str(e)}")
    
    def _create_question_from_row(self, row: Any, subject_id: int) -> StandardQuestion:
        """从数据行创建题目对象"""
        question = StandardQuestion(
            subject_id=subject_id,
            grade_level=row.get('grade', 'Grade 7'),
            stem=row['stem'],
            question_type=QuestionType(row.get('question_type', 'fill_blank')),
            correct_answer=row.get('correct_answer', ''),
            difficulty_level=DifficultyLevel(int(row.get('difficulty_level', 3))),
            explanation=row.get('explanation', ''),
            source=QuestionSource(row.get('source_type', 'manual'))
        )
        
        # 处理选项（如果是选择题）
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_CHOICE]:
            options_data = row.get('options', '')
            if options_data:
                self._add_options_to_question(question, options_data)
        
        return question
    
    def _add_options_to_question(self, question: StandardQuestion, options_data: str):
        """为题目添加选项"""
        try:
            if isinstance(options_data, str):
                # 假设格式为 "A:选项1|B:选项2|C:选项3|D:选项4"
                options = options_data.split('|')
                for option in options:
                    if ':' in option:
                        key, value = option.split(':', 1)
                        is_correct = key.strip() == question.correct_answer.strip()
                        
                        option_obj = QuestionOption(
                            question_id=question.question_id,
                            option_key=key.strip(),
                            option_value=value.strip(),
                            is_correct=is_correct
                        )
                        question.options.append(option_obj)
        except Exception as e:
            print(f"添加选项失败: {e}")
    
    def batch_update_difficulty(self, questions: List[StandardQuestion]) -> int:
        """批量更新题目难度"""
        updated_count = 0
        
        for question in questions:
            if question.usage_count >= 10:
                old_difficulty = question.difficulty_level
                new_difficulty_score = question.calculate_difficulty_score()
                new_difficulty = DifficultyLevel(int(new_difficulty_score))
                
                if new_difficulty != old_difficulty:
                    question.difficulty_level = new_difficulty
                    updated_count += 1
        
        self.session.commit()
        return updated_count
    
    def get_questions_by_criteria(self, 
                                subject_id: Optional[int] = None,
                                grade_level: Optional[str] = None,
                                question_type: Optional[QuestionType] = None,
                                difficulty_level: Optional[DifficultyLevel] = None,
                                min_quality_score: float = 0.0,
                                limit: int = 100) -> List[StandardQuestion]:
        """根据条件查询题目"""
        query = self.session.query(StandardQuestion)
        
        if subject_id:
            query = query.filter(StandardQuestion.subject_id == subject_id)
        if grade_level:
            query = query.filter(StandardQuestion.grade_level == grade_level)
        if question_type:
            query = query.filter(StandardQuestion.question_type == question_type)
        if difficulty_level:
            query = query.filter(StandardQuestion.difficulty_level == difficulty_level)
        if min_quality_score > 0:
            query = query.filter(StandardQuestion.quality_score >= min_quality_score)
        
        query = query.filter(StandardQuestion.status == QuestionStatus.PUBLISHED)
        query = query.order_by(StandardQuestion.quality_score.desc())
        query = query.limit(limit)
        
        return query.all()
    
    def generate_question_statistics(self) -> Dict[str, Any]:
        """生成题库统计信息"""
        total_questions = self.session.query(StandardQuestion).count()
        
        # 按难度分布
        difficulty_dist = {}
        for level in DifficultyLevel:
            count = self.session.query(StandardQuestion).filter(
                StandardQuestion.difficulty_level == level
            ).count()
            difficulty_dist[level.name] = count
        
        # 按题型分布
        type_dist = {}
        for qtype in QuestionType:
            count = self.session.query(StandardQuestion).filter(
                StandardQuestion.question_type == qtype
            ).count()
            type_dist[qtype.name] = count
        
        # 平均质量分
        avg_quality = self.session.query(func.avg(StandardQuestion.quality_score)).scalar() or 0.0
        
        return {
            'total_questions': total_questions,
            'difficulty_distribution': difficulty_dist,
            'type_distribution': type_dist,
            'average_quality_score': round(avg_quality, 2),
            'generated_at': datetime.utcnow().isoformat()
        }


# ========================================
# 辅助函数
# ========================================

def validate_question_data(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """验证题目数据的完整性和正确性"""
    errors = []
    warnings = []
    
    # 必需字段检查
    required_fields = ['stem', 'correct_answer', 'question_type']
    for field in required_fields:
        if not question_data.get(field):
            errors.append(f"缺少必需字段: {field}")
    
    # 题目内容长度检查
    if question_data.get('stem') and len(question_data['stem']) < 10:
        warnings.append("题目内容过短，可能影响质量")
    
    # 答案格式检查
    if question_data.get('correct_answer'):
        answer = question_data['correct_answer']
        if len(answer) > 1000:
            warnings.append("答案内容过长，可能影响用户体验")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def calculate_question_similarity(q1: StandardQuestion, q2: StandardQuestion) -> float:
    """计算两个题目的相似度"""
    from difflib import SequenceMatcher
    
    # 题干相似度
    stem_similarity = SequenceMatcher(None, q1.stem, q2.stem).ratio()
    
    # 答案相似度
    answer_similarity = SequenceMatcher(None, q1.correct_answer, q2.correct_answer).ratio()
    
    # 加权平均
    similarity = (stem_similarity * 0.7) + (answer_similarity * 0.3)
    
    # 如果题目类型不同，降低相似度
    if q1.question_type != q2.question_type:
        similarity *= 0.8
    
    return round(similarity, 3)


# ========================================
# 数据库表关联更新（为现有模型添加关系）
# ========================================

# 注意：需要在knowledge_base.py中的相关模型里添加反向关系
# 例如在Subject模型中添加：
# standard_questions = relationship("StandardQuestion", back_populates="subject")
