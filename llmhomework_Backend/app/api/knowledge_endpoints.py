#!/usr/bin/env python3
"""
知识库管理API端点
Day 7 任务实现 - 完整的知识库查询、搜索、推荐接口

主要功能：
1. 知识点CRUD操作
2. 知识点搜索和过滤
3. 智能推荐接口
4. 知识点关联分析
5. 学习数据统计

技术要点：
- RESTful API设计
- 数据验证和错误处理
- 缓存优化
- 分页查询
- 响应时间监控
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, List, Any, Optional
import logging
import time
from datetime import datetime, timedelta
import json

# 导入服务模块
try:
    from app.services.knowledge_matcher import KnowledgeMatcher
    from app.services.subject_classifier import SubjectClassifier
    from app.utils.response_helper import success_response, error_response, validate_request
    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"部分服务模块导入失败: {e}")
    SERVICES_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
knowledge_api = Blueprint('knowledge_api', __name__, url_prefix='/api/knowledge')

# 全局服务实例（懒加载）
_knowledge_matcher = None
_subject_classifier = None

def get_knowledge_matcher():
    """获取知识匹配器实例"""
    global _knowledge_matcher
    if _knowledge_matcher is None and SERVICES_AVAILABLE:
        try:
            _knowledge_matcher = KnowledgeMatcher()
            logger.info("✅ 知识匹配器初始化成功")
        except Exception as e:
            logger.error(f"❌ 知识匹配器初始化失败: {e}")
            _knowledge_matcher = None
    return _knowledge_matcher

def get_subject_classifier():
    """获取学科分类器实例"""
    global _subject_classifier
    if _subject_classifier is None and SERVICES_AVAILABLE:
        try:
            _subject_classifier = SubjectClassifier()
            logger.info("✅ 学科分类器初始化成功")
        except Exception as e:
            logger.error(f"❌ 学科分类器初始化失败: {e}")
            _subject_classifier = None
    return _subject_classifier

# ========================================
# 核心API端点
# ========================================

@knowledge_api.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    start_time = time.time()
    
    status = {
        'service': 'knowledge_api',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'knowledge_matcher': get_knowledge_matcher() is not None,
            'subject_classifier': get_subject_classifier() is not None,
            'services_available': SERVICES_AVAILABLE
        }
    }
    
    processing_time = time.time() - start_time
    status['response_time_ms'] = round(processing_time * 1000, 2)
    
    return success_response(status)

@knowledge_api.route('/match', methods=['POST'])
def match_knowledge_points():
    """
    题目到知识点的智能匹配
    
    POST /api/knowledge/match
    {
        "text": "解一元一次方程：2x + 3 = 7",
        "top_k": 3,
        "use_ensemble": true,
        "subject_filter": "math"
    }
    """
    start_time = time.time()
    
    try:
        # 验证请求数据
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        text = data.get('text', '').strip()
        if not text:
            return error_response("文本内容不能为空", 400)
        
        top_k = data.get('top_k', 5)
        use_ensemble = data.get('use_ensemble', True)
        subject_filter = data.get('subject_filter')
        
        # 参数验证
        if top_k < 1 or top_k > 20:
            return error_response("top_k必须在1-20之间", 400)
        
        # 获取知识匹配器
        matcher = get_knowledge_matcher()
        if not matcher:
            return error_response("知识匹配服务不可用", 503)
        
        # 执行匹配
        if use_ensemble:
            matches = matcher.ensemble_match(text, top_k=top_k)
        else:
            # 使用单一方法匹配
            matches = matcher.match_by_keyword_rules(text, top_k=top_k)
            matches = [
                {
                    'rank': i + 1,
                    'knowledge_point_id': match[0],
                    'knowledge_point_name': match[2]['name'],
                    'confidence_score': round(match[1], 3),
                    'matching_methods': ['keyword'],
                    'knowledge_point_info': {
                        'difficulty': match[2].get('difficulty', 1),
                        'grade_level': match[2].get('grade_level', 7),
                        'keywords': match[2]['keywords']
                    }
                }
                for i, match in enumerate(matches)
            ]
        
        # 学科过滤
        if subject_filter:
            matches = [m for m in matches if subject_filter.lower() in m['knowledge_point_id'].lower()]
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result = {
            'text': text,
            'matches': matches,
            'total_matches': len(matches),
            'processing_time_ms': round(processing_time * 1000, 2),
            'parameters': {
                'top_k': top_k,
                'use_ensemble': use_ensemble,
                'subject_filter': subject_filter
            }
        }
        
        logger.info(f"知识点匹配完成: {len(matches)}个结果, 耗时{processing_time:.3f}秒")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"知识点匹配失败: {e}", exc_info=True)
        return error_response(f"知识点匹配失败: {str(e)}", 500)

@knowledge_api.route('/classify', methods=['POST'])
def classify_subject():
    """
    文本学科分类
    
    POST /api/knowledge/classify
    {
        "text": "计算三角形的面积",
        "use_ensemble": true
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        text = data.get('text', '').strip()
        if not text:
            return error_response("文本内容不能为空", 400)
        
        use_ensemble = data.get('use_ensemble', True)
        
        # 获取学科分类器
        classifier = get_subject_classifier()
        if not classifier:
            return error_response("学科分类服务不可用", 503)
        
        # 执行分类
        result = classifier.classify(text, use_ensemble=use_ensemble)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        result['processing_time_ms'] = round(processing_time * 1000, 2)
        
        logger.info(f"学科分类完成: {result['subject_name']}, 置信度{result['confidence']}")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"学科分类失败: {e}", exc_info=True)
        return error_response(f"学科分类失败: {str(e)}", 500)

