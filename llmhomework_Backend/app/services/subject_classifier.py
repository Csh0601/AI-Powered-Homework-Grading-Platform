#!/usr/bin/env python3
"""
智能学科分类器
基于文本内容自动识别题目所属学科

主要功能：
1. 基于关键词和规则的分类
2. TextCNN深度学习分类模型
3. 分类置信度评估
4. 多层级分类策略

支持学科：
- 数学 (math)
- 语文 (chinese) 
- 英语 (english)
- 物理 (physics)
- 化学 (chemistry)
- 生物 (biology)
- 历史 (history)
- 地理 (geography)
- 政治 (politics)
"""

import re
import jieba
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter, defaultdict
import pickle
import os
import json
from datetime import datetime
import logging

# 深度学习相关
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import classification_report, confusion_matrix
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False
    print("⚠️ 深度学习库未安装，仅使用规则分类")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def jieba_tokenizer(text):
    """独立的分词函数，用于TfidfVectorizer"""
    return list(jieba.cut(text))

class SubjectClassifier:
    """智能学科分类器"""
    
    def __init__(self, model_path: str = None):
        """初始化分类器"""
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', 'subject_classifier'
        )
        
        # 确保模型目录存在
        os.makedirs(self.model_path, exist_ok=True)
        
        # 学科定义
        self.subjects = {
            'math': '数学',
            'chinese': '语文', 
            'english': '英语',
            'physics': '物理',
            'chemistry': '化学',
            'biology': '生物',
            'history': '历史',
            'geography': '地理',
            'politics': '政治'
        }
        
        # 初始化分类器组件
        self._init_keyword_classifier()
        self._init_rule_patterns()
        
        # 深度学习模型
        self.textcnn_model = None
        self.vectorizer = None
        self.label_encoder = None
        
        # 尝试加载已训练的TextCNN模型
        self._load_textcnn_model()
        
        # 分类统计
        self.classification_stats = {
            'total_classifications': 0,
            'method_usage': {
                'keyword': 0,
                'rule': 0,
                'textcnn': 0,
                'ensemble': 0,
                'fallback': 0
            },
            'confidence_distribution': defaultdict(int)
        }
    
    def _init_keyword_classifier(self):
        """初始化关键词分类器"""
        self.subject_keywords = {
            'math': {
                # 基础数学概念
                'basic': ['数学', '计算', '代数', '几何', '函数', '方程', '不等式', '概率', '统计'],
                # 运算符号
                'operators': ['加', '减', '乘', '除', '等于', '大于', '小于', '平方', '开方', '绝对值'],
                # 几何图形
                'geometry': ['三角形', '四边形', '圆', '正方形', '长方形', '平行四边形', '梯形', 
                           '点', '线', '面', '角', '弧', '半径', '直径', '周长', '面积', '体积'],
                # 代数概念
                'algebra': ['未知数', '系数', '常数', '变量', '解', '根', '因式分解', '配方'],
                # 数字和单位
                'numbers': ['整数', '分数', '小数', '百分比', '比例', '率'],
                # 特殊符号识别
                'symbols': ['π', '∞', '°', '∠', '△', '□', '○', '≈', '≠', '≤', '≥']
            },
            
            'chinese': {
                'literary': ['文学', '诗歌', '散文', '小说', '戏剧', '古诗', '现代文', '文言文'],
                'grammar': ['语法', '词汇', '句式', '修辞', '语言', '文字', '汉字', '拼音'],
                'writing': ['作文', '写作', '表达', '阅读', '理解', '分析', '鉴赏'],
                'classical': ['古代', '文言', '诗词', '唐诗', '宋词', '元曲', '古文'],
                'authors': ['鲁迅', '老舍', '巴金', '茅盾', '沈从文', '朱自清', '冰心']
            },
            
            'english': {
                'grammar': ['grammar', 'tense', 'verb', 'noun', 'adjective', 'adverb'],
                'vocabulary': ['vocabulary', 'word', 'phrase', 'idiom', 'expression'],
                'skills': ['reading', 'writing', 'listening', 'speaking', 'translation'],
                'basic': ['english', '英语', '英文', '单词', '语法', '时态', '句型']
            },
            
            'physics': {
                'mechanics': ['力学', '运动', '速度', '加速度', '力', '质量', '重力', '摩擦'],
                'electricity': ['电学', '电流', '电压', '电阻', '功率', '电路', '磁场'],
                'optics': ['光学', '光线', '反射', '折射', '透镜', '凸透镜', '凹透镜'],
                'thermodynamics': ['热学', '温度', '热量', '比热容', '内能', '热机'],
                'units': ['牛顿', '焦耳', '瓦特', '安培', '伏特', '欧姆', '米/秒']
            },
            
            'chemistry': {
                'elements': ['元素', '原子', '分子', '离子', '质子', '中子', '电子'],
                'compounds': ['化合物', '氧化物', '酸', '碱', '盐', '有机物', '无机物'],
                'reactions': ['化学反应', '氧化', '还原', '燃烧', '中和', '电解'],
                'formulas': ['化学式', '分子式', '离子方程式', '化学方程式'],
                'common': ['氢', '氧', '碳', '氮', '硫', '磷', '氯', '钠', '钾', '钙', '铁']
            },
            
            'biology': {
                'cells': ['细胞', '细胞膜', '细胞壁', '细胞核', '细胞质', '线粒体'],
                'organisms': ['生物', '植物', '动物', '微生物', '细菌', '病毒'],
                'systems': ['消化系统', '呼吸系统', '循环系统', '神经系统', '内分泌系统'],
                'genetics': ['遗传', '基因', 'DNA', 'RNA', '染色体', '性状'],
                'ecology': ['生态', '环境', '生态系统', '食物链', '食物网']
            },
            
            'history': {
                'periods': ['古代', '近代', '现代', '朝代', '王朝', '帝国', '共和'],
                'events': ['战争', '革命', '改革', '起义', '运动', '条约', '协定'],
                'figures': ['皇帝', '将军', '政治家', '思想家', '文学家'],
                'chronology': ['年代', '世纪', '公元', '历史', '史学', '史料']
            },
            
            'geography': {
                'physical': ['地理', '地形', '地貌', '山脉', '河流', '湖泊', '海洋', '平原'],
                'climate': ['气候', '温度', '降水', '风', '季节', '气温', '湿度'],
                'regions': ['亚洲', '欧洲', '非洲', '美洲', '大洋洲', '中国', '省份'],
                'resources': ['资源', '矿产', '石油', '煤炭', '水资源', '土地']
            },
            
            'politics': {
                'concepts': ['政治', '国家', '政府', '法律', '宪法', '权利', '义务'],
                'systems': ['民主', '专制', '共和', '联邦', '议会', '选举'],
                'ideology': ['马克思主义', '社会主义', '资本主义', '思想', '理论'],
                'current': ['时事', '政策', '外交', '国际关系', '联合国']
            }
        }
    
    def _init_rule_patterns(self):
        """初始化规则模式"""
        self.rule_patterns = {
            'math': [
                r'计算.*?的值',
                r'求.*?的.*?(面积|周长|体积|长度)',
                r'解.*?方程',
                r'证明.*?(三角形|四边形|圆)',
                r'\d+[+\-×÷]\d+',
                r'设.*?为.*?，求',
                r'已知.*?求.*?',
                r'函数.*?的.*?(定义域|值域|单调性)',
                r'概率.*?是多少'
            ],
            
            'chinese': [
                r'阅读.*?文章',
                r'分析.*?(人物|情节|主题)',
                r'诗歌.*?(赏析|理解)',
                r'文言文.*?翻译',
                r'作者.*?(想要表达|情感)',
                r'修辞.*?手法',
                r'语言.*?特色'
            ],
            
            'english': [
                r'translate.*?into',
                r'choose.*?correct.*?answer',
                r'complete.*?sentences?',
                r'what.*?does.*?mean',
                r'grammar.*?exercise',
                r'vocabulary.*?test'
            ],
            
            'physics': [
                r'物体.*?运动',
                r'电路.*?图',
                r'光.*?(反射|折射)',
                r'力.*?作用',
                r'能量.*?转换',
                r'温度.*?变化'
            ],
            
            'chemistry': [
                r'化学.*?方程式',
                r'元素.*?化合价',
                r'反应.*?产物',
                r'溶液.*?浓度',
                r'气体.*?体积',
                r'原子.*?结构'
            ],
            
            'biology': [
                r'细胞.*?结构',
                r'生物.*?特征',
                r'遗传.*?规律',
                r'生态.*?系统',
                r'器官.*?功能',
                r'进化.*?过程'
            ],
            
            'history': [
                r'\d+年.*?事件',
                r'历史.*?意义',
                r'朝代.*?更替',
                r'战争.*?结果',
                r'改革.*?影响',
                r'文化.*?交流'
            ],
            
            'geography': [
                r'地理.*?位置',
                r'气候.*?特征',
                r'地形.*?特点',
                r'资源.*?分布',
                r'人口.*?分布',
                r'经济.*?发展'
            ],
            
            'politics': [
                r'政治.*?制度',
                r'法律.*?条文',
                r'权利.*?义务',
                r'国家.*?性质',
                r'政府.*?职能',
                r'民主.*?制度'
            ]
        }
    
    def classify_by_keywords(self, text: str) -> Tuple[str, float]:
        """基于关键词分类"""
        text = text.lower()
        scores = defaultdict(float)
        
        for subject, categories in self.subject_keywords.items():
            for category, keywords in categories.items():
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    count = text.count(keyword_lower)
                    if count > 0:
                        # 根据关键词类别给予不同权重
                        weight = self._get_keyword_weight(category)
                        scores[subject] += count * weight
        
        if not scores:
            return 'unknown', 0.0
        
        best_subject = max(scores, key=scores.get)
        # 计算置信度（基于最高分与次高分的差距）
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
        else:
            confidence = scores[best_subject] / (scores[best_subject] + 1)
        
        confidence = min(confidence, 0.95)  # 最大置信度限制
        return best_subject, confidence
    
    def classify_by_rules(self, text: str) -> Tuple[str, float]:
        """基于规则模式分类"""
        scores = defaultdict(int)
        
        for subject, patterns in self.rule_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                scores[subject] += len(matches)
        
        if not scores:
            return 'unknown', 0.0
        
        best_subject = max(scores, key=scores.get)
        max_score = scores[best_subject]
        total_score = sum(scores.values())
        
        confidence = max_score / total_score if total_score > 0 else 0.0
        confidence = min(confidence, 0.90)  # 规则分类的最大置信度
        
        return best_subject, confidence
    
    def _get_keyword_weight(self, category: str) -> float:
        """获取关键词类别权重"""
        weights = {
            'basic': 1.0,
            'operators': 1.2,
            'geometry': 1.1,
            'algebra': 1.1,
            'symbols': 1.5,
            'literary': 1.2,
            'grammar': 1.0,
            'classical': 1.3,
            'mechanics': 1.2,
            'electricity': 1.2,
            'elements': 1.3,
            'compounds': 1.1,
            'cells': 1.2,
            'organisms': 1.0,
            'periods': 1.1,
            'events': 1.2,
            'physical': 1.1,
            'climate': 1.2,
            'concepts': 1.0,
            'systems': 1.1
        }
        return weights.get(category, 1.0)
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 移除标点符号和特殊字符（保留数学符号）
        math_symbols = ['π', '∞', '°', '∠', '△', '□', '○', '≈', '≠', '≤', '≥', '+', '-', '×', '÷', '=']
        
        # 标准化文本
        text = re.sub(r'\s+', ' ', text)  # 统一空白字符
        text = text.strip()
        
        # 分词
        words = jieba.cut(text)
        processed_text = ' '.join(words)
        
        return processed_text
    
    def classify(self, text: str, use_ensemble: bool = True) -> Dict[str, Any]:
        """
        主分类方法
        
        Args:
            text: 待分类文本
            use_ensemble: 是否使用集成方法
            
        Returns:
            分类结果字典
        """
        if not text or not text.strip():
            return {
                'subject': 'unknown',
                'confidence': 0.0,
                'method': 'fallback',
                'details': {'error': '文本为空'}
            }
        
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 分类结果
        results = {}
        
        # 1. 关键词分类
        keyword_subject, keyword_conf = self.classify_by_keywords(processed_text)
        results['keyword'] = (keyword_subject, keyword_conf)
        
        # 2. 规则分类
        rule_subject, rule_conf = self.classify_by_rules(processed_text)
        results['rule'] = (rule_subject, rule_conf)
        
        # 3. TextCNN分类（如果模型可用）
        if DEEP_LEARNING_AVAILABLE and self.textcnn_model:
            try:
                textcnn_subject, textcnn_conf = self.classify_by_textcnn(processed_text)
                results['textcnn'] = (textcnn_subject, textcnn_conf)
            except Exception as e:
                logger.warning(f"TextCNN分类失败: {e}")
                results['textcnn'] = ('unknown', 0.0)
        else:
            results['textcnn'] = ('unknown', 0.0)
        
        # 4. 集成决策
        if use_ensemble:
            final_subject, final_confidence, method = self._ensemble_decision(results)
        else:
            # 使用最高置信度的结果
            best_result = max(results.items(), key=lambda x: x[1][1])
            final_subject, final_confidence = best_result[1]
            method = best_result[0]
        
        # 更新统计信息
        self.classification_stats['total_classifications'] += 1
        self.classification_stats['method_usage'][method] += 1
        self.classification_stats['confidence_distribution'][round(final_confidence, 1)] += 1
        
        return {
            'subject': final_subject,
            'subject_name': self.subjects.get(final_subject, '未知'),
            'confidence': round(final_confidence, 3),
            'method': method,
            'details': {
                'keyword': {'subject': results['keyword'][0], 'confidence': round(results['keyword'][1], 3)},
                'rule': {'subject': results['rule'][0], 'confidence': round(results['rule'][1], 3)},
                'textcnn': {'subject': results['textcnn'][0], 'confidence': round(results['textcnn'][1], 3)},
                'text_length': len(text),
                'processed_length': len(processed_text)
            }
        }
    
    def _load_textcnn_model(self):
        """加载已训练的TextCNN模型"""
        if not DEEP_LEARNING_AVAILABLE:
            return
        
        try:
            import pickle
            import torch
            
            model_dir = os.path.join(self.model_path, '..', '..', 'models', 'subject_classifier')
            model_path = os.path.join(model_dir, 'textcnn_model.pth')
            vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
            label_encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
            
            if all(os.path.exists(p) for p in [model_path, vectorizer_path, label_encoder_path]):
                # 加载向量化器和标签编码器
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                with open(label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                
                # 初始化模型结构
                vocab_size = 5000
                embed_dim = 128
                num_classes = len(self.label_encoder.classes_)
                
                self.textcnn_model = TextCNN(
                    vocab_size=vocab_size,
                    embed_dim=embed_dim,
                    num_classes=num_classes,
                    kernel_sizes=[3, 4, 5],
                    num_filters=100
                )
                
                # 加载模型权重
                self.textcnn_model.load_state_dict(torch.load(model_path, map_location='cpu'))
                self.textcnn_model.eval()
                
                logger.info("✅ TextCNN模型加载成功")
            else:
                logger.info("⚠️ TextCNN模型文件不存在，需要先训练模型")
        
        except Exception as e:
            logger.warning(f"TextCNN模型加载失败: {e}")
            self.textcnn_model = None
            self.vectorizer = None
            self.label_encoder = None
    
    def classify_by_textcnn(self, text: str) -> Tuple[str, float]:
        """使用TextCNN模型分类"""
        if not DEEP_LEARNING_AVAILABLE or not self.textcnn_model or not self.vectorizer:
            return 'unknown', 0.0
        
        try:
            import torch
            import numpy as np
            
            # 文本向量化
            text_vector = self.vectorizer.transform([text]).toarray()[0]
            
            # 转换为序列（取前128个最重要的特征）
            max_length = 128
            sequence = np.argsort(text_vector)[-max_length:][::-1].copy()  # 添加.copy()解决负步长问题
            
            # 填充或截断到固定长度
            if len(sequence) < max_length:
                sequence = np.pad(sequence, (0, max_length - len(sequence)), 'constant', constant_values=0)
            
            # 转换为tensor并预测
            input_tensor = torch.tensor(sequence, dtype=torch.long).unsqueeze(0)
            
            with torch.no_grad():
                output = self.textcnn_model(input_tensor)
                probabilities = torch.softmax(output, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
                
                # 转换回学科标签
                predicted_label = self.label_encoder.inverse_transform([predicted_idx.item()])[0]
                confidence_score = confidence.item()
                
                return predicted_label, confidence_score
        
        except Exception as e:
            logger.error(f"TextCNN分类错误: {e}")
            return 'unknown', 0.0

    def _ensemble_decision(self, results: Dict[str, Tuple[str, float]]) -> Tuple[str, float, str]:
        """集成决策算法"""
        # 方法权重
        method_weights = {
            'keyword': 0.4,
            'rule': 0.3,
            'textcnn': 0.3
        }
        
        # 计算加权分数
        subject_scores = defaultdict(float)
        total_weight = 0
        
        for method, (subject, confidence) in results.items():
            if subject != 'unknown' and confidence > 0:
                weight = method_weights.get(method, 0)
                subject_scores[subject] += confidence * weight
                total_weight += weight
        
        if not subject_scores:
            return 'unknown', 0.0, 'fallback'
        
        # 找出最高分学科
        best_subject = max(subject_scores, key=subject_scores.get)
        best_score = subject_scores[best_subject]
        
        # 计算最终置信度
        if total_weight > 0:
            final_confidence = best_score / total_weight
        else:
            final_confidence = 0.0
        
        # 确定主要贡献方法
        main_method = 'ensemble'
        for method, (subject, confidence) in results.items():
            if subject == best_subject and confidence > 0.5:
                main_method = method
                break
        
        return best_subject, final_confidence, main_method
    
    def batch_classify(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量分类"""
        results = []
        for text in texts:
            result = self.classify(text)
            results.append(result)
        return results
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """获取分类统计信息"""
        stats = self.classification_stats.copy()
        
        if stats['total_classifications'] > 0:
            for method in stats['method_usage']:
                percentage = (stats['method_usage'][method] / stats['total_classifications']) * 100
                stats['method_usage'][method] = {
                    'count': stats['method_usage'][method],
                    'percentage': round(percentage, 2)
                }
        
        return stats
    
    def save_model(self, model_name: str = 'subject_classifier'):
        """保存分类器模型"""
        model_data = {
            'subjects': self.subjects,
            'subject_keywords': self.subject_keywords,
            'rule_patterns': self.rule_patterns,
            'classification_stats': self.classification_stats,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        save_path = os.path.join(self.model_path, f'{model_name}.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分类器模型已保存: {save_path}")
        return save_path
    
    def load_model(self, model_name: str = 'subject_classifier'):
        """加载分类器模型"""
        load_path = os.path.join(self.model_path, f'{model_name}.json')
        
        if not os.path.exists(load_path):
            logger.warning(f"模型文件不存在: {load_path}")
            return False
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            self.subjects = model_data['subjects']
            self.subject_keywords = model_data['subject_keywords']
            self.rule_patterns = model_data['rule_patterns']
            self.classification_stats = model_data.get('classification_stats', self.classification_stats)
            
            logger.info(f"分类器模型已加载: {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return False


# TextCNN模型实现（如果深度学习库可用）
if DEEP_LEARNING_AVAILABLE:
    class TextCNN(nn.Module):
        """TextCNN模型用于文本分类"""
        
        def __init__(self, vocab_size: int, embed_dim: int, num_classes: int, 
                     kernel_sizes: List[int] = [3, 4, 5], num_filters: int = 100):
            super(TextCNN, self).__init__()
            
            self.embedding = nn.Embedding(vocab_size, embed_dim)
            self.convs = nn.ModuleList([
                nn.Conv1d(embed_dim, num_filters, kernel_size)
                for kernel_size in kernel_sizes
            ])
            self.dropout = nn.Dropout(0.5)
            self.fc = nn.Linear(len(kernel_sizes) * num_filters, num_classes)
            
        def forward(self, x):
            # x: (batch_size, seq_len)
            x = self.embedding(x)  # (batch_size, seq_len, embed_dim)
            x = x.transpose(1, 2)  # (batch_size, embed_dim, seq_len)
            
            conv_outputs = []
            for conv in self.convs:
                conv_out = F.relu(conv(x))  # (batch_size, num_filters, conv_seq_len)
                pooled = F.max_pool1d(conv_out, conv_out.size(2))  # (batch_size, num_filters, 1)
                conv_outputs.append(pooled.squeeze(2))  # (batch_size, num_filters)
            
            x = torch.cat(conv_outputs, dim=1)  # (batch_size, len(kernel_sizes) * num_filters)
            x = self.dropout(x)
            x = self.fc(x)  # (batch_size, num_classes)
            
            return x


def create_training_data_from_keywords():
    """从关键词生成训练数据"""
    classifier = SubjectClassifier()
    training_data = []
    
    for subject, categories in classifier.subject_keywords.items():
        for category, keywords in categories.items():
            for keyword in keywords:
                # 生成包含关键词的简单句子
                sentences = [
                    f"请解释{keyword}的概念",
                    f"关于{keyword}的题目",
                    f"这道题考查的是{keyword}",
                    f"{keyword}相关知识点",
                    f"计算{keyword}的值",
                    f"分析{keyword}的特点"
                ]
                
                for sentence in sentences:
                    training_data.append((sentence, subject))
    
    return training_data


def test_classifier():
    """测试分类器功能"""
    print("🧪 测试智能学科分类器...")
    
    classifier = SubjectClassifier()
    
    # 测试用例
    test_cases = [
        "计算三角形的面积公式",
        "分析鲁迅作品的艺术特色",
        "Translate the following sentence into Chinese",
        "分析电路图中电流的方向",
        "写出氧气的化学式",
        "细胞分裂的过程",
        "明朝的政治制度",
        "中国的地理位置特点",
        "马克思主义基本原理",
        "解方程组：x+y=5, x-y=1"
    ]
    
    print("\n📊 分类结果:")
    print("-" * 80)
    
    for i, text in enumerate(test_cases, 1):
        result = classifier.classify(text)
        print(f"{i:2d}. 文本: {text}")
        print(f"    学科: {result['subject_name']} ({result['subject']})")
        print(f"    置信度: {result['confidence']:.3f}")
        print(f"    方法: {result['method']}")
        print(f"    详情: 关键词={result['details']['keyword']['confidence']:.3f}, "
              f"规则={result['details']['rule']['confidence']:.3f}")
        print()
    
    # 显示统计信息
    stats = classifier.get_classification_stats()
    print("📈 分类统计:")
    print(f"总分类次数: {stats['total_classifications']}")
    print("方法使用情况:")
    for method, data in stats['method_usage'].items():
        if isinstance(data, dict):
            print(f"  {method}: {data['count']} 次 ({data['percentage']:.1f}%)")
    
    # 保存模型
    model_path = classifier.save_model()
    print(f"\n💾 模型已保存: {model_path}")
    
    return classifier


if __name__ == "__main__":
    # 运行测试
    test_classifier()
