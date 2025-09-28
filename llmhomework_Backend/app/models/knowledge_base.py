"""
AI作业批改系统 - 知识库数据模型
完全优化版本，匹配新的数据库设计
支持AI作业批改、知识点分析、题目生成等核心功能

主要功能：
1. 层级化知识体系管理（年级→学科→章节→知识点）
2. 题目与知识点的多对多关联
3. 智能推荐和相似度匹配
4. 用户学习画像和记录跟踪
5. AI功能支持（批改、生成、分析）
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, Table, Index, SmallInteger, JSON, Enum, BigInteger,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base, Session
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.ext.declarative import declared_attr
import enum

Base = declarative_base()

# ========================================
# 基础模型类
# ========================================

class BaseModel:
    """基础模型类，提供通用字段和方法"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    
    @declared_attr  
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        exclude_fields = exclude_fields or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif isinstance(value, enum.Enum):
                    result[column.name] = value.value
                else:
                    result[column.name] = value
        return result

class HierarchyMixin:
    """层级结构混合类，为具有层级关系的模型提供通用方法"""
    
    def get_children_count(self, session: Session, child_relation_name: str) -> int:
        """获取子级项目数量"""
        if hasattr(self, child_relation_name):
            children = getattr(self, child_relation_name)
            if hasattr(children, 'count'):
                return children.count()
            elif hasattr(children, '__len__'):
                return len(children)
        return 0
    
    @classmethod
    def get_active_items(cls, session: Session, is_active_field: str = 'is_active'):
        """获取激活状态的项目"""
        if hasattr(cls, is_active_field):
            return session.query(cls).filter(getattr(cls, is_active_field) == True).all()
        return session.query(cls).all()
    
    def generate_standard_repr(self, key_fields: List[str] = None) -> str:
        """生成标准的字符串表示"""
        key_fields = key_fields or ['id', 'name']
        class_name = self.__class__.__name__
        field_strs = []
        
        for field in key_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if isinstance(value, str):
                    field_strs.append(f"{field}='{value}'")
                else:
                    field_strs.append(f"{field}={value}")
        
        return f"<{class_name}({', '.join(field_strs)})>"

# ========================================
# 枚举定义
# ========================================

class QuestionType(enum.Enum):
    """题目类型枚举"""
    CHOICE = "choice"           # 选择题
    TRUE_FALSE = "true_false"   # 判断题
    FILL_BLANK = "fill_blank"   # 填空题
    CALCULATION = "calculation" # 计算题
    APPLICATION = "application" # 应用题
    FORMULA = "formula"         # 公式题
    MENTAL = "mental"           # 口算题
    ESSAY = "essay"             # 作文题
    READING = "reading"         # 阅读理解
    UNKNOWN = "unknown"         # 未知题型
    
    @classmethod
    def get_choices(cls):
        """获取所有选择项"""
        return [(item.value, item.name) for item in cls]

class ProcessingStatus(enum.Enum):
    """处理状态枚举"""
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败

class RelationshipType(enum.Enum):
    """知识点关系类型枚举"""
    PREREQUISITE = "prerequisite"  # 前置知识
    RELATED = "related"             # 相关知识
    ADVANCED = "advanced"           # 进阶知识
    PARALLEL = "parallel"           # 平行知识

class LearningStyle(enum.Enum):
    """学习风格枚举"""
    VISUAL = "visual"           # 视觉型
    AUDITORY = "auditory"       # 听觉型
    KINESTHETIC = "kinesthetic" # 动觉型
    MIXED = "mixed"             # 混合型

class ExamType(enum.Enum):
    """考试类型枚举"""
    MIDTERM = "midterm"         # 期中
    FINAL = "final"             # 期末
    MOCK = "mock"               # 模拟
    QUIZ = "quiz"               # 小测
    HOMEWORK = "homework"       # 作业

# ========================================
# 关联表定义
# ========================================

# 题目知识点关联表
question_knowledge_association = Table(
    'question_knowledge_association',
    Base.metadata,
    Column('question_id', String(100), ForeignKey('questions.question_id', ondelete='CASCADE'), primary_key=True),
    Column('knowledge_point_id', Integer, ForeignKey('knowledge_points.id', ondelete='CASCADE'), primary_key=True),
    Column('relevance_score', Float, default=1.0, nullable=False, comment='关联度评分(0.0-1.0)'),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    
    # 索引优化
    Index('idx_qka_question', 'question_id'),
    Index('idx_qka_knowledge', 'knowledge_point_id'),
    Index('idx_qka_relevance', 'relevance_score'),
)