@knowledge_api.route('/search', methods=['GET'])
def search_knowledge_points():
    """
    知识点搜索接口
    
    GET /api/knowledge/search?q=方程&subject=math&difficulty=2&limit=10
    """
    start_time = time.time()
    
    try:
        # 获取查询参数
        query = request.args.get('q', '').strip()
        subject = request.args.get('subject', '').strip()
        difficulty = request.args.get('difficulty', type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 参数验证
        if limit < 1 or limit > 100:
            return error_response("limit必须在1-100之间", 400)
        
        if offset < 0:
            return error_response("offset必须大于等于0", 400)
        
        # 获取知识匹配器
        matcher = get_knowledge_matcher()
        if not matcher:
            return error_response("知识搜索服务不可用", 503)
        
        # 构建搜索结果
        all_knowledge_points = []
        
        # 获取所有知识点
        for kp_id, kp_info in matcher.flat_knowledge_points.items():
            # 应用过滤条件
            if subject and subject.lower() not in kp_id.lower():
                continue
            
            if difficulty and kp_info.get('difficulty', 1) != difficulty:
                continue
            
            # 关键词搜索
            if query:
                text_to_search = f"{kp_info['name']} {' '.join(kp_info['keywords'])}".lower()
                if query.lower() not in text_to_search:
                    continue
            
            # 构建结果项
            item = {
                'knowledge_point_id': kp_id,
                'name': kp_info['name'],
                'difficulty': kp_info.get('difficulty', 1),
                'grade_level': kp_info.get('grade_level', 7),
                'keywords': kp_info['keywords'],
                'category_path': kp_id,
                'relevance_score': 1.0  # 默认相关度
            }
            
            # 如果有查询词，计算相关度
            if query:
                relevance = 0.0
                query_lower = query.lower()
                
                # 名称匹配（权重最高）
                if query_lower in kp_info['name'].lower():
                    relevance += 2.0
                
                # 关键词匹配
                for keyword in kp_info['keywords']:
                    if query_lower in keyword.lower():
                        relevance += 1.0
                
                item['relevance_score'] = relevance
            
            all_knowledge_points.append(item)
        
        # 按相关度排序
        all_knowledge_points.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 分页
        total_count = len(all_knowledge_points)
        paginated_results = all_knowledge_points[offset:offset + limit]
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result = {
            'query': query,
            'filters': {
                'subject': subject,
                'difficulty': difficulty
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_count': total_count,
                'has_more': offset + limit < total_count
            },
            'results': paginated_results,
            'processing_time_ms': round(processing_time * 1000, 2)
        }
        
        logger.info(f"知识点搜索完成: {len(paginated_results)}/{total_count}个结果")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"知识点搜索失败: {e}", exc_info=True)
        return error_response(f"知识点搜索失败: {str(e)}", 500)

