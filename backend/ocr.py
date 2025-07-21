import easyocr
import re
from typing import List, Dict, Any

reader = easyocr.Reader(['ch_sim', 'en'])

def clean_line(line: str) -> str:
    """去除多余空格、特殊符号"""
    line = line.strip()
    line = re.sub(r'[^\S\r\n]+', ' ', line)
    line = re.sub(r'[■□◆◇▲△●○◎★☆※→←↑↓]', '', line)
    return line

def is_noise(line: str) -> bool:
    """过滤页眉、页脚、分数栏等非题目内容"""
    if not line or len(line) < 2:
        return True
    if re.search(r'第.{1,3}页|共.{1,3}页|分数|班级|姓名|学号|学校|考试|试卷|密封线', line):
        return True
    return False

def merge_broken_lines(lines: List[str]) -> List[str]:
    """合并被误分割的题干和选项"""
    merged = []
    buffer = ""
    for line in lines:
        if re.match(r'^\d+[\.\、\）]|^（\d+）', line):
            if buffer:
                merged.append(buffer)
            buffer = line
        else:
            if buffer:
                buffer += " " + line
            else:
                buffer = line
    if buffer:
        merged.append(buffer)
    return merged

def split_questions(text: str) -> List[str]:
    """用正则分割题目"""
    pattern = r'(?:^|\n)(\d+[\.\、\）]|（\d+）)'
    matches = list(re.finditer(pattern, text))
    questions = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        q_text = text[start:end].strip()
        if q_text:
            questions.append(q_text)
    return questions

def detect_type(question_text: str) -> str:
    """题型自动识别"""
    if re.search(r'[A-D][\.\、\)]', question_text) and len(re.findall(r'[A-D][\.\、\)]', question_text)) >= 2:
        return '选择题'
    elif re.search(r'对|错|True|False', question_text, re.IGNORECASE):
        return '判断题'
    elif re.search(r'_{2,}|（\s*）|___+', question_text):
        return '填空题'
    else:
        return '未知/简答题'

def extract_options(question_text: str) -> List[str]:
    """提取选择题选项"""
    options = re.findall(r'([A-D][\.\、\)]\s*[^A-D]+)', question_text)
    return [opt.strip() for opt in options]

def extract_answer(question_text: str) -> str:
    """提取标准答案"""
    match = re.search(r'(?:答案|正确答案)[:：]?\s*([A-D对错TrueFalse]+)', question_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def structure_questions(ocr_lines: List[str]) -> List[Dict[str, Any]]:
    """综合结构化：题目分割、题型识别、选项提取、答案提取"""
    text = '\n'.join(ocr_lines)
    questions_raw = split_questions(text)
    structured = []
    for q in questions_raw:
        q_type = detect_type(q)
        options = extract_options(q) if q_type == '选择题' else []
        answer = extract_answer(q)
        structured.append({
            'raw': q,
            'question': q,  # 新增，便于前端兼容
            'type': q_type,
            'options': options,
            'answer': answer
        })
    return structured

def ocr_image(image_path: str) -> List[Dict[str, Any]]:
    """
    市场级别：对图片进行OCR识别，返回结构化题目列表
    """
    result = reader.readtext(image_path, detail=0)
    lines = [clean_line(line) for line in result if not is_noise(line)]
    # 合并被误分割的题干和选项
    lines = merge_broken_lines(lines)
    # 结构化
    structured = structure_questions(lines)
    return structured

# 用法示例
if __name__ == "__main__":
    result = ocr_image('your_exam_image.jpg')
    for q in result:
        print(q)