# 题目标签关联表
question_tags = Table(
    'question_tags',
    Base.metadata,
    Column('question_id', String(100), ForeignKey('questions.question_id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('relevance_score', Float, default=1.0, nullable=False, comment='关联度评分(0.0-1.0)'),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    
    # 索引优化
    Index('idx_qt_tag', 'tag_id'),
    Index('idx_qt_relevance', 'relevance_score'),
)

# 知识点关系表
knowledge_relationship = Table(
    'knowledge_relationship',
    Base.metadata,
    Column('prerequisite_id', Integer, ForeignKey('knowledge_points.id', ondelete='CASCADE'), primary_key=True),
    Column('dependent_id', Integer, ForeignKey('knowledge_points.id', ondelete='CASCADE'), primary_key=True),
    Column('relationship_type', Enum(RelationshipType), nullable=False, comment='关系类型'),
    Column('strength', Float, default=1.0, nullable=False, comment='关系强度(0.0-1.0)'),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    
    # 索引优化
    Index('idx_kr_prerequisite', 'prerequisite_id'),
    Index('idx_kr_dependent', 'dependent_id'),
    Index('idx_kr_type', 'relationship_type'),
    Index('idx_kr_strength', 'strength'),
)

# ========================================
# 基础层级结构表
# ========================================

class Grade(Base, BaseModel, HierarchyMixin):
    """年级表"""
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, comment='年级名称，如：初一、初二、初三')
    code = Column(String(10), unique=True, nullable=False, comment='年级代码，如：grade7、grade8、grade9')
    description = Column(Text, comment='年级描述')
    sort_order = Column(SmallInteger, default=0, nullable=False, comment='排序顺序')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 关系
    subjects = relationship("Subject", back_populates="grade", cascade="all, delete-orphan")
    
    # 索引优化
    __table_args__ = (
        Index('idx_grade_code', 'code'),
        Index('idx_grade_sort', 'sort_order'),
        Index('idx_grade_active', 'is_active'),
    )
    
    def __repr__(self):
        return self.generate_standard_repr(['id', 'name', 'code'])
    
    @classmethod
    def get_active_grades(cls, session: Session) -> List['Grade']:
        """获取所有活跃年级"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order).all()
    
    def get_subjects_count(self, session: Session) -> int:
        """获取该年级的学科数量"""
        return self.get_children_count(session, 'subjects')

class Subject(Base, BaseModel):
    """学科表"""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey('grades.id', ondelete='CASCADE'), nullable=False, comment='年级ID')
    name = Column(String(30), nullable=False, comment='学科名称，如：数学、语文、英语')
    code = Column(String(15), unique=True, nullable=False, comment='学科代码，如：math、chinese、english')
    description = Column(Text, comment='学科描述')
    difficulty_level = Column(TINYINT, default=1, nullable=False, comment='难度等级：1-5')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 关系
    grade = relationship("Grade", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")
    textbooks = relationship("Textbook", back_populates="subject", cascade="all, delete-orphan")
    exam_papers = relationship("ExamPaper", back_populates="subject", cascade="all, delete-orphan")
    # question_banks relationship moved to question_bank.py
    
    # 索引优化
    __table_args__ = (
        Index('idx_subject_grade', 'grade_id'),
        Index('idx_subject_code', 'code'),
        Index('idx_subject_difficulty', 'difficulty_level'),
        Index('idx_subject_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @classmethod
    def get_by_grade(cls, session: Session, grade_id: int) -> List['Subject']:
        """根据年级获取学科"""
        return session.query(cls).filter(cls.grade_id == grade_id, cls.is_active == True).all()
    
    def get_chapters_count(self, session: Session) -> int:
        """获取该学科的章节数量"""
        return session.query(Chapter).filter(Chapter.subject_id == self.id, Chapter.is_active == True).count()
    
    def get_questions_count(self, session: Session) -> int:
        """获取该学科的题目数量"""
        return session.query(Question).filter(Question.subject_id == self.id, Question.is_active == True).count()
    
    def get_difficulty_distribution(self, session: Session) -> Dict[int, int]:
        """获取该学科的难度分布"""
        from sqlalchemy import func
        result = session.query(
            Question.difficulty_level,
            func.count(Question.question_id)
        ).filter(
            Question.subject_id == self.id,
            Question.is_active == True
        ).group_by(Question.difficulty_level).all()
        
        return {level: count for level, count in result}

class Chapter(Base, BaseModel):
    """章节表"""
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='学科ID')
    name = Column(String(100), nullable=False, comment='章节名称')
    code = Column(String(30), nullable=False, comment='章节代码')
    description = Column(Text, comment='章节描述')
    chapter_number = Column(SmallInteger, comment='章节编号')
    difficulty_level = Column(TINYINT, default=1, nullable=False, comment='难度等级：1-5')
    estimated_hours = Column(Float, default=1.0, nullable=False, comment='预估学习时长（小时）')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 关系
    subject = relationship("Subject", back_populates="chapters")
    knowledge_points = relationship("KnowledgePoint", back_populates="chapter", cascade="all, delete-orphan")
    
    # 索引优化
    __table_args__ = (
        Index('idx_chapter_subject', 'subject_id'),
        Index('idx_chapter_code', 'code'),
        Index('idx_chapter_number', 'chapter_number'),
        Index('idx_chapter_difficulty', 'difficulty_level'),
        Index('idx_chapter_active', 'is_active'),
    )

class KnowledgePoint(Base, BaseModel):
    """知识点表"""
    __tablename__ = 'knowledge_points'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, comment='章节ID')
    name = Column(String(200), nullable=False, comment='知识点名称')
    code = Column(String(50), nullable=False, comment='知识点代码')
    description = Column(Text, comment='知识点详细描述')
    difficulty_level = Column(TINYINT, default=1, nullable=False, comment='难度等级：1-5')
    importance_level = Column(TINYINT, default=1, nullable=False, comment='重要程度：1-5')
    exam_frequency = Column(Float, default=0.0, nullable=False, comment='考试频率比例(0.0-1.0)')
    learning_objectives = Column(Text, comment='学习目标')
    common_mistakes = Column(Text, comment='常见错误')
    learning_tips = Column(Text, comment='学习技巧')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 关系
    chapter = relationship("Chapter", back_populates="knowledge_points")
    questions = relationship("Question", secondary=question_knowledge_association, back_populates="knowledge_points")
    keywords = relationship("KnowledgePointKeyword", back_populates="knowledge_point", cascade="all, delete-orphan")
    
    # 自引用关系
    prerequisites = relationship(
        "KnowledgePoint",
        secondary=knowledge_relationship,
        primaryjoin=id == knowledge_relationship.c.dependent_id,
        secondaryjoin=id == knowledge_relationship.c.prerequisite_id,
        backref="dependents"
    )
    
    # 索引优化
    __table_args__ = (
        Index('idx_kp_chapter', 'chapter_id'),
        Index('idx_kp_code', 'code'),
        Index('idx_kp_difficulty', 'difficulty_level'),
        Index('idx_kp_importance', 'importance_level'),
        Index('idx_kp_exam_freq', 'exam_frequency'),
        Index('idx_kp_active', 'is_active'),
        # 复合索引优化常用查询
        Index('idx_kp_chapter_difficulty', 'chapter_id', 'difficulty_level'),
        Index('idx_kp_chapter_importance', 'chapter_id', 'importance_level'),
    )
    
    def __repr__(self):
        return f"<KnowledgePoint(id={self.id}, name='{self.name}', difficulty={self.difficulty_level})>"
    
    @classmethod
    def get_by_difficulty(cls, session: Session, difficulty_level: int, limit: int = 20) -> List['KnowledgePoint']:
        """根据难度等级获取知识点"""
        return session.query(cls).filter(
            cls.difficulty_level == difficulty_level,
            cls.is_active == True
        ).order_by(cls.importance_level.desc()).limit(limit).all()
    
    @classmethod
    def get_high_frequency_knowledge_points(cls, session: Session, threshold: float = 0.5, limit: int = 10) -> List['KnowledgePoint']:
        """获取高频考试知识点"""
        return session.query(cls).filter(
            cls.exam_frequency >= threshold,
            cls.is_active == True
        ).order_by(cls.exam_frequency.desc(), cls.importance_level.desc()).limit(limit).all()
    
    def get_related_questions(self, session: Session, difficulty_filter: Optional[int] = None, limit: int = 10) -> List['Question']:
        """获取相关题目"""
        from sqlalchemy.orm import joinedload
        query = session.query(Question).join(
            question_knowledge_association
        ).filter(
            question_knowledge_association.c.knowledge_point_id == self.id,
            Question.is_active == True
        )
        
        if difficulty_filter:
            query = query.filter(Question.difficulty_level == difficulty_filter)
            
        return query.order_by(
            question_knowledge_association.c.relevance_score.desc()
        ).limit(limit).all()
    
    def get_prerequisite_knowledge_points(self, session: Session) -> List['KnowledgePoint']:
        """获取前置知识点"""
        return session.query(KnowledgePoint).join(
            knowledge_relationship,
            KnowledgePoint.id == knowledge_relationship.c.prerequisite_id
        ).filter(
            knowledge_relationship.c.dependent_id == self.id,
            knowledge_relationship.c.relationship_type == RelationshipType.PREREQUISITE
        ).all()
    
    def get_learning_statistics(self, session: Session, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取学习统计信息"""
        from sqlalchemy import func
        
        # 基础统计
        total_questions = session.query(func.count(Question.question_id)).join(
            question_knowledge_association
        ).filter(question_knowledge_association.c.knowledge_point_id == self.id).scalar()
        
        stats = {
            'knowledge_point_id': self.id,
            'knowledge_point_name': self.name,
            'difficulty_level': self.difficulty_level,
            'importance_level': self.importance_level,
            'exam_frequency': self.exam_frequency,
            'total_questions': total_questions or 0
        }
        
        # 如果提供用户ID，添加个人统计
        if user_id:
            user_stats = session.query(
                func.count(LearningRecord.id).label('attempts'),
                func.sum(LearningRecord.is_correct.cast(Integer)).label('correct_count'),
                func.avg(LearningRecord.answer_time).label('avg_time')
            ).filter(
                LearningRecord.user_id == user_id,
                LearningRecord.knowledge_point_id == self.id
            ).first()
            
            if user_stats and user_stats.attempts:
                stats.update({
                    'user_attempts': user_stats.attempts,
                    'user_correct_count': user_stats.correct_count or 0,
                    'user_accuracy': (user_stats.correct_count or 0) / user_stats.attempts,
                    'user_avg_time': float(user_stats.avg_time) if user_stats.avg_time else 0
                })
            else:
                stats.update({
                    'user_attempts': 0,
                    'user_correct_count': 0,
                    'user_accuracy': 0,
                    'user_avg_time': 0
                })
        
        return stats

# ========================================
# 题目相关表
# ========================================

class Question(Base, BaseModel):
    """题目表 - 使用业务主键"""
    __tablename__ = 'questions'
    
    question_id = Column(String(100), primary_key=True, comment='题目唯一业务ID')
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='学科ID')
    
    # JSON Schema核心字段
    number = Column(String(20), nullable=False, comment='题号')
    stem = Column(Text, nullable=False, comment='题目内容')
    answer = Column(Text, nullable=False, comment='学生答案')
    type = Column(Enum(QuestionType), nullable=False, comment='题目类型')
    timestamp = Column(BigInteger, nullable=False, comment='时间戳')
    
    # 扩展字段
    correct_answer = Column(Text, comment='正确答案')
    explanation = Column(Text, comment='解析')
    difficulty_level = Column(TINYINT, default=1, nullable=False, comment='难度等级：1-5')
    source = Column(String(100), comment='题目来源')
    source_type = Column(String(20), comment='来源类型：textbook、exam、exercise')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 关系
    subject = relationship("Subject", back_populates="questions")
    knowledge_points = relationship("KnowledgePoint", secondary=question_knowledge_association, back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions")
    learning_records = relationship("LearningRecord", back_populates="question", cascade="all, delete-orphan")
    
    # 索引优化
    __table_args__ = (
        Index('idx_question_subject', 'subject_id'),
        Index('idx_question_type', 'type'),
        Index('idx_question_difficulty', 'difficulty_level'),
        Index('idx_question_timestamp', 'timestamp'),
        Index('idx_question_active', 'is_active'),
        Index('idx_question_number', 'number'),
    )
    
    def __repr__(self):
        return f"<Question(id='{self.question_id}', type={self.type.value}, difficulty={self.difficulty_level})>"
    
    @classmethod
    def get_by_type_and_difficulty(cls, session: Session, question_type: QuestionType, 
                                   difficulty_level: int, limit: int = 10) -> List['Question']:
        """根据题型和难度获取题目"""
        return session.query(cls).filter(
            cls.type == question_type,
            cls.difficulty_level == difficulty_level,
            cls.is_active == True
        ).limit(limit).all()
    
    @classmethod
    def get_by_knowledge_points(cls, session: Session, knowledge_point_ids: List[int], 
                               limit: int = 10) -> List['Question']:
        """根据知识点获取题目"""
        return session.query(cls).join(
            question_knowledge_association
        ).filter(
            question_knowledge_association.c.knowledge_point_id.in_(knowledge_point_ids),
            cls.is_active == True
        ).order_by(
            question_knowledge_association.c.relevance_score.desc()
        ).limit(limit).all()
    
    def get_similar_questions(self, session: Session, similarity_threshold: float = 0.5, 
                             limit: int = 5) -> List['Question']:
        """获取相似题目"""
        from sqlalchemy import func
        
        # 基于共同知识点的相似度计算
        similar_questions = session.query(
            Question,
            func.count(question_knowledge_association.c.knowledge_point_id).label('common_knowledge_points')
        ).join(
            question_knowledge_association,
            Question.question_id == question_knowledge_association.c.question_id
        ).filter(
            question_knowledge_association.c.knowledge_point_id.in_(
                session.query(question_knowledge_association.c.knowledge_point_id).filter(
                    question_knowledge_association.c.question_id == self.question_id
                )
            ),
            Question.question_id != self.question_id,
            Question.is_active == True
        ).group_by(Question.question_id).having(
            func.count(question_knowledge_association.c.knowledge_point_id) >= similarity_threshold
        ).order_by(
            func.count(question_knowledge_association.c.knowledge_point_id).desc()
        ).limit(limit).all()
        
        return [q[0] for q in similar_questions]
    
    def get_knowledge_point_coverage(self, session: Session) -> List[Dict[str, Any]]:
        """获取知识点覆盖信息"""
        coverage = session.query(
            KnowledgePoint.id,
            KnowledgePoint.name,
            KnowledgePoint.difficulty_level,
            question_knowledge_association.c.relevance_score
        ).join(
            question_knowledge_association
        ).filter(
            question_knowledge_association.c.question_id == self.question_id
        ).all()
        
        return [{
            'knowledge_point_id': kp.id,
            'knowledge_point_name': kp.name,
            'difficulty_level': kp.difficulty_level,
            'relevance_score': kp.relevance_score
        } for kp in coverage]
    
    def analyze_answer_quality(self) -> Dict[str, Any]:
        """分析答案质量（基础版本，可以集成AI模型）"""
        analysis = {
            'question_id': self.question_id,
            'question_type': self.type.value,
            'has_answer': bool(self.answer and self.answer.strip()),
            'answer_length': len(self.answer) if self.answer else 0,
            'has_correct_answer': bool(self.correct_answer and self.correct_answer.strip()),
            'has_explanation': bool(self.explanation and self.explanation.strip())
        }
        
        # 简单的答案质量评估
        if self.answer:
            answer_words = len(self.answer.split())
            if self.type in [QuestionType.CHOICE, QuestionType.TRUE_FALSE]:
                analysis['answer_completeness'] = 'complete' if answer_words >= 1 else 'incomplete'
            elif self.type == QuestionType.FILL_BLANK:
                analysis['answer_completeness'] = 'complete' if answer_words >= 1 else 'incomplete'
            else:  # 主观题
                if answer_words >= 10:
                    analysis['answer_completeness'] = 'complete'
                elif answer_words >= 5:
                    analysis['answer_completeness'] = 'partial'
                else:
                    analysis['answer_completeness'] = 'incomplete'
        else:
            analysis['answer_completeness'] = 'missing'
            
        return analysis

class QuestionOption(Base):
    """题目选项表"""
    __tablename__ = 'question_options'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(100), ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False, comment='题目业务ID')
    option_key = Column(String(10), nullable=False, comment='选项键：A、B、C、D等')
    option_value = Column(Text, nullable=False, comment='选项内容')
    is_correct = Column(Boolean, default=False, nullable=False, comment='是否为正确答案')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    question = relationship("Question", back_populates="options")
    
    # 约束和索引
    __table_args__ = (
        Index('idx_qo_question', 'question_id'),
        Index('idx_qo_correct', 'is_correct'),
        {'mysql_engine': 'InnoDB'}
    )

