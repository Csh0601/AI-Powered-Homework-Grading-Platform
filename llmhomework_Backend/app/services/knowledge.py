import jieba
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 加载BERT分类模型（假设已训练好并保存在bert_knowledge.pt）
try:
    bert_tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
    bert_model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=10)
    bert_model.load_state_dict(torch.load('bert_knowledge.pt', map_location='cpu'))
    bert_model.eval()
    BERT_READY = True
except Exception as e:
    bert_tokenizer = None
    bert_model = None
    BERT_READY = False

def extract_knowledge(texts):
    words = []
    for text in texts:
        words += jieba.lcut(text)
    counter = Counter(words)
    return [w for w, _ in counter.most_common(5) if len(w)>1]

def extract_knowledge_tfidf(texts):
    vectorizer = TfidfVectorizer(tokenizer=jieba.lcut, stop_words=None)
    X = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    scores = X.sum(axis=0).A1
    top_indices = scores.argsort()[-5:][::-1]
    return [feature_names[i] for i in top_indices]

def classify_knowledge_bert(texts):
    if not BERT_READY:
        return ['BERT模型未加载']
    labels = []
    for text in texts:
        inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=64)
        with torch.no_grad():
            outputs = bert_model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
            labels.append(f'知识点{pred}')
    return labels

def summarize_wrong_questions(results):
    wrongs = [r['question'] for r in results if not r['correct']]
    if BERT_READY and wrongs:
        return classify_knowledge_bert(wrongs)
    elif wrongs:
        return extract_knowledge_tfidf(wrongs)
    else:
        return []
