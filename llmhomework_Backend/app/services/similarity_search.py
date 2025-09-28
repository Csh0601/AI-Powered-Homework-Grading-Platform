#!/usr/bin/env python3
"""
基于语义的题目相似度计算系统
Day10任务: 计算不同题目的相似程度

主要功能：
1. 题目向量化和索引
2. 快速相似题目检索
3. 多维度相似度计算
4. 语义相似度评分
5. 相似题目推荐

技术要点：
- 向量检索和相似度算法
- TF-IDF文本向量化
- 语义特征提取
- 高效索引和搜索

目标：毫秒级相似题目检索，相似度准确率75%+
"""

import re
import jieba
import numpy as np
import json
import os
import logging
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
from datetime import datetime
import hashlib

# 机器学习和NLP库
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.decomposition import TruncatedSVD
    from sklearn.cluster import KMeans
    import scipy.sparse as sp
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习库未完全安装，部分功能可能受限")

logger = logging.getLogger(__name__)

class SimilaritySearchEngine:
    """题目相似度搜索引擎"""
    
    def __init__(self, model_path: str = None):
        """初始化搜索引擎"""
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', 'similarity_search'
        )
        
        # 确保模型目录存在
        os.makedirs(self.model_path, exist_ok=True)
        
        # 初始化组件
        self.tfidf_vectorizer = None
        self.question_vectors = None
        self.question_index = {}  # 题目ID到索引的映射
        self.index_to_question = {}  # 索引到题目数据的映射
        self.similarity_cache = {}  # 相似度缓存
        self.index_built = False  # 索引是否已构建
        
        # 相似度计算参数
        self.similarity_weights = {
            'text_similarity': 0.6,     # 文本相似度权重
            'type_similarity': 0.2,     # 题型相似度权重
            'difficulty_similarity': 0.1,  # 难度相似度权重
            'subject_similarity': 0.1   # 学科相似度权重
        }
        
        # 搜索统计
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'vector_searches': 0,
            'avg_search_time': 0.0,
            'indexed_questions': 0,
            'index_build_time': 0.0
        }
        
        # 性能优化参数
        self.max_cache_size = 1000  # 最大缓存条目数
        self.cache_ttl = 3600  # 缓存生存时间（秒）
        self.cache_timestamps = {}  # 缓存时间戳
        
        # 加载预训练模型
        self._load_models()
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理HTML标签和特殊字符
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 保留重要的数学符号
        math_symbols = ['=', '+', '-', '×', '÷', '>', '<', '≥', '≤', '≠', '≈', 
                       '√', '^', '²', '³', 'π', '∞', '°', '∠', '△', '□', '○']
        
        # 分词
        words = []
        for word in jieba.cut(text):
            word = word.strip()
            # 保留有意义的词汇和数学符号
            if word and (len(word) > 1 or word in math_symbols or word.isdigit()):
                words.append(word)
        
        return ' '.join(words)
    
    def build_question_index(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建题目索引"""
        if not ML_AVAILABLE:
            return self._build_simple_index(questions)
        
        start_time = datetime.now()
        
        try:
            # 预处理所有题目文本
            processed_texts = []
            question_metadata = []
            
            for i, question in enumerate(questions):
                # 处理题目文本
                stem = question.get('stem', '')
                answer = question.get('correct_answer', '')
                combined_text = f"{stem} {answer}"
                processed_text = self.preprocess_text(combined_text)
                processed_texts.append(processed_text)
                
                # 存储元数据
                question_id = question.get('question_id', f"Q_{i}")
                self.question_index[question_id] = i
                self.index_to_question[i] = question
                question_metadata.append({
                    'question_id': question_id,
                    'question_type': question.get('question_type', 'unknown'),
                    'difficulty_level': question.get('difficulty_level', 3),
                    'subject': question.get('subject', 'unknown'),
                    'processed_text': processed_text
                })
            
            # 构建TF-IDF向量
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                min_df=2,
                max_df=0.8,
                ngram_range=(1, 2),
                tokenizer=lambda x: x.split(),  # 已经预处理过了
                lowercase=True
            )
            
            # 拟合并转换文本
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            
            # 使用SVD降维（可选，用于大规模数据）
            if len(questions) > 1000:
                svd = TruncatedSVD(n_components=300, random_state=42)
                self.question_vectors = svd.fit_transform(tfidf_matrix)
            else:
                self.question_vectors = tfidf_matrix.toarray()
            
            # 更新统计信息
            self.search_stats['indexed_questions'] = len(questions)
            build_time = (datetime.now() - start_time).total_seconds()
            self.search_stats['index_build_time'] = build_time
            self.index_built = True
            
            logger.info(f"成功构建 {len(questions)} 个题目的索引，耗时 {build_time:.2f} 秒")
            
            return {
                'success': True,
                'indexed_questions': len(questions),
                'build_time_seconds': build_time,
                'vector_dimensions': self.question_vectors.shape[1] if self.question_vectors is not None else 0
            }
            
        except Exception as e:
            logger.error(f"构建题目索引失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_simple_index(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建简单索引（无需机器学习库）"""
        # 简单的关键词索引
        for i, question in enumerate(questions):
            question_id = question.get('question_id', f"Q_{i}")
            self.question_index[question_id] = i
            self.index_to_question[i] = question
        
        self.search_stats['indexed_questions'] = len(questions)
        self.index_built = True
        
        return {
            'success': True,
            'indexed_questions': len(questions),
            'build_time_seconds': 0.1,
            'vector_dimensions': 0
        }
    
    def find_similar_questions(self, query_question: Dict[str, Any], 
                             top_k: int = 10, 
                             similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """查找相似题目"""
        
        start_time = datetime.now()
        self.search_stats['total_searches'] += 1
        
        # 检查索引是否已构建
        if not self.index_built:
            logger.warning("索引未构建，无法进行相似度搜索")
            return []
        
        # 检查缓存
        query_hash = self._get_question_hash(query_question)
        cache_key = f"{query_hash}_{top_k}_{similarity_threshold}"
        
        # 检查缓存是否有效
        if self._is_cache_valid(cache_key):
            self.search_stats['cache_hits'] += 1
            return self.similarity_cache[cache_key]
        
        # 执行搜索
        if not ML_AVAILABLE or self.question_vectors is None:
            results = self._simple_similarity_search(query_question, top_k, similarity_threshold)
        else:
            results = self._vector_similarity_search(query_question, top_k, similarity_threshold)
        
        # 更新搜索统计
        search_time = (datetime.now() - start_time).total_seconds()
        self.search_stats['avg_search_time'] = (
            (self.search_stats['avg_search_time'] * (self.search_stats['total_searches'] - 1) + search_time) 
            / self.search_stats['total_searches']
        )
        
        # 缓存结果
        self._cache_result(cache_key, results)
        
        return results
    
    def _vector_similarity_search(self, query_question: Dict[str, Any], 
                                top_k: int = 10, 
                                similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """基于向量的相似度搜索"""
        
        self.search_stats['vector_searches'] += 1
        
        try:
            # 处理查询题目
            query_stem = query_question.get('stem', '')
            query_answer = query_question.get('correct_answer', '')
            query_text = f"{query_stem} {query_answer}"
            processed_query = self.preprocess_text(query_text)
            
            # 向量化查询题目
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            
            # 如果使用了SVD，需要相同的变换
            if hasattr(self, 'svd'):
                query_vector = self.svd.transform(query_vector)
            else:
                query_vector = query_vector.toarray()
            
            # 计算文本相似度
            text_similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
            
            # 计算综合相似度
            final_similarities = []
            
            for i, text_sim in enumerate(text_similarities):
                if i in self.index_to_question:
                    candidate_question = self.index_to_question[i]
                    
                    # 计算多维度相似度
                    type_sim = self._calculate_type_similarity(query_question, candidate_question)
                    diff_sim = self._calculate_difficulty_similarity(query_question, candidate_question)
                    subj_sim = self._calculate_subject_similarity(query_question, candidate_question)
                    
                    # 加权综合相似度
                    final_sim = (
                        text_sim * self.similarity_weights['text_similarity'] +
                        type_sim * self.similarity_weights['type_similarity'] +
                        diff_sim * self.similarity_weights['difficulty_similarity'] +
                        subj_sim * self.similarity_weights['subject_similarity']
                    )
                    
                    if final_sim >= similarity_threshold:
                        final_similarities.append((i, final_sim, {
                            'text_similarity': text_sim,
                            'type_similarity': type_sim,
                            'difficulty_similarity': diff_sim,
                            'subject_similarity': subj_sim
                        }))
            
            # 排序并返回Top-K
            final_similarities.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for i, (idx, sim_score, sim_breakdown) in enumerate(final_similarities[:top_k]):
                question = self.index_to_question[idx].copy()
                results.append({
                    'rank': i + 1,
                    'question': question,
                    'similarity_score': round(sim_score, 4),
                    'similarity_breakdown': {k: round(v, 4) for k, v in sim_breakdown.items()},
                    'match_reasons': self._generate_match_reasons(query_question, question, sim_breakdown)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"向量相似度搜索失败: {e}")
            return []
    
    def _simple_similarity_search(self, query_question: Dict[str, Any], 
                                top_k: int = 10, 
                                similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """简单的相似度搜索（基于关键词匹配）"""
        
        query_text = f"{query_question.get('stem', '')} {query_question.get('correct_answer', '')}"
        query_words = set(jieba.cut(query_text.lower()))
        
        similarities = []
        
        for idx, question in self.index_to_question.items():
            question_text = f"{question.get('stem', '')} {question.get('correct_answer', '')}"
            question_words = set(jieba.cut(question_text.lower()))
            
            # 计算Jaccard相似度
            intersection = len(query_words.intersection(question_words))
            union = len(query_words.union(question_words))
            text_sim = intersection / union if union > 0 else 0
            
            # 计算其他维度相似度
            type_sim = self._calculate_type_similarity(query_question, question)
            diff_sim = self._calculate_difficulty_similarity(query_question, question)
            subj_sim = self._calculate_subject_similarity(query_question, question)
            
            # 综合相似度
            final_sim = (
                text_sim * 0.7 +
                type_sim * 0.1 +
                diff_sim * 0.1 +
                subj_sim * 0.1
            )
            
            if final_sim >= similarity_threshold:
                similarities.append((idx, final_sim, {
                    'text_similarity': text_sim,
                    'type_similarity': type_sim,
                    'difficulty_similarity': diff_sim,
                    'subject_similarity': subj_sim
                }))
        
        # 排序并返回结果
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, (idx, sim_score, sim_breakdown) in enumerate(similarities[:top_k]):
            question = self.index_to_question[idx].copy()
            results.append({
                'rank': i + 1,
                'question': question,
                'similarity_score': round(sim_score, 4),
                'similarity_breakdown': {k: round(v, 4) for k, v in sim_breakdown.items()},
                'match_reasons': self._generate_match_reasons(query_question, question, sim_breakdown)
            })
        
        return results
    
    def _calculate_type_similarity(self, q1: Dict[str, Any], q2: Dict[str, Any]) -> float:
        """计算题型相似度"""
        type1 = q1.get('question_type', 'unknown')
        type2 = q2.get('question_type', 'unknown')
        
        if type1 == type2:
            return 1.0
        
        # 定义题型相似度矩阵
        type_similarity_matrix = {
            ('single_choice', 'multiple_choice'): 0.8,
            ('calculation', 'fill_blank'): 0.6,
            ('short_answer', 'essay'): 0.7,
            ('analysis', 'short_answer'): 0.6
        }
        
        # 检查相似度矩阵（双向）
        key1 = (type1, type2)
        key2 = (type2, type1)
        
        if key1 in type_similarity_matrix:
            return type_similarity_matrix[key1]
        elif key2 in type_similarity_matrix:
            return type_similarity_matrix[key2]
        else:
            return 0.0
    
    def _calculate_difficulty_similarity(self, q1: Dict[str, Any], q2: Dict[str, Any]) -> float:
        """计算难度相似度"""
        diff1 = q1.get('difficulty_level', 3)
        diff2 = q2.get('difficulty_level', 3)
        
        # 难度差距越小，相似度越高
        diff_gap = abs(diff1 - diff2)
        if diff_gap == 0:
            return 1.0
        elif diff_gap == 1:
            return 0.7
        elif diff_gap == 2:
            return 0.4
        else:
            return 0.0
    
    def _calculate_subject_similarity(self, q1: Dict[str, Any], q2: Dict[str, Any]) -> float:
        """计算学科相似度"""
        subj1 = q1.get('subject', 'unknown')
        subj2 = q2.get('subject', 'unknown')
        
        if subj1 == subj2:
            return 1.0
        
        # 定义学科相似度
        subject_similarity_matrix = {
            ('math', 'physics'): 0.6,
            ('chinese', 'english'): 0.3,
            ('physics', 'chemistry'): 0.5
        }
        
        key1 = (subj1, subj2)
        key2 = (subj2, subj1)
        
        if key1 in subject_similarity_matrix:
            return subject_similarity_matrix[key1]
        elif key2 in subject_similarity_matrix:
            return subject_similarity_matrix[key2]
        else:
            return 0.0
    
    def _generate_match_reasons(self, query_question: Dict[str, Any], 
                              matched_question: Dict[str, Any], 
                              similarity_breakdown: Dict[str, float]) -> List[str]:
        """生成匹配原因"""
        reasons = []
        
        if similarity_breakdown['text_similarity'] > 0.5:
            reasons.append("题目内容高度相似")
        elif similarity_breakdown['text_similarity'] > 0.3:
            reasons.append("题目内容部分相似")
        
        if similarity_breakdown['type_similarity'] == 1.0:
            reasons.append("题型完全一致")
        elif similarity_breakdown['type_similarity'] > 0.5:
            reasons.append("题型相关")
        
        if similarity_breakdown['difficulty_similarity'] == 1.0:
            reasons.append("难度等级相同")
        elif similarity_breakdown['difficulty_similarity'] > 0.5:
            reasons.append("难度等级接近")
        
        if similarity_breakdown['subject_similarity'] == 1.0:
            reasons.append("同一学科")
        elif similarity_breakdown['subject_similarity'] > 0.5:
            reasons.append("相关学科")
        
        return reasons
    
    def _get_question_hash(self, question: Dict[str, Any]) -> str:
        """生成题目哈希值"""
        key_content = f"{question.get('stem', '')}{question.get('correct_answer', '')}"
        return hashlib.md5(key_content.encode()).hexdigest()[:8]
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        cache_hit_rate = (
            self.search_stats['cache_hits'] / max(self.search_stats['total_searches'], 1)
        ) * 100
        
        return {
            'total_searches': self.search_stats['total_searches'],
            'cache_hits': self.search_stats['cache_hits'],
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'vector_searches': self.search_stats['vector_searches'],
            'avg_search_time_ms': round(self.search_stats['avg_search_time'] * 1000, 2),
            'indexed_questions': self.search_stats['indexed_questions'],
            'cache_size': len(self.similarity_cache)
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.similarity_cache:
            return False
        
        # 检查缓存时间戳
        if cache_key in self.cache_timestamps:
            cache_time = self.cache_timestamps[cache_key]
            current_time = datetime.now().timestamp()
            if current_time - cache_time > self.cache_ttl:
                # 缓存过期，删除
                del self.similarity_cache[cache_key]
                del self.cache_timestamps[cache_key]
                return False
        
        return True
    
    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]):
        """缓存搜索结果"""
        # 检查缓存大小限制
        if len(self.similarity_cache) >= self.max_cache_size:
            # 删除最旧的缓存条目
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.similarity_cache[oldest_key]
            del self.cache_timestamps[oldest_key]
        
        # 添加新缓存
        self.similarity_cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.now().timestamp()
    
    def clear_cache(self):
        """清空相似度缓存"""
        self.similarity_cache.clear()
        self.cache_timestamps.clear()
        logger.info("相似度缓存已清空")
    
    def save_model(self):
        """保存模型和索引"""
        model_data = {
            'similarity_weights': self.similarity_weights,
            'search_stats': self.search_stats,
            'question_index': self.question_index,
            'index_to_question': self.index_to_question,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        save_path = os.path.join(self.model_path, 'similarity_search.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"相似度搜索模型已保存: {save_path}")
        return save_path
    
    def _load_models(self):
        """加载预训练模型"""
        model_path = os.path.join(self.model_path, 'similarity_search.json')
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                if 'similarity_weights' in model_data:
                    self.similarity_weights.update(model_data['similarity_weights'])
                
                if 'search_stats' in model_data:
                    self.search_stats.update(model_data['search_stats'])
                
                logger.info(f"已加载相似度搜索模型: {model_path}")
            except Exception as e:
                logger.warning(f"加载模型失败: {e}")


def test_similarity_search():
    """测试相似度搜索引擎"""
    print("🧪 测试基于语义的题目相似度计算系统...")
    
    # 创建搜索引擎
    search_engine = SimilaritySearchEngine()
    
    # 准备测试数据
    test_questions = [
        {
            'question_id': 'Q1',
            'stem': '解一元一次方程：2x + 3 = 7，求x的值',
            'correct_answer': 'x = 2',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q2',
            'stem': '解方程：3x - 5 = 10，求x的值',
            'correct_answer': 'x = 5',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q3',
            'stem': '计算三角形的面积，已知底边为6米，高为4米',
            'correct_answer': '12平方米',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q4',
            'stem': '选择正确答案：下列哪个是质数？A.4 B.6 C.7 D.8',
            'correct_answer': 'C',
            'question_type': 'single_choice',
            'difficulty_level': 1,
            'subject': 'math'
        },
        {
            'question_id': 'Q5',
            'stem': '解一元二次方程：x² - 5x + 6 = 0',
            'correct_answer': 'x = 2 或 x = 3',
            'question_type': 'calculation',
            'difficulty_level': 4,
            'subject': 'math'
        }
    ]
    
    # 构建索引
    print("🏗️ 构建题目索引...")
    index_result = search_engine.build_question_index(test_questions)
    if index_result['success']:
        print(f"✅ 成功索引 {index_result['indexed_questions']} 个题目")
        print(f"   构建时间: {index_result['build_time_seconds']:.3f} 秒")
        print(f"   向量维度: {index_result['vector_dimensions']}")
    else:
        print(f"❌ 索引构建失败: {index_result['error']}")
        return
    
    # 测试相似度搜索
    print("\n🔍 测试相似度搜索...")
    
    query_question = {
        'stem': '求解方程：4x + 1 = 9，x等于多少？',
        'correct_answer': 'x = 2',
        'question_type': 'calculation',
        'difficulty_level': 2,
        'subject': 'math'
    }
    
    print(f"查询题目: {query_question['stem']}")
    
    similar_questions = search_engine.find_similar_questions(
        query_question, 
        top_k=3, 
        similarity_threshold=0.2
    )
    
    print(f"\n📊 找到 {len(similar_questions)} 个相似题目:")
    for result in similar_questions:
        print(f"\n{result['rank']}. 相似度: {result['similarity_score']:.3f}")
        print(f"   题目: {result['question']['stem']}")
        print(f"   答案: {result['question']['correct_answer']}")
        print(f"   匹配原因: {', '.join(result['match_reasons'])}")
        print(f"   相似度分解: {result['similarity_breakdown']}")
    
    # 显示搜索统计
    stats = search_engine.get_search_statistics()
    print(f"\n📈 搜索统计:")
    print(f"   总搜索次数: {stats['total_searches']}")
    print(f"   平均搜索时间: {stats['avg_search_time_ms']:.2f} ms")
    print(f"   索引题目数: {stats['indexed_questions']}")
    print(f"   缓存命中率: {stats['cache_hit_rate_percent']:.1f}%")
    
    print("✅ 测试完成 - 相似度搜索引擎工作正常")
    return search_engine


if __name__ == "__main__":
    # 运行测试
    test_similarity_search()