# ========================================
# 标签系统
# ========================================

class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment='标签名称')
    category = Column(String(30), comment='标签分类：subject、difficulty、type等')
    description = Column(Text, comment='标签描述')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    questions = relationship("Question", secondary=question_tags, back_populates="tags")
    
    # 索引优化
    __table_args__ = (
        Index('idx_tag_name', 'name'),
        Index('idx_tag_category', 'category'),
        Index('idx_tag_active', 'is_active'),
    )

class KnowledgePointKeyword(Base):
    """知识点关键词表"""
    __tablename__ = 'knowledge_point_keywords'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False, comment='知识点ID')
    keyword = Column(String(100), nullable=False, comment='关键词')
    weight = Column(Float, default=1.0, nullable=False, comment='权重(0.0-1.0)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    knowledge_point = relationship("KnowledgePoint", back_populates="keywords")
    
    # 约束和索引
    __table_args__ = (
        Index('idx_kpk_knowledge', 'knowledge_point_id'),
        Index('idx_kpk_keyword', 'keyword'),
        Index('idx_kpk_weight', 'weight'),
        {'mysql_engine': 'InnoDB'}
    )

# ========================================
# 批改结果表
# ========================================

class GradingResult(Base):
    """批改结果表"""
    __tablename__ = 'grading_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False, comment='任务唯一ID')
    question_id = Column(String(100), ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False, comment='题目业务ID')
    
    # JSON Schema字段
    question = Column(Text, nullable=False, comment='题目内容快照')
    answer = Column(Text, nullable=False, comment='学生答案快照')
    type = Column(Enum(QuestionType), nullable=False, comment='题目类型')
    correct = Column(Boolean, nullable=False, comment='是否正确')
    score = Column(Float, nullable=False, comment='得分')
    explanation = Column(Text, nullable=False, comment='批改解释')
    
    # 扩展字段
    confidence = Column(Float, default=1.0, nullable=False, comment='批改置信度(0.0-1.0)')
    grading_engine = Column(String(30), comment='批改引擎')
    processing_time = Column(Float, comment='处理时间（秒）')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    question_rel = relationship("Question")
    task_record = relationship("TaskRecord", back_populates="grading_results")
    
    # 索引优化
    __table_args__ = (
        Index('idx_gr_task', 'task_id'),
        Index('idx_gr_question', 'question_id'),
        Index('idx_gr_correct', 'correct'),
        Index('idx_gr_score', 'score'),
        Index('idx_gr_created', 'created_at'),
        # 复合索引优化常用查询
        Index('idx_gr_task_correct', 'task_id', 'correct'),
        Index('idx_gr_task_score', 'task_id', 'score'),
    )

class TaskRecord(Base):
    """任务记录表"""
    __tablename__ = 'task_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), unique=True, nullable=False, comment='任务唯一ID')
    timestamp = Column(Integer, nullable=False, comment='时间戳')
    user_id = Column(String(100), comment='用户ID')
    
    # JSON Schema字段
    total_questions = Column(Integer, nullable=False, comment='总题目数')
    correct_count = Column(Integer, nullable=False, comment='正确数量')
    total_score = Column(Float, nullable=False, comment='总分')
    accuracy_rate = Column(Float, nullable=False, comment='正确率')
    
    # 扩展字段
    wrong_knowledges = Column(JSON, comment='错误知识点，JSON格式')
    ai_analysis = Column(JSON, comment='AI分析结果，JSON格式')
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False, comment='处理状态')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    grading_results = relationship("GradingResult", back_populates="task_record")
    
    # 索引优化
    __table_args__ = (
        Index('idx_tr_task_id', 'task_id'),
        Index('idx_tr_user', 'user_id'),
        Index('idx_tr_timestamp', 'timestamp'),
        Index('idx_tr_status', 'processing_status'),
        Index('idx_tr_accuracy', 'accuracy_rate'),
        Index('idx_tr_created', 'created_at'),
        # 复合索引优化常用查询
        Index('idx_tr_user_status', 'user_id', 'processing_status'),
        Index('idx_tr_user_created', 'user_id', 'created_at'),
    )

