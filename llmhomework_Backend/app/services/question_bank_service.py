"""
AI作业批改系统 - 题库管理服务
Day 9: 构建大规模题目数据库服务层

主要功能：
1. 题目批量导入和处理
2. 题目质量评估和优化
3. 题库统计和分析
4. 题目检索和筛选
5. 数据清洗和标准化
"""

import os
import json
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.question_bank import (
    StandardQuestion, QuestionOption, QuestionBank, QuestionBankManager,
    QuestionType, DifficultyLevel, QuestionSource, QuestionStatus,
    AnswerFormat, validate_question_data, calculate_question_similarity
)
from app.models.knowledge_base import Subject, KnowledgePoint
from app.config import Config

logger = logging.getLogger(__name__)


class QuestionBankService:
    """题库服务类 - 提供完整的题库管理功能"""
    
    def __init__(self, session: Session):
        self.session = session
        self.manager = QuestionBankManager(session)
    
    def import_crawled_data(self, data_directory: str) -> Dict[str, Any]:
        """导入爬取的题目数据"""
        results = {
            'total_processed': 0,
            'total_imported': 0,
            'total_failed': 0,
            'files_processed': [],
            'errors': []
        }
        
        try:
            # 查找所有CSV文件
            csv_files = []
            for root, dirs, files in os.walk(data_directory):
                for file in files:
                    if file.endswith('.csv') and 'questions' in file.lower():
                        csv_files.append(os.path.join(root, file))
            
            logger.info(f"发现 {len(csv_files)} 个题目CSV文件")
            
            for csv_file in csv_files:
                try:
                    file_result = self._import_single_csv_file(csv_file)
                    results['files_processed'].append({
                        'file': csv_file,
                        'result': file_result
                    })
                    results['total_processed'] += file_result['total']
                    results['total_imported'] += file_result['success']
                    results['total_failed'] += file_result['failed']
                    
                except Exception as e:
                    error_msg = f"处理文件 {csv_file} 失败: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f"导入完成: 处理 {results['total_processed']} 个题目，"
                       f"成功 {results['total_imported']} 个，失败 {results['total_failed']} 个")
            
            return results
            
        except Exception as e:
            logger.error(f"批量导入失败: {str(e)}")
            raise
    
    def _import_single_csv_file(self, file_path: str) -> Dict[str, Any]:
        """导入单个CSV文件"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"开始处理文件: {file_path}, 包含 {len(df)} 行数据")
            
            results = {
                'total': len(df),
                'success': 0,
                'failed': 0,
                'errors': [],
                'duplicates_skipped': 0
            }
            
            for index, row in df.iterrows():
                try:
                    # 验证数据
                    validation = self._validate_row_data(row)
                    if not validation['valid']:
                        results['failed'] += 1
                        results['errors'].append(f"第{index+1}行验证失败: {validation['errors']}")
                        continue
                    
                    # 检查重复
                    if self._is_duplicate_question(row):
                        results['duplicates_skipped'] += 1
                        continue
                    
                    # 创建题目
                    question = self._create_question_from_csv_row(row)
                    self.session.add(question)
                    results['success'] += 1
                    
                    # 每100个题目提交一次
                    if results['success'] % 100 == 0:
                        self.session.commit()
                        logger.info(f"已处理 {results['success']} 个题目")
                
                except Exception as e:
                    results['failed'] += 1
                    error_msg = f"第{index+1}行处理失败: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.warning(error_msg)
            
            # 最终提交
            self.session.commit()
            return results
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"导入CSV文件失败: {str(e)}")
    
    def _validate_row_data(self, row: pd.Series) -> Dict[str, Any]:
        """验证CSV行数据"""
        errors = []
        
        # 检查必需字段
        required_fields = ['stem', 'correct_answer', 'question_type']
        for field in required_fields:
            if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
                errors.append(f"缺少必需字段: {field}")
        
        # 检查题目类型
        if row.get('question_type'):
            try:
                QuestionType(row['question_type'])
            except ValueError:
                errors.append(f"无效的题目类型: {row['question_type']}")
        
        # 检查难度等级
        if row.get('difficulty_level'):
            try:
                level = int(row['difficulty_level'])
                if level < 1 or level > 5:
                    errors.append("难度等级必须在1-5之间")
            except (ValueError, TypeError):
                errors.append("难度等级必须是数字")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_duplicate_question(self, row: pd.Series) -> bool:
        """检查是否为重复题目"""
        stem = str(row.get('stem', '')).strip()
        if len(stem) < 10:
            return False
        
        # 检查是否存在相似的题目
        existing = self.session.query(StandardQuestion).filter(
            StandardQuestion.stem.like(f"%{stem[:50]}%")
        ).first()
        
        return existing is not None
    
    def _create_question_from_csv_row(self, row: pd.Series) -> StandardQuestion:
        """从CSV行创建StandardQuestion对象"""
        # 获取或创建学科
        subject = self._get_or_create_subject(row.get('subject', '数学'), row.get('grade', 'Grade 7'))
        
        # 创建题目
        question = StandardQuestion(
            subject_id=subject.id,
            grade_level=row.get('grade', 'Grade 7'),
            stem=str(row.get('stem', '')).strip(),
            question_type=QuestionType(row.get('question_type', 'fill_blank')),
            correct_answer=str(row.get('correct_answer', '')).strip(),
            explanation=str(row.get('explanation', '')).strip(),
            difficulty_level=DifficultyLevel(int(row.get('difficulty_level', 3))),
            source=QuestionSource.CROWDSOURCE,
            status=QuestionStatus.APPROVED,
            quality_score=float(row.get('score', 5.0)) if row.get('score') else 5.0,
            created_by='system_import'
        )
        
        # 添加元数据
        extra_metadata = {}
        for field in ['source', 'source_type', 'year', 'tags']:
            if row.get(field) and not pd.isna(row[field]):
                extra_metadata[field] = str(row[field])
        
        if extra_metadata:
            question.extra_metadata = extra_metadata
        
        # 添加关键词和标签
        if row.get('knowledge_points'):
            keywords = str(row['knowledge_points']).split('|')
            question.keywords = [kw.strip() for kw in keywords if kw.strip()]
        
        if row.get('tags'):
            tags = str(row['tags']).split('|')
            question.tags = [tag.strip() for tag in tags if tag.strip()]
        
        return question
    
    def _get_or_create_subject(self, subject_name: str, grade_level: str) -> Subject:
        """获取或创建学科"""
        # 标准化学科名称
        subject_map = {
            '数学': 'Mathematics',
            '语文': 'Chinese', 
            '英语': 'English',
            '物理': 'Physics',
            '化学': 'Chemistry',
            '生物': 'Biology',
            '历史': 'History',
            '地理': 'Geography',
            '政治': 'Politics'
        }
        
        standard_name = subject_map.get(subject_name, subject_name)
        
        # 查找现有学科
        subject = self.session.query(Subject).filter(
            Subject.name == standard_name
        ).first()
        
        if not subject:
            # 这里应该创建学科，但需要先有grade_id
            # 简化处理：返回默认学科
            subject = self.session.query(Subject).filter(
                Subject.name == 'Mathematics'
            ).first()
            
            if not subject:
                raise Exception("未找到默认学科，请先初始化数据库")
        
        return subject
    
    def generate_practice_questions(self, 
                                  subject_id: int,
                                  difficulty_level: Optional[DifficultyLevel] = None,
                                  question_types: Optional[List[QuestionType]] = None,
                                  count: int = 10) -> List[StandardQuestion]:
        """生成练习题集"""
        query = self.session.query(StandardQuestion).filter(
            StandardQuestion.subject_id == subject_id,
            StandardQuestion.status == QuestionStatus.PUBLISHED
        )
        
        if difficulty_level:
            query = query.filter(StandardQuestion.difficulty_level == difficulty_level)
        
        if question_types:
            query = query.filter(StandardQuestion.question_type.in_(question_types))
        
        # 优先选择高质量题目
        query = query.order_by(StandardQuestion.quality_score.desc())
        
        questions = query.limit(count * 2).all()  # 获取更多候选题目
        
        # 随机选择并保证多样性
        if len(questions) > count:
            import random
            # 按题型分组
            type_groups = {}
            for q in questions:
                qtype = q.question_type
                if qtype not in type_groups:
                    type_groups[qtype] = []
                type_groups[qtype].append(q)
            
            # 从每个题型中选择题目
            selected = []
            per_type = max(1, count // len(type_groups))
            
            for qtype, group in type_groups.items():
                selected.extend(random.sample(group, min(per_type, len(group))))
            
            # 如果还需要更多题目，随机补充
            if len(selected) < count:
                remaining = [q for q in questions if q not in selected]
                need = count - len(selected)
                selected.extend(random.sample(remaining, min(need, len(remaining))))
            
            return selected[:count]
        
        return questions
    
    def analyze_question_quality(self, question_id: str) -> Dict[str, Any]:
        """分析题目质量"""
        question = self.session.query(StandardQuestion).filter(
            StandardQuestion.question_id == question_id
        ).first()
        
        if not question:
            raise Exception("题目不存在")
        
        analysis = {
            'question_id': question_id,
            'current_quality_score': question.quality_score,
            'usage_statistics': {
                'usage_count': question.usage_count,
                'correct_rate': question.correct_rate,
                'average_time': question.average_time
            },
            'content_analysis': self._analyze_question_content(question),
            'recommendations': []
        }
        
        # 生成改进建议
        if question.correct_rate < 0.3:
            analysis['recommendations'].append("题目可能过于困难，考虑降低难度或添加提示")
        
        if question.correct_rate > 0.9:
            analysis['recommendations'].append("题目可能过于简单，考虑增加难度")
        
        if len(question.stem) < 20:
            analysis['recommendations'].append("题目描述过于简短，建议丰富内容")
        
        if not question.explanation:
            analysis['recommendations'].append("建议添加详细解析")
        
        return analysis
    
    def _analyze_question_content(self, question: StandardQuestion) -> Dict[str, Any]:
        """分析题目内容"""
        return {
            'stem_length': len(question.stem),
            'answer_length': len(question.correct_answer),
            'has_explanation': bool(question.explanation),
            'has_options': len(question.options) > 0 if hasattr(question, 'options') else False,
            'complexity_indicators': {
                'contains_formulas': '=' in question.stem or '+' in question.stem,
                'contains_images': '[图]' in question.stem or '![' in question.stem,
                'word_count': len(question.stem.split()),
                'sentence_count': question.stem.count('.') + question.stem.count('?') + question.stem.count('!')
            }
        }
    
    def get_question_bank_statistics(self) -> Dict[str, Any]:
        """获取题库统计信息"""
        return self.manager.generate_question_statistics()
    
    def search_questions(self, 
                        keywords: str,
                        subject_id: Optional[int] = None,
                        grade_level: Optional[str] = None,
                        difficulty_level: Optional[DifficultyLevel] = None,
                        question_types: Optional[List[QuestionType]] = None,
                        limit: int = 50) -> List[StandardQuestion]:
        """搜索题目"""
        query = self.session.query(StandardQuestion).filter(
            StandardQuestion.status == QuestionStatus.PUBLISHED
        )
        
        # 关键词搜索
        if keywords:
            search_term = f"%{keywords}%"
            query = query.filter(
                or_(
                    StandardQuestion.stem.like(search_term),
                    StandardQuestion.correct_answer.like(search_term),
                    StandardQuestion.explanation.like(search_term)
                )
            )
        
        # 其他筛选条件
        if subject_id:
            query = query.filter(StandardQuestion.subject_id == subject_id)
        
        if grade_level:
            query = query.filter(StandardQuestion.grade_level == grade_level)
        
        if difficulty_level:
            query = query.filter(StandardQuestion.difficulty_level == difficulty_level)
        
        if question_types:
            query = query.filter(StandardQuestion.question_type.in_(question_types))
        
        # 按质量分数排序
        query = query.order_by(StandardQuestion.quality_score.desc())
        
        return query.limit(limit).all()
    
    def update_question_statistics(self, question_id: str, is_correct: bool, time_spent: float):
        """更新题目统计信息"""
        question = self.session.query(StandardQuestion).filter(
            StandardQuestion.question_id == question_id
        ).first()
        
        if question:
            question.update_statistics(is_correct, time_spent)
            self.session.commit()
    
    def duplicate_detection(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """检测重复题目"""
        questions = self.session.query(StandardQuestion).filter(
            StandardQuestion.status == QuestionStatus.PUBLISHED
        ).all()
        
        duplicates = []
        processed = set()
        
        for i, q1 in enumerate(questions):
            if q1.question_id in processed:
                continue
                
            for j, q2 in enumerate(questions[i+1:], i+1):
                if q2.question_id in processed:
                    continue
                
                similarity = calculate_question_similarity(q1, q2)
                if similarity >= threshold:
                    duplicates.append({
                        'question1_id': q1.question_id,
                        'question2_id': q2.question_id,
                        'similarity': similarity,
                        'question1_stem': q1.stem[:100] + '...',
                        'question2_stem': q2.stem[:100] + '...'
                    })
                    processed.add(q2.question_id)
        
        return duplicates
    
    def batch_quality_assessment(self, batch_size: int = 100) -> Dict[str, Any]:
        """批量质量评估"""
        questions = self.session.query(StandardQuestion).filter(
            StandardQuestion.status == QuestionStatus.PUBLISHED,
            StandardQuestion.usage_count >= 10
        ).limit(batch_size).all()
        
        results = {
            'total_assessed': 0,
            'quality_improved': 0,
            'recommendations_generated': 0
        }
        
        for question in questions:
            # 重新计算质量分数
            old_score = question.quality_score
            new_score = self._calculate_quality_score(question)
            
            if abs(new_score - old_score) > 0.5:
                question.quality_score = new_score
                results['quality_improved'] += 1
            
            results['total_assessed'] += 1
        
        self.session.commit()
        return results
    
    def get_all_questions(self, limit: int = 1000) -> List[StandardQuestion]:
        """获取所有题目（用于相似度搜索）"""
        questions = self.session.query(StandardQuestion).filter(
            StandardQuestion.status == QuestionStatus.PUBLISHED
        ).limit(limit).all()
        
        return questions
    
    def _calculate_quality_score(self, question: StandardQuestion) -> float:
        """计算题目质量分数"""
        score = 5.0  # 基础分数
        
        # 基于使用统计调整
        if question.usage_count >= 10:
            # 正确率调整 (0.3-0.8 为理想范围)
            if 0.3 <= question.correct_rate <= 0.8:
                score += 2.0
            elif question.correct_rate < 0.2 or question.correct_rate > 0.9:
                score -= 1.0
            
            # 完成时间调整
            if 30 <= question.average_time <= 300:  # 30秒到5分钟为合理范围
                score += 1.0
            elif question.average_time > 600:  # 超过10分钟
                score -= 1.0
        
        # 内容质量调整
        if len(question.stem) >= 20:
            score += 0.5
        
        if question.explanation and len(question.explanation) >= 10:
            score += 1.0
        
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_CHOICE]:
            if hasattr(question, 'options') and len(question.options) >= 3:
                score += 0.5
        
        return min(10.0, max(0.0, score))


# ========================================
# 工具函数
# ========================================

def initialize_question_bank_from_crawled_data():
    """从爬取数据初始化题库的主入口函数"""
    from app.database import get_session
    
    session = get_session()
    service = QuestionBankService(session)
    
    try:
        # 获取爬取数据目录
        data_directory = os.path.join(
            os.path.dirname(__file__), 
            '../../data_collection/collectors/crawled_data'
        )
        
        if not os.path.exists(data_directory):
            logger.warning(f"数据目录不存在: {data_directory}")
            return
        
        # 导入数据
        results = service.import_crawled_data(data_directory)
        
        logger.info("题库初始化完成:")
        logger.info(f"  - 总共处理: {results['total_processed']} 个题目")
        logger.info(f"  - 成功导入: {results['total_imported']} 个题目")
        logger.info(f"  - 导入失败: {results['total_failed']} 个题目")
        
        return results
        
    except Exception as e:
        logger.error(f"题库初始化失败: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # 用于测试和初始化
    logging.basicConfig(level=logging.INFO)
    initialize_question_bank_from_crawled_data()
