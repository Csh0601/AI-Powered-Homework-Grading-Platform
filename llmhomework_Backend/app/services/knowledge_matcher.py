#!/usr/bin/env python3
"""
题目到知识点的智能匹配算法
基于TF-IDF关键词匹配和词向量语义相似度计算

主要功能：
1. TF-IDF关键词匹配算法
2. 词向量语义相似度计算
3. 多标签分类机制
4. 知识点权重评分
5. 智能推荐系统

技术要点：
- 信息检索和语义匹配
- 多维度特征提取
- 机器学习分类
- 结果可解释性
"""

import re
import jieba
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
import json
import os
import logging
from datetime import datetime
import pickle

# 机器学习和NLP库
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.cluster import KMeans
    from sklearn.multiclass import MultiLabelBinarizer
    import gensim
    from gensim.models import Word2Vec
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习库未完全安装，部分功能可能受限")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeMatcher:
    """题目到知识点的智能匹配器"""
    
    def __init__(self, model_path: str = None):
        """初始化匹配器"""
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', 'knowledge_matcher'
        )
        
        # 确保模型目录存在
        os.makedirs(self.model_path, exist_ok=True)
        
        # 初始化组件
        self.tfidf_vectorizer = None
        self.word2vec_model = None
        self.knowledge_vectors = {}
        self.knowledge_keywords = {}
        self.label_binarizer = MultiLabelBinarizer() if ML_AVAILABLE else None
        
        # 预定义知识点体系
        self._init_knowledge_system()
        
        # 匹配统计
        self.matching_stats = {
            'total_matches': 0,
            'method_usage': {
                'tfidf': 0,
                'semantic': 0,
                'keyword': 0,
                'ensemble': 0
            },
            'accuracy_distribution': defaultdict(int),
            'knowledge_point_coverage': defaultdict(int)
        }
        
        # 尝试加载预训练模型
        self._load_models()
    
    def _init_knowledge_system(self):
        """初始化知识点体系"""
        self.knowledge_system = {
            'math': {
                'algebra': {
                    'linear_equations': {
                        'name': '一次方程',
                        'keywords': ['方程', '未知数', '解', '等式', '消元', '代入'],
                        'patterns': [r'解.*?方程', r'求.*?的值', r'设.*?为.*?'],
                        'difficulty': 2,
                        'grade_level': 7
                    },
                    'quadratic_equations': {
                        'name': '二次方程',
                        'keywords': ['二次方程', '判别式', '求根公式', '顶点', '开口'],
                        'patterns': [r'二次.*?方程', r'抛物线', r'开口.*?向'],
                        'difficulty': 3,
                        'grade_level': 8
                    },
                    'inequalities': {
                        'name': '不等式',
                        'keywords': ['不等式', '大于', '小于', '不等号', '解集'],
                        'patterns': [r'不等式.*?解', r'[>≥<≤]', r'解集'],
                        'difficulty': 2,
                        'grade_level': 7
                    }
                },
                'geometry': {
                    'triangles': {
                        'name': '三角形',
                        'keywords': ['三角形', '边长', '角度', '面积', '周长', '勾股定理'],
                        'patterns': [r'三角形.*?(面积|周长)', r'△', r'勾股定理'],
                        'difficulty': 2,
                        'grade_level': 7
                    },
                    'circles': {
                        'name': '圆',
                        'keywords': ['圆', '半径', '直径', '周长', '面积', '弧长'],
                        'patterns': [r'圆.*?(面积|周长)', r'半径.*?为', r'○'],
                        'difficulty': 3,
                        'grade_level': 8
                    },
                    'quadrilaterals': {
                        'name': '四边形',
                        'keywords': ['四边形', '矩形', '正方形', '平行四边形', '梯形'],
                        'patterns': [r'四边形', r'矩形.*?(面积|周长)', r'□'],
                        'difficulty': 2,
                        'grade_level': 7
                    }
                },
                'functions': {
                    'linear_functions': {
                        'name': '一次函数',
                        'keywords': ['一次函数', '斜率', '截距', '图像', '正比例'],
                        'patterns': [r'一次函数', r'y=.*?x', r'斜率'],
                        'difficulty': 3,
                        'grade_level': 8
                    },
                    'quadratic_functions': {
                        'name': '二次函数',
                        'keywords': ['二次函数', '抛物线', '顶点', '对称轴', '开口方向'],
                        'patterns': [r'二次函数', r'y=.*?x²', r'抛物线'],
                        'difficulty': 4,
                        'grade_level': 9
                    }
                }
            },
            'chinese': {
                'literature': {
                    'poetry': {
                        'name': '诗歌',
                        'keywords': ['诗歌', '韵律', '意象', '情感', '修辞', '古诗'],
                        'patterns': [r'诗歌.*?赏析', r'古诗.*?理解'],
                        'difficulty': 3,
                        'grade_level': 8
                    },
                    'prose': {
                        'name': '散文',
                        'keywords': ['散文', '抒情', '叙事', '描写', '议论'],
                        'patterns': [r'散文.*?分析', r'作者.*?情感'],
                        'difficulty': 3,
                        'grade_level': 8
                    }
                },
                'grammar': {
                    'sentence_structure': {
                        'name': '句式结构',
                        'keywords': ['主语', '谓语', '宾语', '定语', '状语', '补语'],
                        'patterns': [r'句子.*?成分', r'语法.*?分析'],
                        'difficulty': 2,
                        'grade_level': 7
                    }
                }
            },
            'physics': {
                'mechanics': {
                    'motion': {
                        'name': '运动学',
                        'keywords': ['速度', '加速度', '位移', '时间', '运动'],
                        'patterns': [r'速度.*?计算', r'运动.*?时间'],
                        'difficulty': 3,
                        'grade_level': 8
                    },
                    'force': {
                        'name': '力学',
                        'keywords': ['力', '重力', '摩擦力', '压力', '支持力'],
                        'patterns': [r'力.*?分析', r'受力.*?图'],
                        'difficulty': 3,
                        'grade_level': 8
                    }
                }
            }
        }
        
        # 扁平化知识点便于查找
        self.flat_knowledge_points = {}
        self._flatten_knowledge_system()
    
    def _flatten_knowledge_system(self):
        """扁平化知识点体系"""
        def traverse(node, path=""):
            for key, value in node.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict) and 'name' in value:
                    # 这是一个知识点
                    self.flat_knowledge_points[current_path] = value
                elif isinstance(value, dict):
                    # 这是一个分类，继续遍历
                    traverse(value, current_path)
        
        traverse(self.knowledge_system)
        
        logger.info(f"已加载 {len(self.flat_knowledge_points)} 个知识点")
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 保留重要的数学符号
        math_symbols = ['=', '+', '-', '×', '÷', '>', '<', '≥', '≤', '≠', '≈', 
                       '√', '^', '²', '³', 'π', '∞', '°', '∠', '△', '□', '○']
        
        # 分词并保留数学符号
        words = []
        for word in jieba.cut(text):
            word = word.strip()
            if word and (word.isalnum() or word in math_symbols or len(word) > 1):
                words.append(word)
        
        return ' '.join(words)
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """提取关键词"""
        if not ML_AVAILABLE:
            # 简单的关键词提取
            words = jieba.cut(text)
            word_freq = Counter(words)
            return [(word, freq) for word, freq in word_freq.most_common(top_k)]
        
        # 使用TF-IDF提取关键词
        if not hasattr(self, '_keyword_vectorizer'):
            self._keyword_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,
                tokenizer=lambda x: list(jieba.cut(x)),
                lowercase=True
            )
            
            # 构建语料库（使用知识点描述）
            corpus = []
            for kp_id, kp_info in self.flat_knowledge_points.items():
                corpus.append(' '.join(kp_info['keywords']))
            
            if corpus:
                self._keyword_vectorizer.fit(corpus)
        
        try:
            tfidf_matrix = self._keyword_vectorizer.transform([text])
            feature_names = self._keyword_vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # 获取Top-K关键词
            top_indices = np.argsort(scores)[-top_k:][::-1]
            keywords = [(feature_names[i], scores[i]) for i in top_indices if scores[i] > 0]
            
            return keywords
        except:
            # 降级到简单关键词提取
            words = jieba.cut(text)
            word_freq = Counter(words)
            return [(word, freq) for word, freq in word_freq.most_common(top_k)]
    
    def match_by_tfidf(self, question_text: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """基于TF-IDF的知识点匹配"""
        if not ML_AVAILABLE:
            return []
        
        try:
            # 预处理问题文本
            processed_text = self.preprocess_text(question_text)
            
            # 构建知识点语料库
            knowledge_corpus = []
            knowledge_ids = []
            
            for kp_id, kp_info in self.flat_knowledge_points.items():
                # 合并知识点的关键词、名称等信息
                kp_text = ' '.join([
                    kp_info['name'],
                    ' '.join(kp_info['keywords']),
                    ' '.join(kp_info.get('patterns', []))
                ])
                knowledge_corpus.append(kp_text)
                knowledge_ids.append(kp_id)
            
            if not knowledge_corpus:
                return []
            
            # 初始化TF-IDF向量化器
            vectorizer = TfidfVectorizer(
                tokenizer=lambda x: list(jieba.cut(x)),
                lowercase=True,
                max_features=1000
            )
            
            # 拟合语料库
            tfidf_matrix = vectorizer.fit_transform(knowledge_corpus + [processed_text])
            
            # 计算相似度
            question_vector = tfidf_matrix[-1]  # 最后一个是问题向量
            knowledge_vectors = tfidf_matrix[:-1]  # 前面的是知识点向量
            
            similarities = cosine_similarity(question_vector, knowledge_vectors).flatten()
            
            # 获取Top-K匹配结果
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # 设置最低相似度阈值
                    kp_id = knowledge_ids[idx]
                    kp_info = self.flat_knowledge_points[kp_id]
                    results.append((kp_id, similarities[idx], kp_info))
            
            # 更新统计
            self.matching_stats['method_usage']['tfidf'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"TF-IDF匹配失败: {e}")
            return []
    
    def match_by_semantic_similarity(self, question_text: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """基于语义相似度的知识点匹配"""
        if not ML_AVAILABLE:
            return self._simple_semantic_match(question_text, top_k)
        
        try:
            # 预处理文本
            processed_text = self.preprocess_text(question_text)
            question_words = processed_text.split()
            
            if not question_words:
                return []
            
            # 计算与每个知识点的语义相似度
            similarities = []
            
            for kp_id, kp_info in self.flat_knowledge_points.items():
                # 计算词汇重叠度
                kp_words = set(kp_info['keywords'] + [kp_info['name']])
                question_words_set = set(question_words)
                
                # Jaccard相似度
                intersection = len(kp_words.intersection(question_words_set))
                union = len(kp_words.union(question_words_set))
                jaccard_sim = intersection / union if union > 0 else 0
                
                # 关键词匹配度
                keyword_matches = sum(1 for word in question_words if word in kp_words)
                keyword_sim = keyword_matches / len(question_words) if question_words else 0
                
                # 综合相似度
                combined_sim = 0.6 * jaccard_sim + 0.4 * keyword_sim
                
                if combined_sim > 0.1:
                    similarities.append((kp_id, combined_sim, kp_info))
            
            # 排序并返回Top-K
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # 更新统计
            self.matching_stats['method_usage']['semantic'] += 1
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"语义相似度匹配失败: {e}")
            return []
    
    def _simple_semantic_match(self, question_text: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """简单的语义匹配（无需机器学习库）"""
        processed_text = self.preprocess_text(question_text).lower()
        question_words = set(processed_text.split())
        
        similarities = []
        
        for kp_id, kp_info in self.flat_knowledge_points.items():
            # 关键词匹配
            kp_keywords = set([word.lower() for word in kp_info['keywords']])
            
            # 计算匹配度
            matches = len(question_words.intersection(kp_keywords))
            total_keywords = len(kp_keywords)
            
            if matches > 0:
                similarity = matches / max(len(question_words), total_keywords)
                similarities.append((kp_id, similarity, kp_info))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def match_by_keyword_rules(self, question_text: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """基于关键词规则的匹配"""
        processed_text = self.preprocess_text(question_text).lower()
        
        matches = []
        
        for kp_id, kp_info in self.flat_knowledge_points.items():
            score = 0.0
            reasons = []
            
            # 关键词匹配
            for keyword in kp_info['keywords']:
                if keyword.lower() in processed_text:
                    score += 1.0
                    reasons.append(f"关键词:{keyword}")
            
            # 模式匹配
            for pattern in kp_info.get('patterns', []):
                if re.search(pattern, processed_text, re.IGNORECASE):
                    score += 1.5  # 模式匹配权重更高
                    reasons.append(f"模式:{pattern}")
            
            # 名称匹配
            if kp_info['name'].lower() in processed_text:
                score += 2.0  # 名称匹配权重最高
                reasons.append(f"名称:{kp_info['name']}")
            
            if score > 0:
                # 标准化评分
                normalized_score = min(score / 5.0, 1.0)  # 最高分限制为1.0
                
                # 添加额外信息
                kp_info_extended = kp_info.copy()
                kp_info_extended['match_reasons'] = reasons
                kp_info_extended['raw_score'] = score
                
                matches.append((kp_id, normalized_score, kp_info_extended))
        
        # 排序
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # 更新统计
        self.matching_stats['method_usage']['keyword'] += 1
        
        return matches[:top_k]
    
    def ensemble_match(self, question_text: str, top_k: int = 5, 
                      use_tfidf: bool = True, use_semantic: bool = True, 
                      use_keyword: bool = True) -> List[Dict[str, Any]]:
        """集成匹配算法"""
        all_matches = {}
        
        # 权重配置
        method_weights = {
            'tfidf': 0.4,
            'semantic': 0.3,
            'keyword': 0.3
        }
        
        # TF-IDF匹配
        if use_tfidf:
            tfidf_matches = self.match_by_tfidf(question_text, top_k * 2)
            for kp_id, score, kp_info in tfidf_matches:
                if kp_id not in all_matches:
                    all_matches[kp_id] = {
                        'kp_id': kp_id,
                        'kp_info': kp_info,
                        'scores': {},
                        'total_score': 0.0,
                        'methods': []
                    }
                all_matches[kp_id]['scores']['tfidf'] = score
                all_matches[kp_id]['methods'].append('tfidf')
        
        # 语义匹配
        if use_semantic:
            semantic_matches = self.match_by_semantic_similarity(question_text, top_k * 2)
            for kp_id, score, kp_info in semantic_matches:
                if kp_id not in all_matches:
                    all_matches[kp_id] = {
                        'kp_id': kp_id,
                        'kp_info': kp_info,
                        'scores': {},
                        'total_score': 0.0,
                        'methods': []
                    }
                all_matches[kp_id]['scores']['semantic'] = score
                all_matches[kp_id]['methods'].append('semantic')
        
        # 关键词匹配
        if use_keyword:
            keyword_matches = self.match_by_keyword_rules(question_text, top_k * 2)
            for kp_id, score, kp_info in keyword_matches:
                if kp_id not in all_matches:
                    all_matches[kp_id] = {
                        'kp_id': kp_id,
                        'kp_info': kp_info,
                        'scores': {},
                        'total_score': 0.0,
                        'methods': []
                    }
                all_matches[kp_id]['scores']['keyword'] = score
                all_matches[kp_id]['methods'].append('keyword')
        
        # 计算加权总分
        for match_data in all_matches.values():
            total_score = 0.0
            total_weight = 0.0
            
            for method, weight in method_weights.items():
                if method in match_data['scores']:
                    total_score += match_data['scores'][method] * weight
                    total_weight += weight
            
            if total_weight > 0:
                match_data['total_score'] = total_score / total_weight
            
            # 多方法一致性加成
            if len(match_data['methods']) > 1:
                consistency_bonus = 0.1 * (len(match_data['methods']) - 1)
                match_data['total_score'] = min(match_data['total_score'] + consistency_bonus, 1.0)
        
        # 排序并返回结果
        sorted_matches = sorted(all_matches.values(), key=lambda x: x['total_score'], reverse=True)
        
        # 格式化结果
        results = []
        for i, match in enumerate(sorted_matches[:top_k]):
            result = {
                'rank': i + 1,
                'knowledge_point_id': match['kp_id'],
                'knowledge_point_name': match['kp_info']['name'],
                'confidence_score': round(match['total_score'], 3),
                'matching_methods': match['methods'],
                'method_scores': {k: round(v, 3) for k, v in match['scores'].items()},
                'knowledge_point_info': {
                    'difficulty': match['kp_info'].get('difficulty', 1),
                    'grade_level': match['kp_info'].get('grade_level', 7),
                    'keywords': match['kp_info']['keywords'],
                    'category_path': match['kp_id']
                },
                'match_details': match['kp_info'].get('match_reasons', [])
            }
            results.append(result)
        
        # 更新统计
        self.matching_stats['total_matches'] += 1
        self.matching_stats['method_usage']['ensemble'] += 1
        
        for result in results:
            kp_id = result['knowledge_point_id']
            if kp_id not in self.matching_stats['knowledge_point_coverage']:
                self.matching_stats['knowledge_point_coverage'][kp_id] = 0
            self.matching_stats['knowledge_point_coverage'][kp_id] += 1
        
        return results
    
    def analyze_question_difficulty(self, question_text: str, matched_knowledge_points: List[Dict]) -> Dict[str, Any]:
        """分析题目难度"""
        if not matched_knowledge_points:
            return {'difficulty_level': 1, 'confidence': 0.0, 'explanation': '无法匹配到知识点'}
        
        # 基于匹配的知识点计算难度
        difficulties = []
        weights = []
        
        for kp in matched_knowledge_points:
            difficulty = kp['knowledge_point_info']['difficulty']
            confidence = kp['confidence_score']
            difficulties.append(difficulty)
            weights.append(confidence)
        
        # 加权平均难度
        if weights:
            weighted_difficulty = sum(d * w for d, w in zip(difficulties, weights)) / sum(weights)
        else:
            weighted_difficulty = sum(difficulties) / len(difficulties) if difficulties else 1
        
        # 文本复杂度分析
        text_complexity = self._analyze_text_complexity(question_text)
        
        # 综合难度评估
        final_difficulty = 0.7 * weighted_difficulty + 0.3 * text_complexity
        final_difficulty = max(1, min(5, round(final_difficulty)))
        
        return {
            'difficulty_level': int(final_difficulty),
            'confidence': sum(weights) / len(weights) if weights else 0.0,
            'explanation': f'基于{len(matched_knowledge_points)}个匹配知识点的难度分析',
            'text_complexity': text_complexity,
            'knowledge_point_difficulties': difficulties
        }
    
    def _analyze_text_complexity(self, text: str) -> float:
        """分析文本复杂度"""
        # 简单的文本复杂度指标
        word_count = len(text.split())
        char_count = len(text)
        
        # 复杂度评分（1-5）
        if word_count < 10:
            complexity = 1
        elif word_count < 20:
            complexity = 2
        elif word_count < 40:
            complexity = 3
        elif word_count < 80:
            complexity = 4
        else:
            complexity = 5
        
        # 基于字符数的调整
        if char_count > 200:
            complexity = min(5, complexity + 1)
        
        return float(complexity)
    
    def get_knowledge_point_recommendations(self, user_weak_points: List[str], 
                                          difficulty_preference: int = 2,
                                          limit: int = 10) -> List[Dict[str, Any]]:
        """基于薄弱知识点推荐相关练习内容"""
        recommendations = []
        
        for weak_point in user_weak_points:
            # 查找相关知识点
            if weak_point in self.flat_knowledge_points:
                kp_info = self.flat_knowledge_points[weak_point]
                
                # 生成推荐内容
                recommendation = {
                    'knowledge_point_id': weak_point,
                    'knowledge_point_name': kp_info['name'],
                    'difficulty_level': kp_info.get('difficulty', difficulty_preference),
                    'recommended_practice': self._generate_practice_suggestions(kp_info),
                    'prerequisite_points': self._find_prerequisite_points(weak_point),
                    'related_points': self._find_related_points(weak_point),
                    'learning_priority': self._calculate_learning_priority(kp_info, difficulty_preference)
                }
                recommendations.append(recommendation)
        
        # 按学习优先级排序
        recommendations.sort(key=lambda x: x['learning_priority'], reverse=True)
        
        return recommendations[:limit]
    
    def _generate_practice_suggestions(self, kp_info: Dict) -> List[str]:
        """生成练习建议"""
        suggestions = []
        
        # 基于知识点类型生成建议
        if 'equation' in kp_info['name'].lower():
            suggestions.extend([
                '多做不同类型的方程求解练习',
                '重点理解解题步骤和方法',
                '练习检验解的正确性'
            ])
        elif 'geometry' in kp_info.get('category', '').lower():
            suggestions.extend([
                '绘制几何图形帮助理解',
                '记忆相关公式和定理',
                '练习几何证明题'
            ])
        else:
            suggestions.extend([
                '加强基础概念理解',
                '多做相关练习题',
                '总结解题规律'
            ])
        
        return suggestions
    
    def _find_prerequisite_points(self, kp_id: str) -> List[str]:
        """查找前置知识点"""
        # 简单的前置关系推断（可以扩展为更复杂的图结构）
        prerequisites = []
        
        # 基于路径结构推断
        path_parts = kp_id.split('.')
        if len(path_parts) > 2:
            # 查找同一分类下的基础知识点
            base_path = '.'.join(path_parts[:-1])
            for other_kp_id, other_kp_info in self.flat_knowledge_points.items():
                if (other_kp_id.startswith(base_path) and 
                    other_kp_id != kp_id and
                    other_kp_info.get('difficulty', 5) < self.flat_knowledge_points[kp_id].get('difficulty', 1)):
                    prerequisites.append(other_kp_id)
        
        return prerequisites[:3]  # 最多返回3个前置知识点
    
    def _find_related_points(self, kp_id: str) -> List[str]:
        """查找相关知识点"""
        related = []
        current_kp = self.flat_knowledge_points[kp_id]
        
        # 基于关键词相似度查找相关知识点
        current_keywords = set(current_kp['keywords'])
        
        for other_kp_id, other_kp_info in self.flat_knowledge_points.items():
            if other_kp_id != kp_id:
                other_keywords = set(other_kp_info['keywords'])
                # 计算关键词重叠度
                overlap = len(current_keywords.intersection(other_keywords))
                if overlap >= 2:  # 至少有2个关键词重叠
                    related.append(other_kp_id)
        
        return related[:5]  # 最多返回5个相关知识点
    
    def _calculate_learning_priority(self, kp_info: Dict, difficulty_preference: int) -> float:
        """计算学习优先级"""
        base_priority = 0.5
        
        # 难度匹配度
        difficulty_diff = abs(kp_info.get('difficulty', 2) - difficulty_preference)
        difficulty_score = max(0, 1 - difficulty_diff * 0.2)
        
        # 重要程度（可以基于考试频率等因素）
        importance_score = kp_info.get('exam_frequency', 0.5)
        
        # 综合优先级
        priority = base_priority + 0.3 * difficulty_score + 0.2 * importance_score
        
        return min(1.0, priority)
    
    def batch_match(self, questions: List[str], **kwargs) -> List[List[Dict[str, Any]]]:
        """批量匹配题目到知识点"""
        results = []
        for question in questions:
            matches = self.ensemble_match(question, **kwargs)
            results.append(matches)
        return results
    
    def get_matching_statistics(self) -> Dict[str, Any]:
        """获取匹配统计信息"""
        stats = self.matching_stats.copy()
        
        # 计算方法使用率
        total_matches = stats['total_matches']
        if total_matches > 0:
            # 创建新的method_usage字典避免修改原始数据
            new_method_usage = {}
            for method in stats['method_usage']:
                count = stats['method_usage'][method]
                percentage = (count / total_matches) * 100
                new_method_usage[method] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }
            stats['method_usage'] = new_method_usage
        
        # 添加知识点覆盖统计
        stats['knowledge_point_coverage_summary'] = {
            'total_knowledge_points': len(self.flat_knowledge_points),
            'covered_knowledge_points': len(stats['knowledge_point_coverage']),
            'coverage_rate': len(stats['knowledge_point_coverage']) / len(self.flat_knowledge_points) * 100
        }
        
        return stats
    
    def save_models(self):
        """保存模型和配置"""
        model_data = {
            'knowledge_system': self.knowledge_system,
            'flat_knowledge_points': self.flat_knowledge_points,
            'matching_stats': self.matching_stats,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        save_path = os.path.join(self.model_path, 'knowledge_matcher.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"知识匹配器模型已保存: {save_path}")
        return save_path
    
    def _load_models(self):
        """加载预训练模型"""
        model_path = os.path.join(self.model_path, 'knowledge_matcher.json')
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                if 'knowledge_system' in model_data:
                    self.knowledge_system = model_data['knowledge_system']
                    self._flatten_knowledge_system()
                
                if 'matching_stats' in model_data:
                    # 确保method_usage保持为整数计数器格式
                    saved_stats = model_data['matching_stats']
                    if 'method_usage' in saved_stats:
                        for method, value in saved_stats['method_usage'].items():
                            if isinstance(value, dict) and 'count' in value:
                                # 如果是字典格式，提取count值
                                self.matching_stats['method_usage'][method] = value['count']
                            else:
                                # 如果是整数格式，直接使用
                                self.matching_stats['method_usage'][method] = value
                    
                    # 更新其他统计信息
                    self.matching_stats['total_matches'] = saved_stats.get('total_matches', 0)
                    self.matching_stats['accuracy_distribution'] = saved_stats.get('accuracy_distribution', defaultdict(int))
                    self.matching_stats['knowledge_point_coverage'] = saved_stats.get('knowledge_point_coverage', defaultdict(int))
                
                logger.info(f"已加载知识匹配器模型: {model_path}")
            except Exception as e:
                logger.warning(f"加载模型失败: {e}")


def test_knowledge_matcher():
    """简单测试知识点匹配器"""
    print("🧪 测试知识点匹配算法...")
    
    matcher = KnowledgeMatcher()
    
    # 简单测试用例
    test_questions = [
        "解一元一次方程：2x + 3 = 7",
        "计算三角形的面积",
        "求二次函数的顶点坐标"
    ]
    
    for i, question in enumerate(test_questions, 1):
        matches = matcher.ensemble_match(question, top_k=2)
        print(f"{i}. {question}")
        if matches:
            for match in matches:
                print(f"   → {match['knowledge_point_name']} (置信度: {match['confidence_score']:.3f})")
        else:
            print("   → 未找到匹配")
    
    print("✅ 测试完成")
    return matcher


if __name__ == "__main__":
    # 运行测试
    test_knowledge_matcher()