# ========================================
# 教学资源表
# ========================================

class Textbook(Base):
    """教材表"""
    __tablename__ = 'textbooks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='学科ID')
    name = Column(String(200), nullable=False, comment='教材名称')
    publisher = Column(String(100), comment='出版社')
    edition = Column(String(50), comment='版本')
    publish_year = Column(Integer, comment='出版年份')
    isbn = Column(String(20), comment='ISBN')
    description = Column(Text, comment='教材描述')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    subject = relationship("Subject", back_populates="textbooks")
    
    # 索引优化
    __table_args__ = (
        Index('idx_textbook_subject', 'subject_id'),
        Index('idx_textbook_publisher', 'publisher'),
        Index('idx_textbook_year', 'publish_year'),
        Index('idx_textbook_active', 'is_active'),
    )

class ExamPaper(Base):
    """试卷表"""
    __tablename__ = 'exam_papers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='学科ID')
    name = Column(String(200), nullable=False, comment='试卷名称')
    exam_type = Column(Enum(ExamType), nullable=False, comment='考试类型')
    exam_year = Column(Integer, comment='考试年份')
    region = Column(String(100), comment='考试地区')
    total_score = Column(Integer, comment='总分')
    duration = Column(Integer, comment='考试时长（分钟）')
    description = Column(Text, comment='试卷描述')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    subject = relationship("Subject", back_populates="exam_papers")
    
    # 索引优化
    __table_args__ = (
        Index('idx_exam_subject', 'subject_id'),
        Index('idx_exam_type', 'exam_type'),
        Index('idx_exam_year', 'exam_year'),
        Index('idx_exam_active', 'is_active'),
    )

