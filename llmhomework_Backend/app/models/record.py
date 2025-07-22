import os
import json

RECORD_FILE = os.path.join(os.path.dirname(__file__), '../../uploads/records.json')

def get_records(user_id=None, task_id=None):
    if not os.path.exists(RECORD_FILE):
        return []
    with open(RECORD_FILE, 'r', encoding='utf-8') as f:
        try:
            records = json.load(f)
        except Exception:
            return []
    if user_id:
        records = [r for r in records if r.get('user_id') == user_id]
    if task_id:
        records = [r for r in records if r.get('task_id') == task_id]
    return records

def clean_record(record):
    # 只保留结构化文本数据，去除图片内容和非utf-8内容
    def safe(obj):
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif isinstance(obj, list):
            return [safe(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: safe(v) for k, v in obj.items()}
        else:
            return str(obj)
    return safe(record)

def save_record(record):
    records = get_records()
    record = clean_record(record)
    records.append(record)
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
