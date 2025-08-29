import jieba
from collections import Counter

def summarize_wrong_questions(results):
    """简化的错题知识点提取"""
    wrong_questions = [r['question'] for r in results if not r.get('correct', True)]
    
    if not wrong_questions:
        return []
    
    # 简单的关键词提取
    all_words = []
    for question in wrong_questions:
        words = jieba.cut(question)
        # 过滤掉单字和常见停用词
        meaningful_words = [w for w in words if len(w) > 1 and w not in ['的', '是', '在', '了', '和', '与']]
        all_words.extend(meaningful_words)
    
    # 统计词频，返回前5个最常见的词作为知识点
    counter = Counter(all_words)
    top_words = [word for word, count in counter.most_common(5)]
    
    return top_words