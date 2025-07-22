import jieba
import re
from typing import List, Dict

def clean_text(text: str) -> str:
    # 去除特殊符号、空白等
    text = re.sub(r'[\s\u3000]+', '', text)
    text = re.sub(r'[，。！？、~@#￥%……&*（）\[\]{}<>《》:：；“”‘’"\'\\/]', '', text)
    return text

def segment_text(text: str) -> List[str]:
    # 中文分词
    return list(jieba.cut(text))

def classify_question(text: str) -> str:
    # 简单题型分类：选择题、判断题、填空题
    if re.search(r'[A-D][.．、]', text):
        return '选择题'
    elif re.search(r'对|错|True|False', text, re.I):
        return '判断题'
    elif '___' in text or '（' in text:
        return '填空题'
    else:
        return '未知题型'

def preprocess_ocr_result(ocr_lines: List[str]) -> List[Dict]:
    # 结构化OCR结果
    results = []
    for line in ocr_lines:
        clean = clean_text(line)
        segs = segment_text(clean)
        qtype = classify_question(line)
        results.append({'raw': line, 'clean': clean, 'segs': segs, 'type': qtype})
    return results 