@knowledge_api.route('/recommend', methods=['POST'])
def recommend_knowledge_points():
    """
    个性化知识点推荐
    
    POST /api/knowledge/recommend
    {
        "user_weak_points": ["math.algebra.linear_equations"],
        "difficulty_preference": 2,
        "limit": 10
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        user_weak_points = data.get('user_weak_points', [])
        difficulty_preference = data.get('difficulty_preference', 2)
        limit = data.get('limit', 10)
        
        # 参数验证
        if not isinstance(user_weak_points, list):
            return error_response("user_weak_points必须是列表", 400)
        
        if difficulty_preference < 1 or difficulty_preference > 5:
            return error_response("difficulty_preference必须在1-5之间", 400)
        
        if limit < 1 or limit > 50:
            return error_response("limit必须在1-50之间", 400)
        
        # 获取知识匹配器
        matcher = get_knowledge_matcher()
        if not matcher:
            return error_response("知识推荐服务不可用", 503)
        
        # 生成推荐
        recommendations = matcher.get_knowledge_point_recommendations(
            user_weak_points=user_weak_points,
            difficulty_preference=difficulty_preference,
            limit=limit
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result = {
            'user_weak_points': user_weak_points,
            'difficulty_preference': difficulty_preference,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'processing_time_ms': round(processing_time * 1000, 2)
        }
        
        logger.info(f"知识点推荐完成: {len(recommendations)}个推荐")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"知识点推荐失败: {e}", exc_info=True)
        return error_response(f"知识点推荐失败: {str(e)}", 500)

@knowledge_api.route('/analyze', methods=['POST'])
def analyze_question_difficulty():
    """
    题目难度分析
    
    POST /api/knowledge/analyze
    {
        "text": "解方程组：x+y=5, 2x-y=1",
        "context": "初二数学题"
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        text = data.get('text', '').strip()
        context = data.get('context', '').strip()
        
        if not text:
            return error_response("文本内容不能为空", 400)
        
        # 获取知识匹配器
        matcher = get_knowledge_matcher()
        if not matcher:
            return error_response("题目分析服务不可用", 503)
        
        # 先进行知识点匹配
        matches = matcher.ensemble_match(text, top_k=5)
        
        # 分析难度
        difficulty_analysis = matcher.analyze_question_difficulty(text, matches)
        
        # 学科分类（如果有分类器）
        subject_info = None
        classifier = get_subject_classifier()
        if classifier:
            subject_result = classifier.classify(text)
            subject_info = {
                'subject': subject_result['subject'],
                'subject_name': subject_result['subject_name'],
                'confidence': subject_result['confidence']
            }
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result = {
            'text': text,
            'context': context,
            'subject_classification': subject_info,
            'knowledge_point_matches': matches,
            'difficulty_analysis': difficulty_analysis,
            'processing_time_ms': round(processing_time * 1000, 2)
        }
        
        logger.info(f"题目分析完成: 难度等级{difficulty_analysis['difficulty_level']}")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"题目分析失败: {e}", exc_info=True)
        return error_response(f"题目分析失败: {str(e)}", 500)

@knowledge_api.route('/statistics', methods=['GET'])
def get_statistics():
    """
    获取知识库统计信息
    
    GET /api/knowledge/statistics
    """
    start_time = time.time()
    
    try:
        # 获取服务实例
        matcher = get_knowledge_matcher()
        classifier = get_subject_classifier()
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'services_status': {
                'knowledge_matcher_available': matcher is not None,
                'subject_classifier_available': classifier is not None,
                'services_module_available': SERVICES_AVAILABLE
            }
        }
        
        # 知识匹配器统计
        if matcher:
            matching_stats = matcher.get_matching_statistics()
            stats['knowledge_matcher'] = {
                'total_knowledge_points': len(matcher.flat_knowledge_points),
                'matching_statistics': matching_stats,
                'supported_subjects': list(set(kp_id.split('.')[0] for kp_id in matcher.flat_knowledge_points.keys()))
            }
        
        # 学科分类器统计
        if classifier:
            classification_stats = classifier.get_classification_stats()
            stats['subject_classifier'] = {
                'supported_subjects': list(classifier.subjects.keys()),
                'classification_statistics': classification_stats
            }
        
        # 计算处理时间
        processing_time = time.time() - start_time
        stats['processing_time_ms'] = round(processing_time * 1000, 2)
        
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        return error_response(f"获取统计信息失败: {str(e)}", 500)

