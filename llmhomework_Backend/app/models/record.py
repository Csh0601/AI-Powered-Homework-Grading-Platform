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
    from app.utils.schema_validator import validate_database_record
    
    # 验证记录格式
    validation = validate_database_record(record)
    if not validation['valid']:
        print(f"⚠️ 数据库记录格式验证失败: {validation['error']}")
        # 可以选择是否继续保存或抛出异常
        # raise ValueError(f"数据格式不符合Schema: {validation['error']}")
    else:
        print("✅ 数据库记录格式验证通过")
    
    records = get_records()
    record = clean_record(record)
    
    # 添加汇总信息
    if 'grading_result' in record and record['grading_result']:
        grading_results = record['grading_result']
        total_questions = len(grading_results)
        correct_count = sum(1 for r in grading_results if r.get('correct', False))
        total_score = sum(r.get('score', 0) for r in grading_results)
        accuracy_rate = correct_count / total_questions if total_questions > 0 else 0
        
        record['summary'] = {
            'total_questions': total_questions,
            'correct_count': correct_count,
            'total_score': total_score,
            'accuracy_rate': round(accuracy_rate, 2)
        }
    
    records.append(record)
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
