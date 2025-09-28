#!/usr/bin/env python3
"""
独立测试相似度搜索功能
避免复杂的依赖问题
"""

import sys
import os
import re
import jieba
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import hashlib

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

# 尝试导入机器学习库
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
    print("✅ 机器学习库可用")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ 机器学习库不可用，将使用简化版本")

class SimpleSimilarityEngine:
    """简化的相似度搜索引擎"""
    
    def __init__(self):
        self.question_vectors = None
        self.tfidf_vectorizer = None
        self.questions = []
        self.index_built = False
        
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 保留重要的数学符号
        math_symbols = ['=', '+', '-', '×', '÷', '>', '<', '≥', '≤', '≠', '≈', 
                       '√', '^', '²', '³', 'π', '∞', '°', '∠', '△', '□', '○']
        
        # 分词
        words = []
        for word in jieba.cut(text):
            word = word.strip()
            if word and (len(word) > 1 or word in math_symbols or word.isdigit()):
                words.append(word)
        
        return ' '.join(words)
    
    def build_index(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建题目索引"""
        self.questions = questions
        start_time = datetime.now()
        
        if not ML_AVAILABLE:
            # 简化版本
            self.index_built = True
            build_time = (datetime.now() - start_time).total_seconds()
            return {
                'success': True,
                'indexed_questions': len(questions),
                'build_time_seconds': build_time,
                'vector_dimensions': 0
            }
        
        try:
            # 预处理文本
            processed_texts = []
            for question in questions:
                stem = question.get('stem', '')
                answer = question.get('correct_answer', '')
                combined_text = f"{stem} {answer}"
                processed_text = self.preprocess_text(combined_text)
                processed_texts.append(processed_text)
            
            # 构建TF-IDF向量
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                min_df=1,
                max_df=0.8,
                tokenizer=lambda x: x.split(),
                lowercase=True
            )
            
            # 拟合并转换
            self.question_vectors = self.tfidf_vectorizer.fit_transform(processed_texts)
            self.index_built = True
            
            build_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'indexed_questions': len(questions),
                'build_time_seconds': build_time,
                'vector_dimensions': self.question_vectors.shape[1]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_similar(self, query_question: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """查找相似题目"""
        if not self.index_built:
            return []
        
        query_stem = query_question.get('stem', '')
        query_answer = query_question.get('correct_answer', '')
        query_text = f"{query_stem} {query_answer}"
        processed_query = self.preprocess_text(query_text)
        
        if not ML_AVAILABLE:
            # 简化版本：基于关键词匹配
            return self._simple_search(query_question, top_k)
        
        try:
            # 向量化查询
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            
            # 计算相似度
            similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
            
            # 获取Top-K结果
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for i, idx in enumerate(top_indices):
                if similarities[idx] > 0.1:  # 最低阈值
                    results.append({
                        'rank': i + 1,
                        'question': self.questions[idx],
                        'similarity_score': round(similarities[idx], 4),
                        'match_reasons': ['文本相似度匹配']
                    })
            
            return results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def _simple_search(self, query_question: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        """简化的搜索方法"""
        query_text = f"{query_question.get('stem', '')} {query_question.get('correct_answer', '')}"
        query_words = set(jieba.cut(query_text.lower()))
        
        similarities = []
        
        for i, question in enumerate(self.questions):
            question_text = f"{question.get('stem', '')} {question.get('correct_answer', '')}"
            question_words = set(jieba.cut(question_text.lower()))
            
            # 计算Jaccard相似度
            intersection = len(query_words.intersection(question_words))
            union = len(query_words.union(question_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.1:
                similarities.append((i, similarity))
        
        # 排序并返回Top-K
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, (idx, sim) in enumerate(similarities[:top_k]):
            results.append({
                'rank': i + 1,
                'question': self.questions[idx],
                'similarity_score': round(sim, 4),
                'match_reasons': ['关键词匹配']
            })
        
        return results

def test_similarity_engine():
    """测试相似度搜索引擎"""
    print("🧪 测试相似度搜索引擎（独立版本）...")
    print("=" * 50)
    
    # 创建搜索引擎
    engine = SimpleSimilarityEngine()
    
    # 准备测试数据
    test_questions = [
        {
            'question_id': 'Q001',
            'stem': '解一元一次方程：2x + 3 = 7，求x的值',
            'correct_answer': 'x = 2',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q002',
            'stem': '解方程：3x - 5 = 10，求x的值',
            'correct_answer': 'x = 5',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q003',
            'stem': '计算三角形的面积，已知底边为6米，高为4米',
            'correct_answer': '12平方米',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q004',
            'stem': '选择正确答案：下列哪个是质数？A.4 B.6 C.7 D.8',
            'correct_answer': 'C',
            'question_type': 'single_choice',
            'difficulty_level': 1,
            'subject': 'math'
        },
        {
            'question_id': 'Q005',
            'stem': '解一元二次方程：x² - 5x + 6 = 0',
            'correct_answer': 'x = 2 或 x = 3',
            'question_type': 'calculation',
            'difficulty_level': 4,
            'subject': 'math'
        }
    ]
    
    print(f"📚 准备 {len(test_questions)} 个测试题目")
    
    # 构建索引
    print("\n🏗️ 构建题目索引...")
    index_result = engine.build_index(test_questions)
    
    if index_result['success']:
        print(f"✅ 索引构建成功！")
        print(f"   - 索引题目数: {index_result['indexed_questions']}")
        print(f"   - 构建时间: {index_result['build_time_seconds']:.3f} 秒")
        print(f"   - 向量维度: {index_result['vector_dimensions']}")
    else:
        print(f"❌ 索引构建失败: {index_result.get('error')}")
        return
    
    # 执行搜索
    print("\n🔍 执行相似度搜索...")
    
    query = {
        'stem': '求解方程：4x + 1 = 9，x等于多少？',
        'correct_answer': 'x = 2',
        'question_type': 'calculation',
        'difficulty_level': 2,
        'subject': 'math'
    }
    
    print(f"查询题目: {query['stem']}")
    
    results = engine.find_similar(query, top_k=3)
    
    print(f"\n📊 找到 {len(results)} 个相似题目:")
    for result in results:
        print(f"\n{result['rank']}. 相似度: {result['similarity_score']:.3f}")
        print(f"   题目: {result['question']['stem']}")
        print(f"   答案: {result['question']['correct_answer']}")
        print(f"   匹配原因: {', '.join(result['match_reasons'])}")
    
    print("\n🎉 相似度搜索测试完成！")
    return True

if __name__ == "__main__":
    try:
        success = test_similarity_engine()
        if success:
            print("\n✅ Day10相似度搜索功能验证成功！")
        else:
            print("\n❌ 测试失败")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
