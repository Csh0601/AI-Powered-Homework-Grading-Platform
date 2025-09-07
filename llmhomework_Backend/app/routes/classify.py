#!/usr/bin/env python3
"""
学科分类API路由
提供题目学科智能分类服务
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.subject_classifier import SubjectClassifier
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

classify_bp = Blueprint('classify', __name__)

# 全局分类器实例（延迟初始化）
_classifier = None

def get_classifier():
    """获取分类器实例（单例模式）"""
    global _classifier
    if _classifier is None:
        try:
            _classifier = SubjectClassifier()
            logger.info("学科分类器初始化成功")
        except Exception as e:
            logger.error(f"学科分类器初始化失败: {e}")
            _classifier = None
    return _classifier

@classify_bp.route('/classify_text', methods=['POST'])
def classify_text():
    """
    对单个文本进行学科分类
    
    请求格式:
    {
        "text": "计算三角形的面积公式",
        "use_ensemble": true  // 可选，是否使用集成方法
    }
    
    响应格式:
    {
        "status": "success",
        "result": {
            "subject": "math",
            "subject_name": "数学",
            "confidence": 0.845,
            "method": "keyword",
            "details": {...}
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': '请提供要分类的文本内容'
            }), 400
        
        text = data['text']
        use_ensemble = data.get('use_ensemble', True)
        
        if not text or not text.strip():
            return jsonify({
                'status': 'error',
                'message': '文本内容不能为空'
            }), 400
        
        # 获取分类器
        classifier = get_classifier()
        if not classifier:
            return jsonify({
                'status': 'error',
                'message': '学科分类器不可用'
            }), 503
        
        # 执行分类
        start_time = time.time()
        result = classifier.classify(text, use_ensemble=use_ensemble)
        processing_time = time.time() - start_time
        
        # 构建响应
        response = {
            'status': 'success',
            'result': result,
            'processing_time': round(processing_time, 4),
            'timestamp': int(time.time())
        }
        
        logger.info(f"文本分类成功: {text[:50]}... -> {result['subject_name']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"文本分类失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'分类过程中发生错误: {str(e)}'
        }), 500