@knowledge_api.route('/batch-match', methods=['POST'])
def batch_match_knowledge_points():
    """
    批量知识点匹配
    
    POST /api/knowledge/batch-match
    {
        "texts": ["题目1", "题目2", "题目3"],
        "top_k": 3,
        "use_ensemble": true
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)
        
        texts = data.get('texts', [])
        top_k = data.get('top_k', 3)
        use_ensemble = data.get('use_ensemble', True)
        
        # 参数验证
        if not isinstance(texts, list) or not texts:
            return error_response("texts必须是非空列表", 400)
        
        if len(texts) > 50:
            return error_response("批量处理最多支持50个文本", 400)
        
        if top_k < 1 or top_k > 10:
            return error_response("批量处理时top_k必须在1-10之间", 400)
        
        # 获取知识匹配器
        matcher = get_knowledge_matcher()
        if not matcher:
            return error_response("知识匹配服务不可用", 503)
        
        # 批量匹配
        if use_ensemble:
            batch_results = matcher.batch_match(texts, top_k=top_k)
        else:
            batch_results = []
            for text in texts:
                matches = matcher.match_by_keyword_rules(text, top_k=top_k)
                formatted_matches = [
                    {
                        'rank': i + 1,
                        'knowledge_point_id': match[0],
                        'knowledge_point_name': match[2]['name'],
                        'confidence_score': round(match[1], 3)
                    }
                    for i, match in enumerate(matches)
                ]
                batch_results.append(formatted_matches)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result = {
            'texts': texts,
            'results': [
                {
                    'text': text,
                    'matches': matches,
                    'match_count': len(matches)
                }
                for text, matches in zip(texts, batch_results)
            ],
            'total_processed': len(texts),
            'parameters': {
                'top_k': top_k,
                'use_ensemble': use_ensemble
            },
            'processing_time_ms': round(processing_time * 1000, 2),
            'avg_time_per_text_ms': round(processing_time * 1000 / len(texts), 2) if texts else 0
        }
        
        logger.info(f"批量知识点匹配完成: {len(texts)}个文本, 耗时{processing_time:.3f}秒")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"批量知识点匹配失败: {e}", exc_info=True)
        return error_response(f"批量知识点匹配失败: {str(e)}", 500)

# ========================================
# 管理接口
# ========================================

@knowledge_api.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        # 重新初始化服务实例
        global _knowledge_matcher, _subject_classifier
        _knowledge_matcher = None
        _subject_classifier = None
        
        logger.info("缓存清除成功")
        return success_response({
            'message': '缓存清除成功',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return error_response(f"清除缓存失败: {str(e)}", 500)

@knowledge_api.route('/reload', methods=['POST'])
def reload_services():
    """重新加载服务"""
    try:
        # 清除现有实例
        global _knowledge_matcher, _subject_classifier
        _knowledge_matcher = None
        _subject_classifier = None
        
        # 重新初始化
        matcher = get_knowledge_matcher()
        classifier = get_subject_classifier()
        
        result = {
            'message': '服务重新加载完成',
            'services_status': {
                'knowledge_matcher': matcher is not None,
                'subject_classifier': classifier is not None
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info("服务重新加载成功")
        return success_response(result)
        
    except Exception as e:
        logger.error(f"重新加载服务失败: {e}")
        return error_response(f"重新加载服务失败: {str(e)}", 500)

# ========================================
# 错误处理
# ========================================

@knowledge_api.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return error_response("API端点不存在", 404)

@knowledge_api.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return error_response("HTTP方法不允许", 405)

@knowledge_api.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"内部服务器错误: {error}")
    return error_response("内部服务器错误", 500)

# ========================================
# API信息
# ========================================

@knowledge_api.route('/info', methods=['GET'])
def api_info():
    """API信息"""
    return success_response({
        'name': 'Knowledge Base API',
        'version': '1.0.0',
        'description': '知识库管理API - 提供知识点匹配、搜索、推荐等功能',
        'endpoints': {
            'health': 'GET /api/knowledge/health - 健康检查',
            'match': 'POST /api/knowledge/match - 知识点匹配',
            'classify': 'POST /api/knowledge/classify - 学科分类',
            'search': 'GET /api/knowledge/search - 知识点搜索',
            'recommend': 'POST /api/knowledge/recommend - 知识点推荐',
            'analyze': 'POST /api/knowledge/analyze - 题目分析',
            'batch_match': 'POST /api/knowledge/batch-match - 批量匹配',
            'statistics': 'GET /api/knowledge/statistics - 统计信息'
        },
        'features': [
            '智能知识点匹配',
            '多维度搜索过滤',
            '个性化推荐',
            '学科自动分类',
            '题目难度分析',
            '批量处理支持',
            '性能监控'
        ]
    })

if __name__ == '__main__':
    # 简单测试
    print("🧪 知识库API端点模块测试")
    print("可用端点:")
    for rule in knowledge_api.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