# QuestionBank类已移动到question_bank.py中，避免重复定义

# ========================================
# 学习分析表
# ========================================

class LearningRecord(Base):
    """学习记录表"""
    __tablename__ = 'learning_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, comment='用户ID')
    question_id = Column(String(100), ForeignKey('questions.question_id', ondelete='CASCADE'), nullable=False, comment='题目业务ID')
    knowledge_point_id = Column(Integer, ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False, comment='知识点ID')
    
    # 学习数据
    answer_time = Column(Integer, comment='答题用时（秒）')
    is_correct = Column(Boolean, nullable=False, comment='是否答对')
    attempt_count = Column(TINYINT, default=1, nullable=False, comment='尝试次数')
    confidence_level = Column(TINYINT, comment='学生信心等级(1-5)')
    
    # 时间戳
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    question = relationship("Question", back_populates="learning_records")
    knowledge_point = relationship("KnowledgePoint")
    
    # 索引优化
    __table_args__ = (
        Index('idx_lr_user', 'user_id'),
        Index('idx_lr_question', 'question_id'),
        Index('idx_lr_knowledge', 'knowledge_point_id'),
        Index('idx_lr_correct', 'is_correct'),
        Index('idx_lr_answered', 'answered_at'),
        # 复合索引优化常用查询
        Index('idx_lr_user_knowledge', 'user_id', 'knowledge_point_id'),
        Index('idx_lr_user_correct', 'user_id', 'is_correct'),
    )