@classify_bp.route('/classify_batch', methods=['POST'])
def classify_batch():
    """
    批量文本学科分类
    
    请求格式:
    {
        "texts": [
            "计算三角形的面积公式",
            "分析鲁迅作品的艺术特色",
            "Translate the sentence"
        ],
        "use_ensemble": true  // 可选
    }
    
    响应格式:
    {
        "status": "success",
        "results": [
            {
                "index": 0,
                "text": "计算三角形的面积公式",
                "classification": {...}
            },
            ...
        ],
        "summary": {
            "total_count": 3,
            "processing_time": 0.125,
            "success_count": 3,
            "error_count": 0
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'texts' not in data:
            return jsonify({
                'status': 'error',
                'message': '请提供要分类的文本列表'
            }), 400
        
        texts = data['texts']
        use_ensemble = data.get('use_ensemble', True)
        
        if not isinstance(texts, list):
            return jsonify({
                'status': 'error',
                'message': 'texts字段必须是数组格式'
            }), 400
        
        if len(texts) == 0:
            return jsonify({
                'status': 'error',
                'message': '文本列表不能为空'
            }), 400
        
        if len(texts) > 100:  # 限制批量处理数量
            return jsonify({
                'status': 'error',
                'message': '批量处理最多支持100个文本'
            }), 400
        
        # 获取分类器
        classifier = get_classifier()
        if not classifier:
            return jsonify({
                'status': 'error',
                'message': '学科分类器不可用'
            }), 503
        
        # 批量分类
        start_time = time.time()
        results = []
        success_count = 0
        error_count = 0
        
        for index, text in enumerate(texts):
            try:
                if text and text.strip():
                    classification = classifier.classify(text, use_ensemble=use_ensemble)
                    results.append({
                        'index': index,
                        'text': text,
                        'classification': classification,
                        'status': 'success'
                    })
                    success_count += 1
                else:
                    results.append({
                        'index': index,
                        'text': text,
                        'classification': None,
                        'status': 'error',
                        'error': '文本内容为空'
                    })
                    error_count += 1
            except Exception as e:
                results.append({
                    'index': index,
                    'text': text,
                    'classification': None,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        processing_time = time.time() - start_time
        
        # 构建响应
        response = {
            'status': 'success',
            'results': results,
            'summary': {
                'total_count': len(texts),
                'success_count': success_count,
                'error_count': error_count,
                'processing_time': round(processing_time, 4),
                'average_time_per_text': round(processing_time / len(texts), 4)
            },
            'timestamp': int(time.time())
        }
        
        logger.info(f"批量分类完成: {len(texts)}个文本, 成功{success_count}个")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"批量分类失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'批量分类过程中发生错误: {str(e)}'
        }), 500

@classify_bp.route('/classifier_info', methods=['GET'])
def get_classifier_info():
    """
    获取分类器信息和统计
    
    响应格式:
    {
        "status": "success",
        "info": {
            "available": true,
            "version": "1.0.0",
            "supported_subjects": {...},
            "statistics": {...}
        }
    }
    """
    try:
        classifier = get_classifier()
        
        if not classifier:
            return jsonify({
                'status': 'success',
                'info': {
                    'available': False,
                    'message': '分类器不可用'
                }
            })
        
        # 获取分类器信息
        info = {
            'available': True,
            'version': '1.0.0',
            'supported_subjects': classifier.subjects,
            'classification_methods': ['keyword', 'rule', 'textcnn', 'ensemble'],
            'statistics': classifier.get_classification_stats(),
            'timestamp': int(time.time())
        }
        
        return jsonify({
            'status': 'success',
            'info': info
        })
        
    except Exception as e:
        logger.error(f"获取分类器信息失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取分类器信息时发生错误: {str(e)}'
        }), 500

@classify_bp.route('/test_classification', methods=['GET'])
def test_classification():
    """
    测试分类器功能
    
    响应格式:
    {
        "status": "success",
        "test_results": [
            {
                "text": "测试文本",
                "expected": "math",
                "predicted": "math",
                "correct": true,
                "confidence": 0.85
            },
            ...
        ],
        "summary": {
            "total_tests": 10,
            "correct_predictions": 8,
            "accuracy": 0.8
        }
    }
    """
    try:
        classifier = get_classifier()
        
        if not classifier:
            return jsonify({
                'status': 'error',
                'message': '分类器不可用'
            }), 503
        
        # 简单测试用例
        test_cases = [
            {'text': '计算三角形的面积', 'expected': 'math'},
            {'text': '分析古诗词的意境', 'expected': 'chinese'},
            {'text': 'Grammar exercise about tenses', 'expected': 'english'},
            {'text': '电路图分析', 'expected': 'physics'},
            {'text': '化学方程式配平', 'expected': 'chemistry'},
            {'text': '细胞分裂过程', 'expected': 'biology'},
            {'text': '历史事件分析', 'expected': 'history'},
            {'text': '地理位置特征', 'expected': 'geography'},
            {'text': '政治制度研究', 'expected': 'politics'}
        ]
        
        test_results = []
        correct_count = 0
        
        for test_case in test_cases:
            result = classifier.classify(test_case['text'])
            predicted = result['subject']
            expected = test_case['expected']
            is_correct = predicted == expected
            
            if is_correct:
                correct_count += 1
            
            test_results.append({
                'text': test_case['text'],
                'expected': expected,
                'predicted': predicted,
                'correct': is_correct,
                'confidence': result['confidence'],
                'method': result['method']
            })
        
        accuracy = correct_count / len(test_cases)
        
        response = {
            'status': 'success',
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_cases),
                'correct_predictions': correct_count,
                'accuracy': round(accuracy, 3),
                'timestamp': int(time.time())
            }
        }
        
        logger.info(f"分类器测试完成: 准确率 {accuracy:.1%}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"分类器测试失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'测试过程中发生错误: {str(e)}'
        }), 500

@classify_bp.route('/update_classifier', methods=['POST'])
def update_classifier():
    """
    更新分类器（重新初始化）
    
    响应格式:
    {
        "status": "success",
        "message": "分类器更新成功"
    }
    """
    try:
        global _classifier
        _classifier = None  # 清除现有实例
        
        # 重新初始化
        new_classifier = get_classifier()
        
        if new_classifier:
            return jsonify({
                'status': 'success',
                'message': '分类器更新成功',
                'timestamp': int(time.time())
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '分类器更新失败'
            }), 500
            
    except Exception as e:
        logger.error(f"更新分类器失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'更新过程中发生错误: {str(e)}'
        }), 500
