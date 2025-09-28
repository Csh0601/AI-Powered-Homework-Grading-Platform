"""
AI作业批改系统 - 题库管理API端点
Day 9: 构建大规模题目数据库的API接口

主要功能：
1. 题目导入和批量处理API
2. 题库查询和检索API
3. 题目质量分析API
4. 题库统计和报告API
5. 练习题生成API
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any, List, Optional

from app.services.question_bank_service import QuestionBankService
from app.models.question_bank import QuestionType, DifficultyLevel, QuestionSource
from app.database import get_session
from app.utils.response_helper import success_response, error_response
from app.config import Config

# 创建蓝图
question_bank_bp = Blueprint('question_bank', __name__, url_prefix='/api/question_bank')

logger = logging.getLogger(__name__)


@question_bank_bp.route('/import_crawled_data', methods=['POST'])
@cross_origin()
def import_crawled_data():
    """导入爬取的题目数据"""
    try:
        session = get_session()
        service = QuestionBankService(session)
        
        # 获取数据目录路径
        import os
        data_directory = os.path.join(
            os.path.dirname(__file__), 
            '../../data_collection/collectors/crawled_data'
        )
        
        if not os.path.exists(data_directory):
            return error_response("数据目录不存在", 404)
        
        # 执行导入
        results = service.import_crawled_data(data_directory)
        
        logger.info(f"题目导入完成: 成功 {results['total_imported']} 个，失败 {results['total_failed']} 个")
        
        return success_response(results, "题目数据导入完成")
        
    except Exception as e:
        logger.error(f"导入题目数据失败: {str(e)}")
        return error_response(f"导入失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_statistics():
    """获取题库统计信息"""
    try:
        session = get_session()
        service = QuestionBankService(session)
        
        stats = service.get_question_bank_statistics()
        
        return success_response(stats, "题库统计信息")
        
    except Exception as e:
        logger.error(f"获取题库统计失败: {str(e)}")
        return error_response(f"获取统计信息失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/search', methods=['POST'])
@cross_origin()
def search_questions():
    """搜索题目"""
    try:
        data = request.get_json()
        
        session = get_session()
        service = QuestionBankService(session)
        
        # 解析搜索参数
        keywords = data.get('keywords', '')
        subject_id = data.get('subject_id')
        grade_level = data.get('grade_level')
        difficulty_level = None
        question_types = None
        limit = data.get('limit', 20)
        
        # 处理难度等级
        if data.get('difficulty_level'):
            try:
                difficulty_level = DifficultyLevel(int(data['difficulty_level']))
            except (ValueError, TypeError):
                pass
        
        # 处理题目类型
        if data.get('question_types'):
            try:
                question_types = [QuestionType(qtype) for qtype in data['question_types']]
            except (ValueError, TypeError):
                pass
        
        # 执行搜索
        questions = service.search_questions(
            keywords=keywords,
            subject_id=subject_id,
            grade_level=grade_level,
            difficulty_level=difficulty_level,
            question_types=question_types,
            limit=limit
        )
        
        # 转换为字典格式
        results = []
        for question in questions:
            question_dict = question.to_dict()
            results.append(question_dict)
        
        return success_response({
            'questions': results,
            'total': len(results)
        }, "搜索完成")
        
    except Exception as e:
        logger.error(f"搜索题目失败: {str(e)}")
        return error_response(f"搜索失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/generate_practice', methods=['POST'])
@cross_origin()
def generate_practice_questions():
    """生成练习题集"""
    try:
        data = request.get_json()
        
        session = get_session()
        service = QuestionBankService(session)
        
        # 解析参数
        subject_id = data.get('subject_id')
        difficulty_level = None
        question_types = None
        count = data.get('count', 10)
        
        if not subject_id:
            return error_response("缺少学科ID参数", 400)
        
        # 处理难度等级
        if data.get('difficulty_level'):
            try:
                difficulty_level = DifficultyLevel(int(data['difficulty_level']))
            except (ValueError, TypeError):
                pass
        
        # 处理题目类型
        if data.get('question_types'):
            try:
                question_types = [QuestionType(qtype) for qtype in data['question_types']]
            except (ValueError, TypeError):
                pass
        
        # 生成练习题
        questions = service.generate_practice_questions(
            subject_id=subject_id,
            difficulty_level=difficulty_level,
            question_types=question_types,
            count=count
        )
        
        # 转换为字典格式
        results = []
        for question in questions:
            question_dict = question.to_dict()
            # 添加选项信息（如果是选择题）
            if hasattr(question, 'options') and question.options:
                question_dict['options'] = [opt.to_dict() for opt in question.options]
            results.append(question_dict)
        
        return success_response({
            'practice_questions': results,
            'total': len(results),
            'generated_at': datetime.utcnow().isoformat()
        }, "练习题生成完成")
        
    except Exception as e:
        logger.error(f"生成练习题失败: {str(e)}")
        return error_response(f"生成练习题失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/analyze_quality/<question_id>', methods=['GET'])
@cross_origin()
def analyze_question_quality(question_id: str):
    """分析题目质量"""
    try:
        session = get_session()
        service = QuestionBankService(session)
        
        analysis = service.analyze_question_quality(question_id)
        
        return success_response(analysis, "质量分析完成")
        
    except Exception as e:
        logger.error(f"分析题目质量失败: {str(e)}")
        return error_response(f"分析失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/detect_duplicates', methods=['POST'])
@cross_origin()
def detect_duplicates():
    """检测重复题目"""
    try:
        data = request.get_json() or {}
        threshold = data.get('threshold', 0.8)
        
        session = get_session()
        service = QuestionBankService(session)
        
        duplicates = service.duplicate_detection(threshold=threshold)
        
        return success_response({
            'duplicates': duplicates,
            'total_duplicates': len(duplicates),
            'threshold': threshold
        }, "重复检测完成")
        
    except Exception as e:
        logger.error(f"检测重复题目失败: {str(e)}")
        return error_response(f"检测失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/batch_quality_assessment', methods=['POST'])
@cross_origin()
def batch_quality_assessment():
    """批量质量评估"""
    try:
        data = request.get_json() or {}
        batch_size = data.get('batch_size', 100)
        
        session = get_session()
        service = QuestionBankService(session)
        
        results = service.batch_quality_assessment(batch_size=batch_size)
        
        return success_response(results, "批量质量评估完成")
        
    except Exception as e:
        logger.error(f"批量质量评估失败: {str(e)}")
        return error_response(f"评估失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/update_statistics', methods=['POST'])
@cross_origin()
def update_question_statistics():
    """更新题目统计信息"""
    try:
        data = request.get_json()
        
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')
        time_spent = data.get('time_spent')
        
        if not all([question_id is not None, is_correct is not None, time_spent is not None]):
            return error_response("缺少必需参数", 400)
        
        session = get_session()
        service = QuestionBankService(session)
        
        service.update_question_statistics(question_id, is_correct, time_spent)
        
        return success_response({}, "统计信息更新完成")
        
    except Exception as e:
        logger.error(f"更新统计信息失败: {str(e)}")
        return error_response(f"更新失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/subjects', methods=['GET'])
@cross_origin()
def get_subjects():
    """获取所有学科列表"""
    try:
        session = get_session()
        
        from app.models.knowledge_base import Subject
        subjects = session.query(Subject).filter(Subject.is_active == True).all()
        
        results = []
        for subject in subjects:
            results.append({
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'description': subject.description,
                'difficulty_level': subject.difficulty_level
            })
        
        return success_response({
            'subjects': results,
            'total': len(results)
        }, "学科列表")
        
    except Exception as e:
        logger.error(f"获取学科列表失败: {str(e)}")
        return error_response(f"获取学科失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/question_types', methods=['GET'])
@cross_origin()
def get_question_types():
    """获取题目类型列表"""
    try:
        types = []
        for qtype in QuestionType:
            types.append({
                'value': qtype.value,
                'name': qtype.name,
                'description': _get_question_type_description(qtype)
            })
        
        return success_response({
            'question_types': types,
            'total': len(types)
        }, "题目类型列表")
        
    except Exception as e:
        logger.error(f"获取题目类型失败: {str(e)}")
        return error_response(f"获取题目类型失败: {str(e)}", 500)


@question_bank_bp.route('/difficulty_levels', methods=['GET'])
@cross_origin()
def get_difficulty_levels():
    """获取难度等级列表"""
    try:
        levels = []
        for level in DifficultyLevel:
            levels.append({
                'value': level.value,
                'name': level.name,
                'description': _get_difficulty_description(level)
            })
        
        return success_response({
            'difficulty_levels': levels,
            'total': len(levels)
        }, "难度等级列表")
        
    except Exception as e:
        logger.error(f"获取难度等级失败: {str(e)}")
        return error_response(f"获取难度等级失败: {str(e)}", 500)


@question_bank_bp.route('/find_similar', methods=['POST'])
@cross_origin()
def find_similar_questions():
    """查找相似题目 - Day10功能"""
    try:
        data = request.get_json()
        
        if not data or 'query_question' not in data:
            return error_response("缺少查询题目参数", 400)
        
        query_question = data['query_question']
        top_k = data.get('top_k', 10)
        similarity_threshold = data.get('similarity_threshold', 0.3)
        
        # 导入相似度搜索引擎
        from app.services.similarity_search import SimilaritySearchEngine
        
        # 创建搜索引擎实例
        search_engine = SimilaritySearchEngine()
        
        # 从数据库获取所有题目用于构建索引
        session = get_session()
        service = QuestionBankService(session)
        
        # 获取所有题目（限制数量以避免内存问题）
        all_questions = service.get_all_questions(limit=1000)
        
        if not all_questions:
            return error_response("题库中没有题目数据", 404)
        
        # 转换为搜索引擎需要的格式
        questions_for_index = []
        for question in all_questions:
            questions_for_index.append({
                'question_id': question.question_id,
                'stem': question.stem,
                'correct_answer': question.correct_answer,
                'question_type': question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type),
                'difficulty_level': question.difficulty_level.value if hasattr(question.difficulty_level, 'value') else question.difficulty_level,
                'subject': question.subject.code if hasattr(question, 'subject') and question.subject else 'unknown'
            })
        
        # 构建索引
        index_result = search_engine.build_question_index(questions_for_index)
        
        if not index_result['success']:
            return error_response(f"构建索引失败: {index_result.get('error', '未知错误')}", 500)
        
        # 执行相似度搜索
        similar_questions = search_engine.find_similar_questions(
            query_question, 
            top_k=top_k, 
            similarity_threshold=similarity_threshold
        )
        
        # 获取搜索统计
        search_stats = search_engine.get_search_statistics()
        
        return success_response({
            'similar_questions': similar_questions,
            'total_found': len(similar_questions),
            'search_statistics': search_stats,
            'index_statistics': {
                'indexed_questions': index_result['indexed_questions'],
                'build_time_seconds': index_result['build_time_seconds'],
                'vector_dimensions': index_result['vector_dimensions']
            }
        }, "相似题目搜索完成")
        
    except Exception as e:
        logger.error(f"查找相似题目失败: {str(e)}")
        return error_response(f"搜索失败: {str(e)}", 500)
    finally:
        session.close()


@question_bank_bp.route('/export_questions', methods=['POST'])
@cross_origin()
def export_questions():
    """导出题目数据"""
    try:
        data = request.get_json() or {}
        
        session = get_session()
        service = QuestionBankService(session)
        
        # 获取筛选条件
        subject_id = data.get('subject_id')
        grade_level = data.get('grade_level')
        difficulty_level = None
        question_types = None
        limit = data.get('limit', 1000)
        
        if data.get('difficulty_level'):
            try:
                difficulty_level = DifficultyLevel(int(data['difficulty_level']))
            except (ValueError, TypeError):
                pass
        
        if data.get('question_types'):
            try:
                question_types = [QuestionType(qtype) for qtype in data['question_types']]
            except (ValueError, TypeError):
                pass
        
        # 获取题目
        questions = service.search_questions(
            keywords='',
            subject_id=subject_id,
            grade_level=grade_level,
            difficulty_level=difficulty_level,
            question_types=question_types,
            limit=limit
        )
        
        # 转换为导出格式
        export_data = []
        for question in questions:
            question_data = {
                'question_id': question.question_id,
                'subject': question.subject.name if hasattr(question, 'subject') else '',
                'grade_level': question.grade_level,
                'question_type': question.question_type.value,
                'stem': question.stem,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'difficulty_level': question.difficulty_level.value,
                'quality_score': question.quality_score,
                'usage_count': question.usage_count,
                'correct_rate': question.correct_rate,
                'source': question.source.value,
                'created_at': question.created_at.isoformat()
            }
            
            # 添加选项（如果有）
            if hasattr(question, 'options') and question.options:
                options_str = '|'.join([f"{opt.option_key}:{opt.option_value}" for opt in question.options])
                question_data['options'] = options_str
            
            export_data.append(question_data)
        
        return success_response({
            'questions': export_data,
            'total': len(export_data),
            'exported_at': datetime.utcnow().isoformat()
        }, "题目导出完成")
        
    except Exception as e:
        logger.error(f"导出题目失败: {str(e)}")
        return error_response(f"导出失败: {str(e)}", 500)
    finally:
        session.close()


# ========================================
# 辅助函数
# ========================================

def _get_question_type_description(qtype: QuestionType) -> str:
    """获取题目类型描述"""
    descriptions = {
        QuestionType.MULTIPLE_CHOICE: "多选题",
        QuestionType.SINGLE_CHOICE: "单选题", 
        QuestionType.TRUE_FALSE: "判断题",
        QuestionType.FILL_BLANK: "填空题",
        QuestionType.SHORT_ANSWER: "简答题",
        QuestionType.ESSAY: "论述题",
        QuestionType.CALCULATION: "计算题",
        QuestionType.PROOF: "证明题",
        QuestionType.ANALYSIS: "分析题",
        QuestionType.SYNTHESIS: "综合题"
    }
    return descriptions.get(qtype, qtype.value)


def _get_difficulty_description(level: DifficultyLevel) -> str:
    """获取难度等级描述"""
    descriptions = {
        DifficultyLevel.VERY_EASY: "非常简单",
        DifficultyLevel.EASY: "简单",
        DifficultyLevel.MEDIUM: "中等",
        DifficultyLevel.HARD: "困难", 
        DifficultyLevel.VERY_HARD: "非常困难"
    }
    return descriptions.get(level, f"等级{level.value}")


# ========================================
# 错误处理
# ========================================

@question_bank_bp.errorhandler(Exception)
def handle_error(error):
    """统一错误处理"""
    logger.error(f"题库API错误: {str(error)}")
    return error_response("内部服务器错误", 500)


# 导入必要的模块
from datetime import datetime