class UserProfile(Base):
    """用户学习画像表"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, comment='用户ID')
    
    # 学习能力评估
    math_level = Column(TINYINT, default=1, nullable=False, comment='数学水平等级(1-5)')
    chinese_level = Column(TINYINT, default=1, nullable=False, comment='语文水平等级(1-5)')
    english_level = Column(TINYINT, default=1, nullable=False, comment='英语水平等级(1-5)')
    
    # 学习偏好
    preferred_difficulty = Column(TINYINT, default=3, nullable=False, comment='偏好难度等级(1-5)')
    learning_style = Column(Enum(LearningStyle), default=LearningStyle.MIXED, nullable=False, comment='学习风格')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引优化
    __table_args__ = (
        Index('idx_up_user', 'user_id'),
        Index('idx_up_math', 'math_level'),
        Index('idx_up_chinese', 'chinese_level'),
        Index('idx_up_english', 'english_level'),
    )

# ========================================
# AI推荐服务类
# ========================================

class KnowledgeRecommendationService:
    """知识推荐服务 - AI功能支持"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_personalized_recommendations(self, user_id: str, subject_name: str, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """获取个性化推荐"""
        # 获取用户画像
        user_profile = self.session.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not user_profile:
            return self._get_default_recommendations(subject_name, limit)
        
        # 根据用户水平推荐
        subject_level_map = {
            'Mathematics': user_profile.math_level,
            'Chinese': user_profile.chinese_level,
            'English': user_profile.english_level
        }
        
        user_level = subject_level_map.get(subject_name, 3)
        preferred_difficulty = user_profile.preferred_difficulty
        
        # 获取用户薄弱的知识点
        weak_knowledge_points = self._get_weak_knowledge_points(user_id, subject_name)
        
        recommendations = []
        
        # 基于薄弱知识点推荐
        if weak_knowledge_points:
            for kp in weak_knowledge_points[:limit//2]:
                questions = kp.get_related_questions(
                    self.session, 
                    difficulty_filter=min(preferred_difficulty, user_level + 1),
                    limit=2
                )
                for q in questions:
                    recommendations.append({
                        'question_id': q.question_id,
                        'question_type': q.type.value,
                        'difficulty_level': q.difficulty_level,
                        'knowledge_point': kp.name,
                        'recommendation_reason': 'weak_knowledge_point',
                        'priority': 0.9
                    })
        
        # 基于学习偏好推荐
        remaining = limit - len(recommendations)
        if remaining > 0:
            preference_questions = self._get_preference_based_questions(
                subject_name, user_level, preferred_difficulty, remaining
            )
            for q in preference_questions:
                recommendations.append({
                    'question_id': q.question_id,
                    'question_type': q.type.value,
                    'difficulty_level': q.difficulty_level,
                    'recommendation_reason': 'preference_based',
                    'priority': 0.7
                })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        return recommendations[:limit]
    
    def _get_weak_knowledge_points(self, user_id: str, subject_name: str) -> List[KnowledgePoint]:
        """获取用户薄弱的知识点"""
        from sqlalchemy import func, and_
        
        weak_kps = self.session.query(KnowledgePoint).join(
            LearningRecord
        ).join(Question).join(Subject).filter(
            and_(
                Subject.name == subject_name,
                LearningRecord.user_id == user_id
            )
        ).group_by(KnowledgePoint.id).having(
            func.avg(LearningRecord.is_correct.cast(Float)) < 0.6  # 正确率低于60%
        ).order_by(
            func.avg(LearningRecord.is_correct.cast(Float)).asc()
        ).limit(5).all()
        
        return weak_kps
    
    def _get_preference_based_questions(self, subject_name: str, user_level: int, 
                                      preferred_difficulty: int, limit: int) -> List[Question]:
        """基于偏好获取题目"""
        target_difficulty = min(max(preferred_difficulty, user_level - 1), user_level + 1)
        
        questions = self.session.query(Question).join(Subject).filter(
            Subject.name == subject_name,
            Question.difficulty_level == target_difficulty,
            Question.is_active == True
        ).order_by(func.random()).limit(limit).all()
        
        return questions
    
    def _get_default_recommendations(self, subject_name: str, limit: int) -> List[Dict[str, Any]]:
        """获取默认推荐"""
        questions = self.session.query(Question).join(Subject).filter(
            Subject.name == subject_name,
            Question.difficulty_level.in_([2, 3]),  # 中等难度
            Question.is_active == True
        ).order_by(func.random()).limit(limit).all()
        
        return [{
            'question_id': q.question_id,
            'question_type': q.type.value,
            'difficulty_level': q.difficulty_level,
            'recommendation_reason': 'default',
            'priority': 0.5
        } for q in questions]
    
    def analyze_learning_progress(self, user_id: str, subject_name: str) -> Dict[str, Any]:
        """分析学习进度"""
        from sqlalchemy import func, and_
        
        # 总体统计
        total_stats = self.session.query(
            func.count(LearningRecord.id).label('total_attempts'),
            func.sum(LearningRecord.is_correct.cast(Integer)).label('correct_count'),
            func.avg(LearningRecord.answer_time).label('avg_time')
        ).join(Question).join(Subject).filter(
            and_(
                LearningRecord.user_id == user_id,
                Subject.name == subject_name
            )
        ).first()
        
        # 难度分布统计
        difficulty_stats = self.session.query(
            Question.difficulty_level,
            func.count(LearningRecord.id).label('attempts'),
            func.avg(LearningRecord.is_correct.cast(Float)).label('accuracy')
        ).join(LearningRecord).join(Subject).filter(
            and_(
                LearningRecord.user_id == user_id,
                Subject.name == subject_name
            )
        ).group_by(Question.difficulty_level).all()
        
        progress = {
            'user_id': user_id,
            'subject_name': subject_name,
            'total_attempts': total_stats.total_attempts or 0,
            'total_correct': total_stats.correct_count or 0,
            'overall_accuracy': (total_stats.correct_count or 0) / max(total_stats.total_attempts or 1, 1),
            'average_time': float(total_stats.avg_time) if total_stats.avg_time else 0,
            'difficulty_breakdown': {}
        }
        
        for diff_stat in difficulty_stats:
            progress['difficulty_breakdown'][diff_stat.difficulty_level] = {
                'attempts': diff_stat.attempts,
                'accuracy': float(diff_stat.accuracy) if diff_stat.accuracy else 0
            }
        
        return progress

# ========================================
# 导出所有模型
# ========================================

__all__ = [
    'Base',
    'BaseModel',
    'Grade',
    'Subject', 
    'Chapter',
    'KnowledgePoint',
    'Question',
    'QuestionOption',
    'Tag',
    'KnowledgePointKeyword',
    'GradingResult',
    'TaskRecord',
    'Textbook',
    'ExamPaper',
    'QuestionBank',
    'LearningRecord',
    'UserProfile',
    'KnowledgeRecommendationService',
    'QuestionType',
    'ProcessingStatus',
    'RelationshipType',
    'LearningStyle',
    'ExamType',
]
