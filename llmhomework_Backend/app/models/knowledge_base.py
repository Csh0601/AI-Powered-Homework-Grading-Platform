"""
教材知识库数据模型 - 符合JSON Schema规范
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# 题目类型枚举 - 符合JSON Schema
class QuestionType(enum.Enum):
    CHOICE = "选择题"
    JUDGE = "判断题"
    FILL = "填空题"
    CALCULATION = "计算题"
    APPLICATION = "应用题"
    FORMULA = "公式题"
    MENTAL = "口算题"
    UNKNOWN = "未知题型"
    FAILED = "识别失败"

# 关联表
question_knowledge_association = Table(
    'question_knowledge_association',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('knowledge_point_id', Integer, ForeignKey('knowledge_points.id'), primary_key=True),
    Column('relevance_score', Float, default=1.0),
    Column('created_at', DateTime, default=datetime.utcnow)
)

knowledge_relationship = Table(
    'knowledge_relationship',
    Base.metadata,
    Column('prerequisite_id', Integer, ForeignKey('knowledge_points.id'), primary_key=True),
    Column('dependent_id', Integer, ForeignKey('knowledge_points.id'), primary_key=True),
    Column('relationship_type', String(50)),
    Column('strength', Float, default=1.0),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Grade(Base):
    """年级表"""
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subjects = relationship("Subject", back_populates="grade")

class Subject(Base):
    """学科表"""
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=False)
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    grade = relationship("Grade", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject")

class Chapter(Base):
    """章节表"""
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    chapter_number = Column(Integer)
    difficulty_level = Column(Integer, default=1)
    estimated_hours = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subject = relationship("Subject", back_populates="chapters")
    knowledge_points = relationship("KnowledgePoint", back_populates="chapter")

class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = 'knowledge_points'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(100), nullable=False)
    description = Column(Text)
    keywords = Column(Text)
    difficulty_level = Column(Integer, default=1)
    importance_level = Column(Integer, default=1)
    exam_frequency = Column(Integer, default=0)
    learning_objectives = Column(Text)
    common_mistakes = Column(Text)
    learning_tips = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapter = relationship("Chapter", back_populates="knowledge_points")
    questions = relationship("Question", secondary=question_knowledge_association, back_populates="knowledge_points")
    
    prerequisites = relationship(
        "KnowledgePoint",
        secondary=knowledge_relationship,
        primaryjoin=id == knowledge_relationship.c.dependent_id,
        secondaryjoin=id == knowledge_relationship.c.prerequisite_id,
        backref="dependents"
    )

class Question(Base):
    """题目表 - 符合JSON Schema"""
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    
    # JSON Schema字段
    number = Column(String(20), nullable=False)
    stem = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    options = Column(Text)
    type = Column(String(50), nullable=False)
    question_id = Column(String(100), unique=True, nullable=False)
    timestamp = Column(Integer, nullable=False)
    
    # 扩展字段
    correct_answer = Column(Text)
    explanation = Column(Text)
    difficulty_level = Column(Integer, default=1)
    source = Column(String(200))
    source_type = Column(String(50))
    tags = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subject = relationship("Subject")
    knowledge_points = relationship("KnowledgePoint", secondary=question_knowledge_association, back_populates="questions")

class GradingResult(Base):
    """批改结果表 - 符合JSON Schema"""
    __tablename__ = 'grading_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False)
    question_id = Column(String(100), nullable=False)
    
    # JSON Schema字段
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    correct = Column(Boolean, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    
    # 扩展字段
    confidence = Column(Float, default=1.0)
    grading_engine = Column(String(50))
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskRecord(Base):
    """任务记录表 - 符合JSON Schema"""
    __tablename__ = 'task_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), unique=True, nullable=False)
    timestamp = Column(Integer, nullable=False)
    user_id = Column(String(100))
    
    # JSON Schema字段
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    total_score = Column(Float, nullable=False)
    accuracy_rate = Column(Float, nullable=False)
    
    # 扩展字段
    wrong_knowledges = Column(Text)
    ai_analysis = Column(Text)
    processing_status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
