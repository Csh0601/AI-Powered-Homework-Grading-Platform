from difflib import SequenceMatcher
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

# 加载BERT模型（全局只加载一次）
bert_model = SentenceTransformer('app/models/paraphrase-multilingual-MiniLM-L12-v2')

def bert_sim(a, b):
    emb1 = bert_model.encode(a, convert_to_tensor=True)
    emb2 = bert_model.encode(b, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(emb1, emb2).item()
    return sim

def grade_homework(ocr_result: List[str]) -> List[Dict]:
    results = []
    for idx, item in enumerate(ocr_result):
        if ':' in item:
            q, a = item.split(':', 1)
            # 选择题
            if any(opt in a.upper() for opt in ['A','B','C','D']):
                correct = True  # 实际应查标准答案
                score = 1 if correct else 0
                results.append({'question': q, 'answer': a, 'type': '选择题', 'correct': correct, 'score': score, 'explanation': ''})
            # 判断题
            elif a.strip() in ['对','错','True','False']:
                correct = True  # 实际应查标准答案
                score = 1 if correct else 0
                results.append({'question': q, 'answer': a, 'type': '判断题', 'correct': correct, 'score': score, 'explanation': ''})
            else:
                # 填空题用BERT相似度
                correct_answer = '标准答案'  # 实际应查标准答案
                sim = bert_sim(a.strip(), correct_answer)
                score = round(sim,2)
                results.append({'question': q, 'answer': a, 'type': '填空题', 'correct': sim>0.8, 'score': score, 'explanation': f'BERT相似度: {score}'})
        else:
            results.append({'question': item, 'answer': '', 'type': '未知题型', 'correct': False, 'score': 0, 'explanation': '格式错误'})
    return results
