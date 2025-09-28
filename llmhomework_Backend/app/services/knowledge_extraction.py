#!/usr/bin/env python3
"""
高精度知识点提取系统
Day8任务: 基于BERT embeddings的语义提取，实现从题目中准确提取知识点标签

主要功能：
1. 基于BERT embeddings的语义提取
2. 知识点权重评分机制
3. 多知识点自动标注
4. 结合规则匹配和机器学习
5. 支持批量处理

技术要点：
- 深度学习和语义理解
- 多维度特征提取
- 机器学习分类
- 结果可解释性

目标：知识点提取准确率达80%+
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
import hashlib

# 机器学习和NLP库
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.multiclass import MultiLabelBinarizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import gensim
    from gensim.models import Word2Vec
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习库未完全安装，部分功能可能受限")

# BERT和深度学习库
try:
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import torch
    BERT_AVAILABLE = True
except ImportError as e:
    BERT_AVAILABLE = False
    print(f"⚠️ BERT/Transformers库未安装，语义提取功能将受限: {e}")
except Exception as e:
    BERT_AVAILABLE = False
    print(f"⚠️ BERT/Transformers库初始化失败，语义提取功能将受限: {e}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """高精度知识点提取器"""
    
    def __init__(self, model_path: str = None):
        """初始化提取器"""
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', 'knowledge_matcher'
        )
        
        # 确保模型目录存在
        os.makedirs(self.model_path, exist_ok=True)
        
        # 初始化组件
        self.tfidf_vectorizer = None
        self.word2vec_model = None
        self.ml_classifier = None
        self.label_encoder = MultiLabelBinarizer() if ML_AVAILABLE else None
        
        # BERT模型组件
        self.bert_tokenizer = None
        self.bert_model = None
        self.sentence_transformer = None
        self.knowledge_embeddings = None
        
        # 知识点体系和规则
        self._init_knowledge_rules()
        
        # 提取统计
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'method_accuracy': {
                'rule_based': [],
                'tfidf_based': [],
                'bert_based': [],
                'ensemble': []
            },
            'knowledge_point_frequency': defaultdict(int),
            'subject_distribution': defaultdict(int)
        }
        
        # 加载预训练模型
        self._load_models()
        
        # 初始化BERT模型
        self._init_bert_models()
    
    def _init_knowledge_rules(self):
        """初始化知识点规则库"""
        self.knowledge_rules = {
            # 数学学科规则
            'math': {
                'equations': {
                    'keywords': ['方程', '解', '求解', '未知数', '等式', '消元', '代入'],
                    'patterns': [
                        r'解.*?方程',
                        r'求.*?的值',
                        r'设.*?为.*?',
                        r'[xyz]\s*=',
                        r'\d+x\s*[+\-=]',
                        r'一元.*?方程',
                        r'二元.*?方程'
                    ],
                    'negative_patterns': [r'不等式', r'函数'],
                    'weight': 1.0,
                    'confidence_base': 0.8
                },
                'inequalities': {
                    'keywords': ['不等式', '大于', '小于', '不等号', '解集', '取值范围'],
                    'patterns': [
                        r'不等式.*?解',
                        r'[>≥<≤]',
                        r'解集',
                        r'取值范围',
                        r'满足.*?不等'
                    ],
                    'negative_patterns': [r'方程', r'等式'],
                    'weight': 1.0,
                    'confidence_base': 0.9
                },
                'geometry_triangle': {
                    'keywords': ['三角形', '边长', '角度', '面积', '周长', '勾股定理', '内角', '外角'],
                    'patterns': [
                        r'三角形.*?(面积|周长|边长)',
                        r'△.*?ABC',
                        r'勾股定理',
                        r'直角三角形',
                        r'等腰三角形',
                        r'等边三角形'
                    ],
                    'negative_patterns': [],
                    'weight': 1.2,
                    'confidence_base': 0.85
                },
                'geometry_circle': {
                    'keywords': ['圆', '半径', '直径', '周长', '面积', '弧长', '扇形'],
                    'patterns': [
                        r'圆.*?(面积|周长|半径|直径)',
                        r'半径.*?为',
                        r'○.*?[ABC]',
                        r'弧长',
                        r'扇形.*?面积'
                    ],
                    'negative_patterns': [],
                    'weight': 1.1,
                    'confidence_base': 0.85
                },
                'functions_linear': {
                    'keywords': ['一次函数', '斜率', '截距', '图像', '正比例', '反比例'],
                    'patterns': [
                        r'一次函数',
                        r'y\s*=.*?x',
                        r'斜率',
                        r'k.*?值',
                        r'函数.*?图像'
                    ],
                    'negative_patterns': [r'二次函数'],
                    'weight': 1.1,
                    'confidence_base': 0.8
                },
                'functions_quadratic': {
                    'keywords': ['二次函数', '抛物线', '顶点', '对称轴', '开口方向', '最值'],
                    'patterns': [
                        r'二次函数',
                        r'y\s*=.*?x²',
                        r'y\s*=.*?x\^2',
                        r'抛物线',
                        r'顶点.*?坐标',
                        r'对称轴'
                    ],
                    'negative_patterns': [r'一次函数'],
                    'weight': 1.3,
                    'confidence_base': 0.9
                }
            },
            
            # 语文学科规则
            'chinese': {
                'poetry_analysis': {
                    'keywords': ['诗歌', '韵律', '意象', '情感', '修辞', '古诗', '诗词', '赏析'],
                    'patterns': [
                        r'诗歌.*?赏析',
                        r'古诗.*?理解',
                        r'诗词.*?分析',
                        r'表达.*?情感',
                        r'修辞.*?手法'
                    ],
                    'negative_patterns': [r'散文', r'小说'],
                    'weight': 1.0,
                    'confidence_base': 0.8
                },
                'prose_analysis': {
                    'keywords': ['散文', '抒情', '叙事', '描写', '议论', '文章', '作者'],
                    'patterns': [
                        r'散文.*?分析',
                        r'作者.*?情感',
                        r'文章.*?主题',
                        r'描写.*?方法'
                    ],
                    'negative_patterns': [r'诗歌', r'古诗'],
                    'weight': 1.0,
                    'confidence_base': 0.75
                },
                'grammar': {
                    'keywords': ['主语', '谓语', '宾语', '定语', '状语', '补语', '句子', '成分'],
                    'patterns': [
                        r'句子.*?成分',
                        r'语法.*?分析',
                        r'主谓宾',
                        r'定状补'
                    ],
                    'negative_patterns': [],
                    'weight': 1.0,
                    'confidence_base': 0.85
                }
            },
            
            # 物理学科规则
            'physics': {
                'mechanics_motion': {
                    'keywords': ['速度', '加速度', '位移', '时间', '运动', '匀速', '变速'],
                    'patterns': [
                        r'速度.*?计算',
                        r'运动.*?时间',
                        r'位移.*?公式',
                        r'匀速.*?运动',
                        r'加速度.*?为'
                    ],
                    'negative_patterns': [],
                    'weight': 1.1,
                    'confidence_base': 0.8
                },
                'mechanics_force': {
                    'keywords': ['力', '重力', '摩擦力', '压力', '支持力', '合力', '分力'],
                    'patterns': [
                        r'力.*?分析',
                        r'受力.*?图',
                        r'重力.*?为',
                        r'摩擦力.*?大小',
                        r'合力.*?方向'
                    ],
                    'negative_patterns': [],
                    'weight': 1.1,
                    'confidence_base': 0.8
                }
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 保留重要的数学符号和标点
        important_symbols = ['=', '+', '-', '×', '÷', '>', '<', '≥', '≤', '≠', '≈', 
                           '√', '^', '²', '³', 'π', '∞', '°', '∠', '△', '□', '○', 
                           '(', ')', '[', ']', '{', '}', '，', '。', '？', '！']
        
        # 分词并保留重要符号
        words = []
        for word in jieba.cut(text):
            word = word.strip()
            if word and (word.isalnum() or word in important_symbols or len(word) > 1):
                words.append(word)
        
        return ' '.join(words)
    
    def extract_by_rules(self, question_text: str, subject_hint: str = None) -> List[Dict[str, Any]]:
        """基于规则的知识点提取"""
        processed_text = self.preprocess_text(question_text).lower()
        
        extractions = []
        
        # 确定搜索范围
        search_subjects = [subject_hint] if subject_hint and subject_hint in self.knowledge_rules else self.knowledge_rules.keys()
        
        for subject in search_subjects:
            subject_rules = self.knowledge_rules[subject]
            
            for knowledge_point, rules in subject_rules.items():
                score = 0.0
                matched_keywords = []
                matched_patterns = []
                
                # 关键词匹配
                for keyword in rules['keywords']:
                    if keyword.lower() in processed_text:
                        score += 1.0
                        matched_keywords.append(keyword)
                
                # 模式匹配
                for pattern in rules['patterns']:
                    if re.search(pattern, processed_text, re.IGNORECASE):
                        score += 1.5  # 模式匹配权重更高
                        matched_patterns.append(pattern)
                
                # 负模式检查（排除不相关的知识点）
                negative_match = False
                for neg_pattern in rules.get('negative_patterns', []):
                    if re.search(neg_pattern, processed_text, re.IGNORECASE):
                        negative_match = True
                        break
                
                # 计算置信度
                if score > 0 and not negative_match:
                    # 基础置信度
                    base_confidence = rules.get('confidence_base', 0.5)
                    
                    # 基于匹配强度调整置信度
                    keyword_bonus = min(len(matched_keywords) * 0.1, 0.3)
                    pattern_bonus = min(len(matched_patterns) * 0.15, 0.4)
                    
                    final_confidence = min(base_confidence + keyword_bonus + pattern_bonus, 1.0)
                    
                    # 应用权重
                    weighted_score = score * rules.get('weight', 1.0)
                    
                    extractions.append({
                        'knowledge_point': knowledge_point,
                        'subject': subject,
                        'confidence': round(final_confidence, 3),
                        'raw_score': score,
                        'weighted_score': weighted_score,
                        'matched_keywords': matched_keywords,
                        'matched_patterns': matched_patterns,
                        'extraction_method': 'rule_based'
                    })
        
        # 按置信度排序
        extractions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return extractions
    
    def extract_by_tfidf(self, question_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """基于TF-IDF的知识点提取"""
        if not ML_AVAILABLE:
            return []
        
        try:
            # 预处理文本
            processed_text = self.preprocess_text(question_text)
            
            # 构建知识点文档库
            knowledge_docs = []
            knowledge_labels = []
            
            for subject, subject_rules in self.knowledge_rules.items():
                for kp, rules in subject_rules.items():
                    # 合并关键词和模式作为文档
                    doc_text = ' '.join(rules['keywords'])
                    # 从模式中提取有意义的词汇
                    for pattern in rules['patterns']:
                        # 简单提取模式中的中文词汇
                        pattern_words = re.findall(r'[\u4e00-\u9fa5]+', pattern)
                        doc_text += ' ' + ' '.join(pattern_words)
                    
                    knowledge_docs.append(doc_text)
                    knowledge_labels.append((subject, kp))
            
            if not knowledge_docs:
                return []
            
            # 初始化TF-IDF向量化器
            if not hasattr(self, '_tfidf_extractor'):
                self._tfidf_extractor = TfidfVectorizer(
                    tokenizer=lambda x: list(jieba.cut(x)),
                    lowercase=True,
                    max_features=1000,
                    min_df=1,
                    max_df=0.95
                )
                # 拟合知识点文档
                self._tfidf_extractor.fit(knowledge_docs)
            
            # 计算相似度
            question_vector = self._tfidf_extractor.transform([processed_text])
            knowledge_vectors = self._tfidf_extractor.transform(knowledge_docs)
            
            similarities = cosine_similarity(question_vector, knowledge_vectors).flatten()
            
            # 获取Top-K结果
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            extractions = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # 最低相似度阈值
                    subject, kp = knowledge_labels[idx]
                    extractions.append({
                        'knowledge_point': kp,
                        'subject': subject,
                        'confidence': round(similarities[idx], 3),
                        'similarity_score': similarities[idx],
                        'extraction_method': 'tfidf_based'
                    })
            
            return extractions
            
        except Exception as e:
            logger.error(f"TF-IDF知识点提取失败: {e}")
            return []
    
    def extract_by_ensemble(self, question_text: str, subject_hint: str = None, 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """集成方法的知识点提取"""
        
        # 1. 基于规则的提取
        rule_extractions = self.extract_by_rules(question_text, subject_hint)
        
        # 2. 基于TF-IDF的提取
        tfidf_extractions = self.extract_by_tfidf(question_text, top_k * 2)
        
        # 3. 基于BERT的语义提取
        bert_extractions = self.extract_by_bert(question_text, top_k * 2)
        
        # 4. 合并结果
        combined_results = {}
        
        # 处理规则提取结果
        for extraction in rule_extractions:
            key = f"{extraction['subject']}.{extraction['knowledge_point']}"
            if key not in combined_results:
                combined_results[key] = {
                    'knowledge_point': extraction['knowledge_point'],
                    'subject': extraction['subject'],
                    'scores': {},
                    'methods': [],
                    'details': {}
                }
            
            combined_results[key]['scores']['rule_based'] = extraction['confidence']
            combined_results[key]['methods'].append('rule_based')
            combined_results[key]['details']['rule_based'] = {
                'matched_keywords': extraction.get('matched_keywords', []),
                'matched_patterns': extraction.get('matched_patterns', [])
            }
        
        # 处理TF-IDF提取结果
        for extraction in tfidf_extractions:
            key = f"{extraction['subject']}.{extraction['knowledge_point']}"
            if key not in combined_results:
                combined_results[key] = {
                    'knowledge_point': extraction['knowledge_point'],
                    'subject': extraction['subject'],
                    'scores': {},
                    'methods': [],
                    'details': {}
                }
            
            combined_results[key]['scores']['tfidf_based'] = extraction['confidence']
            combined_results[key]['methods'].append('tfidf_based')
            combined_results[key]['details']['tfidf_based'] = {
                'similarity_score': extraction.get('similarity_score', 0)
            }
        
        # 处理BERT提取结果
        for extraction in bert_extractions:
            key = f"{extraction['subject']}.{extraction['knowledge_point']}"
            if key not in combined_results:
                combined_results[key] = {
                    'knowledge_point': extraction['knowledge_point'],
                    'subject': extraction['subject'],
                    'scores': {},
                    'methods': [],
                    'details': {}
                }
            
            combined_results[key]['scores']['bert_based'] = extraction['confidence']
            combined_results[key]['methods'].append('bert_based')
            combined_results[key]['details']['bert_based'] = {
                'semantic_similarity': extraction.get('semantic_similarity', 0),
                'knowledge_description': extraction.get('knowledge_description', '')
            }
        
        # 5. 计算综合得分
        method_weights = {
            'rule_based': 0.4,    # 规则方法权重
            'tfidf_based': 0.2,   # TF-IDF作为补充
            'bert_based': 0.4     # BERT语义理解权重
        }
        
        final_extractions = []
        for key, data in combined_results.items():
            # 计算加权平均分
            total_score = 0.0
            total_weight = 0.0
            
            for method, weight in method_weights.items():
                if method in data['scores']:
                    total_score += data['scores'][method] * weight
                    total_weight += weight
            
            if total_weight > 0:
                avg_score = total_score / total_weight
                
                # 多方法一致性加成
                consistency_bonus = 0.1 * (len(data['methods']) - 1)
                final_score = min(avg_score + consistency_bonus, 1.0)
                
                final_extractions.append({
                    'knowledge_point': data['knowledge_point'],
                    'subject': data['subject'],
                    'confidence': round(final_score, 3),
                    'extraction_methods': data['methods'],
                    'method_scores': {k: round(v, 3) for k, v in data['scores'].items()},
                    'extraction_details': data['details'],
                    'consistency_score': len(data['methods'])
                })
        
        # 按置信度排序
        final_extractions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 更新统计
        self.extraction_stats['total_extractions'] += 1
        if final_extractions:
            self.extraction_stats['successful_extractions'] += 1
            for extraction in final_extractions[:top_k]:
                kp = extraction['knowledge_point']
                subject = extraction['subject']
                self.extraction_stats['knowledge_point_frequency'][kp] += 1
                self.extraction_stats['subject_distribution'][subject] += 1
        
        return final_extractions[:top_k]
    
    def batch_extract(self, questions: List[str], subject_hints: List[str] = None, 
                     top_k: int = 3) -> List[List[Dict[str, Any]]]:
        """批量知识点提取"""
        results = []
        subject_hints = subject_hints or [None] * len(questions)
        
        for i, question in enumerate(questions):
            subject_hint = subject_hints[i] if i < len(subject_hints) else None
            extractions = self.extract_by_ensemble(question, subject_hint, top_k)
            results.append(extractions)
        
        return results
    
    def evaluate_extraction_accuracy(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估提取准确性"""
        if not test_data:
            return {'error': '测试数据为空'}
        
        total_questions = len(test_data)
        correct_predictions = 0
        method_accuracies = defaultdict(list)
        
        for test_case in test_data:
            question = test_case['question']
            true_knowledge_points = set(test_case['knowledge_points'])
            subject_hint = test_case.get('subject')
            
            # 提取知识点
            extractions = self.extract_by_ensemble(question, subject_hint)
            predicted_knowledge_points = set([ext['knowledge_point'] for ext in extractions])
            
            # 计算准确性
            intersection = true_knowledge_points.intersection(predicted_knowledge_points)
            if intersection:
                accuracy = len(intersection) / len(true_knowledge_points)
                if accuracy >= 0.5:  # 至少50%匹配才算正确
                    correct_predictions += 1
                
                # 记录各方法的准确性
                for extraction in extractions:
                    if extraction['knowledge_point'] in true_knowledge_points:
                        for method in extraction['extraction_methods']:
                            method_accuracies[method].append(1.0)
                    else:
                        for method in extraction['extraction_methods']:
                            method_accuracies[method].append(0.0)
        
        # 计算总体准确率
        overall_accuracy = correct_predictions / total_questions
        
        # 计算各方法准确率
        method_accuracy_summary = {}
        for method, accuracies in method_accuracies.items():
            if accuracies:
                method_accuracy_summary[method] = {
                    'accuracy': np.mean(accuracies),
                    'samples': len(accuracies)
                }
        
        return {
            'overall_accuracy': overall_accuracy,
            'correct_predictions': correct_predictions,
            'total_questions': total_questions,
            'method_accuracies': method_accuracy_summary,
            'extraction_stats': self.extraction_stats
        }
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """获取提取统计信息"""
        stats = self.extraction_stats.copy()
        
        # 计算成功率
        if stats['total_extractions'] > 0:
            stats['success_rate'] = stats['successful_extractions'] / stats['total_extractions']
        else:
            stats['success_rate'] = 0.0
        
        # 知识点热度排行
        stats['top_knowledge_points'] = dict(
            sorted(stats['knowledge_point_frequency'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        # 学科分布
        stats['subject_distribution_summary'] = dict(stats['subject_distribution'])
        
        return stats
    
    def save_model(self):
        """保存模型和统计数据"""
        model_data = {
            'knowledge_rules': self.knowledge_rules,
            'extraction_stats': self.extraction_stats,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        save_path = os.path.join(self.model_path, 'knowledge_extractor.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"知识点提取器模型已保存: {save_path}")
        return save_path
    
    def _load_models(self):
        """加载预训练模型"""
        model_path = os.path.join(self.model_path, 'knowledge_extractor.json')
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                if 'knowledge_rules' in model_data:
                    self.knowledge_rules.update(model_data['knowledge_rules'])
                
                if 'extraction_stats' in model_data:
                    saved_stats = model_data['extraction_stats']
                    self.extraction_stats.update(saved_stats)
                
                logger.info(f"已加载知识点提取器模型: {model_path}")
            except Exception as e:
                logger.warning(f"加载模型失败: {e}")
    
    def _init_bert_models(self):
        """初始化BERT模型"""
        if not BERT_AVAILABLE:
            logger.warning("BERT库不可用，跳过BERT模型初始化")
            return
        
        try:
            # 使用轻量级的中文BERT模型
            model_name = "distilbert-base-multilingual-cased"
            
            # 初始化SentenceTransformer（更适合语义相似度计算）
            self.sentence_transformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ SentenceTransformer模型加载成功")
            
            # 预计算知识点embeddings
            self._precompute_knowledge_embeddings()
            
        except Exception as e:
            logger.error(f"BERT模型初始化失败: {e}")
            self.sentence_transformer = None
    
    def _precompute_knowledge_embeddings(self):
        """预计算知识点embeddings"""
        if not self.sentence_transformer:
            return
        
        try:
            knowledge_texts = []
            knowledge_labels = []
            
            for subject, subject_rules in self.knowledge_rules.items():
                for kp, rules in subject_rules.items():
                    # 构建知识点的文本描述
                    kp_text = f"{subject} {kp} {' '.join(rules['keywords'])}"
                    knowledge_texts.append(kp_text)
                    knowledge_labels.append((subject, kp))
            
            if knowledge_texts:
                # 计算embeddings
                self.knowledge_embeddings = self.sentence_transformer.encode(knowledge_texts)
                self.knowledge_labels = knowledge_labels
                logger.info(f"✅ 预计算了 {len(knowledge_texts)} 个知识点的embeddings")
            
        except Exception as e:
            logger.error(f"预计算知识点embeddings失败: {e}")
            self.knowledge_embeddings = None
    
    def extract_by_bert(self, question_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """基于BERT embeddings的语义提取"""
        if not BERT_AVAILABLE or not self.sentence_transformer or self.knowledge_embeddings is None:
            logger.warning("BERT模型不可用，跳过语义提取")
            return []
        
        try:
            # 预处理问题文本
            processed_text = self.preprocess_text(question_text)
            
            # 计算问题文本的embedding
            question_embedding = self.sentence_transformer.encode([processed_text])
            
            # 计算与所有知识点的相似度
            similarities = cosine_similarity(question_embedding, self.knowledge_embeddings).flatten()
            
            # 获取Top-K结果
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            extractions = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # 语义相似度阈值
                    subject, kp = self.knowledge_labels[idx]
                    
                    # 获取对应的规则信息
                    rules = self.knowledge_rules[subject][kp]
                    
                    extractions.append({
                        'knowledge_point': kp,
                        'subject': subject,
                        'confidence': round(similarities[idx], 3),
                        'semantic_similarity': similarities[idx],
                        'extraction_method': 'bert_based',
                        'knowledge_description': f"{subject} {kp} {' '.join(rules['keywords'])}"
                    })
            
            return extractions
            
        except Exception as e:
            logger.error(f"BERT语义提取失败: {e}")
            return []


def test_knowledge_extractor():
    """测试知识点提取器"""
    print("🧪 测试高精度知识点提取系统...")
    
    extractor = KnowledgeExtractor()
    
    # 测试用例
    test_questions = [
        {
            'question': '解一元一次方程：2x + 3 = 7，求x的值',
            'expected_subject': 'math',
            'expected_kp': ['equations']
        },
        {
            'question': '已知三角形ABC的三边长分别为3、4、5，求该三角形的面积',
            'expected_subject': 'math',
            'expected_kp': ['geometry_triangle']
        },
        {
            'question': '已知二次函数y = x² - 2x + 1，求其顶点坐标和对称轴',
            'expected_subject': 'math',
            'expected_kp': ['functions_quadratic']
        },
        {
            'question': '分析《春晓》这首古诗中诗人表达的情感和运用的意象',
            'expected_subject': 'chinese',
            'expected_kp': ['poetry_analysis']
        },
        {
            'question': '一物体以10m/s的初速度做匀加速运动，加速度为2m/s²，求5秒后的速度',
            'expected_subject': 'physics',
            'expected_kp': ['mechanics_motion']
        }
    ]
    
    print(f"测试 {len(test_questions)} 个问题...")
    
    for i, test_case in enumerate(test_questions, 1):
        question = test_case['question']
        expected_subject = test_case['expected_subject']
        
        print(f"\n{i}. {question}")
        
        # 提取知识点
        extractions = extractor.extract_by_ensemble(question, expected_subject, top_k=3)
        
        if extractions:
            print("   提取结果:")
            for j, extraction in enumerate(extractions, 1):
                print(f"   {j}. {extraction['knowledge_point']} ({extraction['subject']})")
                print(f"      置信度: {extraction['confidence']:.3f}")
                print(f"      方法: {', '.join(extraction['extraction_methods'])}")
                
                # 显示各方法得分
                if 'method_scores' in extraction:
                    scores = extraction['method_scores']
                    score_str = ', '.join([f"{method}: {score:.3f}" for method, score in scores.items()])
                    print(f"      各方法得分: {score_str}")
        else:
            print("   → 未提取到知识点")
    
    # 显示统计信息
    stats = extractor.get_extraction_statistics()
    print(f"\n📊 提取统计:")
    print(f"   总提取次数: {stats['total_extractions']}")
    print(f"   成功提取次数: {stats['successful_extractions']}")
    print(f"   成功率: {stats['success_rate']:.2%}")
    
    if stats['top_knowledge_points']:
        print(f"   热门知识点: {list(stats['top_knowledge_points'].keys())[:3]}")
    
    print("✅ 测试完成")
    return extractor


if __name__ == "__main__":
    # 运行测试
    test_knowledge_extractor()
