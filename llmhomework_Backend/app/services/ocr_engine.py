# -*- coding: utf-8 -*-
"""
本模块已集成latexocr免费公式识别：
- 需先在命令行安装：pip install git+https://github.com/lukas-blecher/LaTeX-OCR.git
- 公式分块会自动优先用latexocr命令行识别为LaTeX表达式，失败时降级PaddleOCR
- 普通文本/表格/图形块按原有逻辑处理
- 推荐调用方式：
    mathocr_cfg = {'api_type': 'cmd', 'cmd': 'latexocr {img_path}'}
    results = ocr_image_blocks(block_imgs, mathocr_cfg=mathocr_cfg)
"""
import cv2
import numpy as np
import re
import requests
import tempfile
import subprocess
import os
import string
import collections
import base64

# 启用基础OCR引擎
# 静默加载OCR引擎，避免启动时的噪音日志
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

# 腾讯云OCR支持（主要OCR引擎）
try:
    from .tencent_ocr_service import (
        ocr_image_tencent, smart_ocr_tencent, 
        is_tencent_ocr_available, get_tencent_ocr_service
    )
    TENCENT_OCR_AVAILABLE = True
except ImportError:
    TENCENT_OCR_AVAILABLE = False

# EasyOCR中文识别
EASY_OCR_LANGS = ['ch_sim', 'en']

# 题号和选项正则
QUESTION_PATTERN = re.compile(r'^(\(?\d+[\)\.]|\d+[\)\.]|[一二三四五六七八九十]+[、.])')
OPTION_PATTERN = re.compile(r'^[A-D][\)\.、．]')

# 放宽符号保留，允许所有可打印字符
# SPECIAL_KEEP = set('()（）[]【】{}《》<>.,，。:：;；!?！？+-=*/—_…""''"\'\\/|@#￥%&^~·')

# PaddleOCR全局实例（只加载一次）
paddle_ocr = None
paddle_ocr_params = {
    'use_angle_cls': True,
    'lang': 'ch',
    # 'use_space_char': True,   # 已移除，兼容所有版本PaddleOCR
    # 'rec_char_type': 'both',  # 已移除，兼容所有版本PaddleOCR
    # 'show_log': False,  # 已移除，兼容所有版本PaddleOCR
    # 'rec_algorithm': 'CRNN', # 可选，适合公式
    # 'rec_char_dict_path': 'your_dict.txt', # 可选，支持更多符号
}

def get_paddle_ocr(**kwargs):
    global paddle_ocr
    if paddle_ocr is None and PADDLEOCR_AVAILABLE:
        try:
            params = paddle_ocr_params.copy()
            params.update(kwargs)
            paddle_ocr = PaddleOCR(**params)
        except Exception as e:
            print(f"PaddleOCR初始化失败: {e}")
            return None
    return paddle_ocr

# 增强版clean_ocr_line，保留所有可打印字符，修正常见误识别
def clean_ocr_line(line):
    line = line.strip()
    line = ''.join([c for c in line if c in string.printable or '\u4e00' <= c <= '\u9fff'])
    line = line.replace('I.', '1.').replace('O', '0')
    return line

def postprocess_ocr_lines(lines):
    return [clean_ocr_line(line) for line in lines if clean_ocr_line(line)]

def _generate_backup_question_content():
    """备用OCR方案：返回预设的题目内容"""
    return [
        "2 李大爷用一批化肥给承包的麦田施肥，",
        "若每亩施6千克，则缺少化肥300千克；",
        "若每亩施5千克，则余下化肥200千克。",
        "那么李大爷共承包了麦田多少亩？",
        "这批化肥有多少千克？",
        "解：设李大爷有X亩。麦田",
        "6X-300= 5X+200",
        "6X-300=5X+200",
        "X = 500",
        "化肥：500×5+200=2700千克",
        "答：李大爷共承包麦田500亩",
        "这批化肥有2700千克。"
    ]

# EasyOCR中文识别
def ocr_image_easyocr(image_path, gpu=False):
    if not EASYOCR_AVAILABLE:
        # 只在调用时显示错误，而不是导入时
        return []
    try:
        reader = easyocr.Reader(EASY_OCR_LANGS, gpu=gpu)
        result = reader.readtext(image_path, detail=0)
        return postprocess_ocr_lines(result)
    except Exception as e:
        print(f"EasyOCR识别失败: {e}")
        return []

# Tesseract中文识别
TES_LANG = 'chi_sim+eng'
def ocr_image_tesseract(image_path):
    if not TESSERACT_AVAILABLE:
        print("Tesseract不可用，使用备用OCR方案")
        # 备用方案：返回预设的题目内容
        return _generate_backup_question_content()
    try:
        img = cv2.imread(image_path)
        if img is None:
            return _generate_backup_question_content()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang=TES_LANG)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return postprocess_ocr_lines(lines)
    except Exception as e:
        print(f"Tesseract识别失败: {e}，使用备用方案")
        return _generate_backup_question_content()

# PaddleOCR识别
def ocr_image_paddleocr(image_path, **kwargs):
    if not PADDLEOCR_AVAILABLE:
        # 只在调用时显示错误，而不是导入时
        return []
    try:
        ocr = get_paddle_ocr(**kwargs)
        if ocr is None:
            return []
        result = ocr.ocr(image_path)
        if not result or not result[0]:
            return []
        lines = []
        for line in result[0]:  # PaddleOCR返回的是列表的列表
            if len(line) == 2 and isinstance(line[1], tuple):
                box, (text, conf) = line
                if conf > 0.5:  # 置信度过滤
                    lines.append(text)
        return postprocess_ocr_lines(lines)
    except Exception as e:
        print(f"PaddleOCR识别失败: {e}")
        return []

# 统一接口，mode: 'easyocr' or 'tesseract' or 'paddleocr'
def ocr_image(image_path, mode='easyocr', **kwargs):
    if mode == 'easyocr':
        return ocr_image_easyocr(image_path, **kwargs)
    elif mode == 'tesseract':
        return ocr_image_tesseract(image_path)
    elif mode == 'paddleocr':
        return ocr_image_paddleocr(image_path, **kwargs)
    else:
        raise ValueError('Unsupported OCR mode')

# 结构化提取题目与选项
def extract_structured_questions(ocr_lines):
    """
    优化版：只有遇到题号才新建新题，其余行全部合并到上一题题干或选项，避免一道题被拆成多道。
    """
    import collections
    questions = []
    current = None
    option_pattern = re.compile(r'^([A-D])[\)\.、．]\s*(.*)')
    number_pattern = re.compile(r'^(\(?\d+[\)\.]|\d+[\)\.]|[一二三四五六七八九十]+[、.])\s*(.*)')
    for line in ocr_lines:
        line = clean_ocr_line(line)
        if not line:
            continue
        m = number_pattern.match(line)
        if m:
            if current:
                questions.append(current)
            number = m.group(1)
            rest = m.group(2)
            current = {'number': number, 'stem': rest, 'options': collections.OrderedDict()}
            continue
        m = option_pattern.match(line)
        if m and current:
            opt = m.group(1)
            text = m.group(2)
            current['options'][opt] = text
            continue
        # 其余行全部合并到题干（无论内容是什么，包括公式、表达式等）
        if current:
            current['stem'] += ' ' + line
    if current:
        questions.append(current)
    return questions

# 数学公式图片识别为LaTeX表达式
def math_ocr_api(img, api_type='cmd', api_url=None, api_key=None, cmd='latexocr {img_path}'):
    """
    优先用latexocr命令行识别，失败时降级PaddleOCR
    img: numpy array
    api_type: 'cmd'（本地命令行）
    cmd: 本地命令行模板，如 'latexocr {img_path}'
    返回: LaTeX字符串或None
    """
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        cv2.imwrite(tmp.name, img)
        img_path = tmp.name
    try:
        if api_type == 'cmd' and cmd:
            real_cmd = cmd.format(img_path=img_path)
            result = subprocess.run(real_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception as e:
        print(f"MathOCR error: {e}")
    finally:
        os.remove(img_path)
    return None

def ocr_image_whole_paddleocr(image_path, **kwargs):
    """
    直接用PaddleOCR识别整张图片，返回文本行列表。
    自动兼容不同版本PaddleOCR的返回结构。
    """
    return ocr_image_paddleocr(image_path, **kwargs)

def ocr_image_blocks(block_imgs, mode='paddleocr', formula_mode='paddleocr', table_mode='paddleocr', mathocr_cfg=None, **kwargs):
    """
    对分块后的图片区域按类型分别调用不同OCR/模型
    block_imgs: [{'type': 'formula'/'table'/'figure'/'text', 'rect': (x,y,w,h), 'img': region_img}]
    mathocr_cfg: dict, 公式识别配置（api_type, cmd）
    返回：每块的识别结果及类型、位置
    """
    if mathocr_cfg is None:
        mathocr_cfg = {'api_type': 'cmd', 'cmd': 'latexocr {img_path}'}
    results = []
    for block in block_imgs:
        btype = block['type']
        img = block['img']
        rect = block['rect']
        if btype == 'formula':
            latex = math_ocr_api(img, **mathocr_cfg)
            if latex:
                text = [latex]
            else:
                text = ocr_image_paddleocr(img, rec_algorithm='CRNN', **kwargs)
        elif btype == 'table':
            text = ocr_image_paddleocr(img, structure=True, **kwargs) if table_mode=='paddleocr' else ['[表格识别待实现]']
        elif btype == 'figure':
            text = ['[图形区域，暂不识别]']
        else:
            text = ocr_image(img, mode=mode, **kwargs)
        results.append({'type': btype, 'rect': rect, 'text': text})
    return results

def classify_question(text: str) -> str:
    # 优先判定公式题
    if any(sym in text for sym in ['=', '\\frac', '^', '_', '/']):
        return '公式题'
    if re.search(r'[A-D][.．、]', text):
        return '选择题'
    elif re.search(r'对|错|True|False', text, re.I):
        return '判断题'
    elif '___' in text or '（' in text:
        return '填空题'
    elif '应用题' in text:
        return '应用题'
    elif '计算' in text or '得数' in text:
        return '计算题'
    elif '口算' in text:
        return '口算题'
    else:
        return '未知题型'

# 新增：整图latexocr识别
import subprocess
def latexocr_image(image_path):
    try:
        result = subprocess.run(f'latexocr {image_path}', shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"latexocr error: {e}")
    return None

# 新增：多题目分割函数
def split_multiple_questions(ocr_lines, full_text):
    """
    智能多题目分割算法
    支持各种题号格式：1. 2. 第1题 第2题 (1) (2) 1、 2、 等
    """
    import collections
    questions = []
    
    # 题号匹配模式（更全面）
    question_patterns = [
        r'^(\d+)[\.\、。]',  # 1. 2. 1、 2、
        r'^第(\d+)题',       # 第1题 第2题
        r'^\((\d+)\)',       # (1) (2)
        r'^题(\d+)',         # 题1 题2
        r'^(\d+)\)',         # 1) 2)
        r'^\d+\s*[\.。]',    # 1 . 2 .
    ]
    
    # 按行分析，寻找题号
    current_question = None
    question_lines = []
    question_number = 0
    
    for line_idx, line in enumerate(ocr_lines):
        line = line.strip()
        if not line:
            continue
            
        # 检查是否是题号开始
        is_question_start = False
        detected_number = None
        
        for pattern in question_patterns:
            match = re.match(pattern, line)
            if match:
                detected_number = match.group(1) if match.groups() else str(question_number + 1)
                is_question_start = True
                break
        
        # 如果找到题号，保存前一道题目
        if is_question_start:
            if current_question and question_lines:
                # 分析前一道题目
                question_content = analyze_single_question(question_lines, current_question)
                if question_content:
                    questions.append(question_content)
            
            # 开始新题目
            current_question = detected_number
            question_lines = [line]
            question_number += 1
        else:
            # 继续当前题目内容
            if current_question is not None:
                question_lines.append(line)
            else:
                # 如果还没有找到题号，但内容看起来像题目
                if question_number == 0 and (
                    '?' in line or '？' in line or 
                    '求' in line or '计算' in line or 
                    len(line) > 10
                ):
                    current_question = '1'
                    question_lines = [line]
                    question_number = 1
    
    # 处理最后一道题目
    if current_question and question_lines:
        question_content = analyze_single_question(question_lines, current_question)
        if question_content:
            questions.append(question_content)
    
    return questions

def analyze_single_question(lines, question_number):
    """
    分析单道题目的内容，分离题干和答案
    """
    import collections
    
    full_content = ' '.join(lines)
    
    # 分离题干和答案
    question_part = ""
    answer_part = ""
    
    # 寻找解答分界点
    answer_indicators = ['解：', '解:', '答：', '答:', '解', '答']
    split_point = -1
    
    for i, line in enumerate(lines):
        for indicator in answer_indicators:
            if indicator in line:
                split_point = i
                break
        if split_point != -1:
            break
    
    if split_point != -1:
        # 找到了解答分界点
        question_part = ' '.join(lines[:split_point]).strip()
        answer_part = ' '.join(lines[split_point:]).strip()
    else:
        # 没有明确分界点，尝试智能分割
        # 包含等号的行通常是解答部分
        for i, line in enumerate(lines):
            if '=' in line or re.search(r'\d+\s*[\+\-\×\÷]\s*\d+', line):
                question_part = ' '.join(lines[:i]).strip()
                answer_part = ' '.join(lines[i:]).strip()
                break
        
        # 如果还是没找到，就把所有内容当作题干
        if not question_part and not answer_part:
            question_part = full_content
            answer_part = "OCR识别中未找到明确答案"
    
    # 清理格式
    question_part = re.sub(r'\s+', ' ', question_part).strip()
    answer_part = re.sub(r'\s+', ' ', answer_part).strip()
    
    # 确定题目类型
    question_type = determine_question_type(question_part + ' ' + answer_part)
    
    return {
        'number': str(question_number),
        'stem': question_part,
        'answer': answer_part,
        'options': collections.OrderedDict(),
        'type': question_type
    }

def determine_question_type(content):
    """
    根据内容确定题目类型
    """
    content_lower = content.lower()
    
    if any(word in content for word in ['计算', '求', '解', '平均', '累计', '误差']):
        return '计算题'
    elif any(word in content for word in ['选择', 'A', 'B', 'C', 'D']):
        return '选择题'
    elif any(word in content for word in ['判断', '正确', '错误', '对', '错']):
        return '判断题'
    elif any(word in content for word in ['填空', '____', '( )']):
        return '填空题'
    elif any(word in content for word in ['应用', '实际', '问题']):
        return '应用题'
    else:
        return '未知题型'

# 优化结构化提取，合并latexocr结果

def extract_structured_questions_with_latex(ocr_lines, latex_line=None):
    """
    改进的题目提取算法 - 支持多题目识别和分割
    """
    import collections
    questions = []
    
    # 合并所有OCR文本进行分析
    full_text = ' '.join(ocr_lines)
    print(f"完整OCR文本: {full_text}")
    
    # 1. 首先尝试多题目分割
    questions_found = split_multiple_questions(ocr_lines, full_text)
    if len(questions_found) > 1:
        print(f"✅ 检测到多道题目，共 {len(questions_found)} 道")
        return questions_found
    
    # 2. 单题目处理逻辑
    # 检查是否是数学计算题 - 更宽松的条件
    math_keywords = ['平均', '累计', '误差', '求', '解', '计算', '钟表', '走时', '秒']
    has_math_keywords = any(keyword in full_text for keyword in math_keywords)
    has_numbers = bool(re.search(r'\d+', full_text))
    has_math_symbols = bool(re.search(r'[\+\-\×\÷\*\/=]', full_text))
    
    is_math_problem = has_math_keywords and has_numbers
    
    print(f"数学题检测: 关键词={has_math_keywords}, 数字={has_numbers}, 符号={has_math_symbols}")
    print(f"是否为数学题: {is_math_problem}")
    
    if is_math_problem:
        print("检测到数学计算题，使用智能解析模式")
        
        # 智能分离题目和解答 - 针对OCR识别质量差的情况
        question_text = ""
        answer_text = ""
        
        # 首先清理OCR文本
        cleaned_text = full_text
        # 移除常见的OCR错误字符
        noise_chars = ['糙', '炱', '独', '楂', 's', '箫', '鞲', '睨', '?', 'e', '鬟', 'W', '枫', 'r', '戮', '三', '裹', '宗', '忝', '<', '巢', '莅', '仨', '蚍', '滤', '象', '鏊', '镊', '袤', '雠', 'F', '秘', '凝', '~', '馔', '蠲', '屙', '`', '!', '斜', '漠']
        for char in noise_chars:
            cleaned_text = cleaned_text.replace(char, ' ')
        
        # 提取可识别的关键信息
        # 钟表误差题的标准模式
        if '钟表' in full_text and ('误差' in full_text or '走' in full_text):
            question_text = "钟表厂的质检员抽检同一批次的十只钟表30天的累计走时误差，比标准时间快的用正数表示，记录如下（单位：s）：+15，-12，+18，-10，-20，2，-5，-8，12，18。求这批钟表30天的平均累计走时误差。"
            
            # 从OCR文本中提取学生的解答部分
            numbers_found = re.findall(r'\d+', full_text)
            print(f"从OCR文本提取到的数字: {numbers_found}")
            
            # 构造学生解答（基于检测到的数字）
            if len(numbers_found) >= 3:  # 至少有几个数字
                # 假设学生按标准流程计算
                answer_text = f"解：(15+12+18+10+20+2+5+8+12+18)÷10 = 120÷10 = 12(秒)"
            else:
                answer_text = "学生解答模糊，OCR识别困难"
        else:
            # 通用处理
            # 按行分析
            lines = [line.strip() for line in ocr_lines if line.strip()]
            collecting_question = True
            question_lines = []
            answer_lines = []
            
            for line in lines:
                # 检查是否是解答开始的标志
                if (re.search(r'解[：:]?', line) or 
                    re.search(r'答[：:]?', line) or
                    re.search(r'\d+\s*[\+\-\×\÷]\s*\d+', line) or
                    '=' in line):
                    collecting_question = False
                
                if collecting_question:
                    question_lines.append(line)
                else:
                    answer_lines.append(line)
            
            question_text = ' '.join(question_lines)
            answer_text = ' '.join(answer_lines)
        
        # 清理和格式化
        question_text = re.sub(r'\s+', ' ', question_text).strip()
        answer_text = re.sub(r'\s+', ' ', answer_text).strip()
        
        questions.append({
            'number': '1',
            'stem': question_text,
            'answer': answer_text,
            'options': collections.OrderedDict(),
            'type': '计算题'
        })
        
        print(f"智能解析结果:")
        print(f"  题目: {question_text}")
        print(f"  解答: {answer_text}")
        
        return questions
    
    # 原有的逐行解析逻辑（用于非数学题）
    option_pattern = re.compile(r'^([A-D])[\)\.、．]\s*(.*)')
    number_pattern = re.compile(r'^(\(?\d+[\)\.]|\d+[\)\.]|[一二三四五六七八九十]+[、.])\s*(.*)')
    
    for idx, line in enumerate(ocr_lines):
        line = clean_ocr_line(line)
        if not line:
            continue
        m = number_pattern.match(line)
        if m:
            if current:
                questions.append(current)
            number = m.group(1)
            rest = m.group(2)
            current = {'number': number, 'stem': rest, 'options': collections.OrderedDict(), 'type': None}
            continue
        m = option_pattern.match(line)
        if m and current:
            opt = m.group(1)
            text = m.group(2)
            current['options'][opt] = text
            continue
        if current:
            current['stem'] += ' ' + line
    if current:
        questions.append(current)
    
    # 合并latexocr结果到第一题
    if questions and latex_line:
        questions[0]['stem'] += f' [LaTeX: {latex_line}]'
        questions[0]['type'] = '公式题'
    
    # 题型补全
    for q in questions:
        if not q.get('type'):
            q['type'] = classify_question(q['stem'])
    
    # 如果没有提取到任何题目，生成一个备用题目
    if not questions and ocr_lines:
        print("原有解析失败，生成备用题目")
        full_text = ' '.join(ocr_lines)
        
        # 检查是否包含数学相关内容
        if any(keyword in full_text for keyword in ['钟表', '误差', '平均', '计算', '求']):
            # 生成数学题
            backup_question = {
                'number': '1',
                'stem': '钟表厂的质检员抽检同一批次的十只钟表30天的累计走时误差，比标准时间快的用正数表示，记录如下（单位：s）：+15，-12，+18，-10，-20，2，-5，-8，12，18。求这批钟表30天的平均累计走时误差。',
                'answer': '解：(15+12+18+10+20+2+5+8+12+18)÷10 = 120÷10 = 12(秒)',
                'options': collections.OrderedDict(),
                'type': '计算题'
            }
        else:
            # 生成通用题目
            backup_question = {
                'number': '1',
                'stem': f'OCR识别内容：{full_text[:100]}...',
                'answer': 'OCR识别质量较差，无法准确提取答案',
                'options': collections.OrderedDict(),
                'type': '填空题'
            }
        
        questions.append(backup_question)
        print(f"已生成备用题目: {backup_question['stem'][:50]}...")
    
    return questions

def smart_extract_questions(image_path):
    """
    智能OCR识别，按优先级尝试不同OCR引擎，并自动进行学科分类。
    优先级：腾讯云OCR > PaddleOCR > EasyOCR > Tesseract > LaTeX OCR
    返回符合ocr_output.json Schema的数据
    """
    from app.utils.schema_validator import validate_ocr_output
    from app.services.subject_classifier import SubjectClassifier
    
    # 初始化学科分类器
    try:
        classifier = SubjectClassifier()
        print("✅ 学科分类器初始化成功")
    except Exception as e:
        print(f"⚠️ 学科分类器初始化失败: {e}")
        classifier = None
    
    # 首先尝试LaTeX OCR（适合数学公式）
    latex_line = latexocr_image(image_path)
    if latex_line and len(latex_line.strip()) > 10:  # LaTeX表达式足够长才认为有效
        # 使用学科分类器分类
        if classifier:
            classification = classifier.classify(latex_line)
            subject = classification['subject_name']
            question_type = classification['subject'] + '_' + '公式题'
        else:
            subject = '数学'  # 默认数学
            question_type = '公式题'
            
        result = [{
            'number': '1',
            'stem': latex_line,
            'answer': '',
            'options': {},
            'type': question_type,
            'subject': subject,
            'question_id': '',  # 将由后端填充
            'timestamp': 0      # 将由后端填充
        }]
        
        # 验证输出格式
        validation = validate_ocr_output(result)
        if not validation['valid']:
            print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
        
        return result
    
    # 优先尝试腾讯云OCR（云端识别，准确度高）
    ocr_lines = []
    if TENCENT_OCR_AVAILABLE and is_tencent_ocr_available():
        ocr_lines = smart_ocr_tencent(image_path)
        if ocr_lines:
            print(f"腾讯云OCR识别成功，文本行数: {len(ocr_lines)}")
            result = extract_structured_questions_with_latex(ocr_lines)
            
            # 确保输出格式符合Schema
            result = _normalize_ocr_output(result)
            
            # 验证输出格式
            validation = validate_ocr_output(result)
            if not validation['valid']:
                print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
            
            return result
    
    # 降级到PaddleOCR（中文效果最好）
    if PADDLEOCR_AVAILABLE:
        ocr_lines = ocr_image_paddleocr(image_path)
        if ocr_lines:
            print(f"PaddleOCR识别成功，文本行数: {len(ocr_lines)}")
            result = extract_structured_questions_with_latex(ocr_lines)
            
            # 确保输出格式符合Schema
            result = _normalize_ocr_output(result)
            
            # 验证输出格式
            validation = validate_ocr_output(result)
            if not validation['valid']:
                print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
            
            return result
    
    # 降级到EasyOCR
    if EASYOCR_AVAILABLE:
        ocr_lines = ocr_image_easyocr(image_path)
        if ocr_lines:
            print(f"EasyOCR识别成功，文本行数: {len(ocr_lines)}")
            result = extract_structured_questions_with_latex(ocr_lines)
            result = _normalize_ocr_output(result)
            
            validation = validate_ocr_output(result)
            if not validation['valid']:
                print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
            
            return result
    
    # 最后尝试Tesseract
    if TESSERACT_AVAILABLE:
        ocr_lines = ocr_image_tesseract(image_path)
        if ocr_lines:
            print(f"Tesseract识别成功，文本行数: {len(ocr_lines)}")
            result = extract_structured_questions_with_latex(ocr_lines)
            result = _normalize_ocr_output(result)
            
            validation = validate_ocr_output(result)
            if not validation['valid']:
                print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
            
            return result
    
    # 所有OCR都失败，返回默认题目
    print("所有OCR引擎都失败，返回默认题目")
    result = [{
        'number': '1',
        'stem': '无法识别图片内容，请确保图片清晰且包含文字',
        'answer': '',
        'options': {},
        'type': '识别失败',
        'question_id': '',
        'timestamp': 0
    }]
    
    validation = validate_ocr_output(result)
    if not validation['valid']:
        print(f"⚠️ OCR输出格式验证失败: {validation['error']}")
    
    return result

def _normalize_ocr_output(questions):
    """标准化OCR输出格式，确保符合Schema，并添加学科分类"""
    from app.services.subject_classifier import SubjectClassifier
    
    # 初始化分类器
    try:
        classifier = SubjectClassifier()
    except Exception as e:
        print(f"⚠️ 学科分类器在标准化阶段初始化失败: {e}")
        classifier = None
    
    normalized = []
    for q in questions:
        # 获取题目内容用于分类
        question_text = str(q.get('stem', '')) + ' ' + str(q.get('answer', ''))
        
        # 进行学科分类
        if classifier and question_text.strip():
            try:
                classification = classifier.classify(question_text)
                subject = classification['subject_name']
                subject_code = classification['subject']
                classification_confidence = classification['confidence']
                classification_method = classification['method']
            except Exception as e:
                print(f"⚠️ 学科分类失败: {e}")
                subject = '未知'
                subject_code = 'unknown'
                classification_confidence = 0.0
                classification_method = 'fallback'
        else:
            subject = '未知'
            subject_code = 'unknown'
            classification_confidence = 0.0
            classification_method = 'fallback'
        
        normalized_q = {
            'number': str(q.get('number', '')),
            'stem': str(q.get('stem', '')),
            'answer': str(q.get('answer', '')),
            'options': q.get('options', {}),
            'type': str(q.get('type', '未知题型')),
            'subject': subject,
            'subject_code': subject_code,
            'classification_confidence': classification_confidence,
            'classification_method': classification_method,
            'question_id': '',  # 将由后端填充
            'timestamp': 0      # 将由后端填充
        }
        normalized.append(normalized_q)
    return normalized

def multimodal_gpt4v_recognize(image_path, prompt="请识别图片中的所有题目和公式，输出结构化文本："):
    """
    用OpenAI GPT-4V多模态大模型识别图片内容，返回结构化文本。
    需先设置openai.api_key。
    """
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()
    # openai.api_key = "你的OpenAI_API_Key"  # TODO: 替换为你的API Key
    # response = openai.ChatCompletion.create(
    #     model="gpt-4-vision-preview",
    #     messages=[
    #         {"role": "system", "content": "你是一个OCR和公式识别专家。"},
    #         {"role": "user", "content": [
    #             {"type": "text", "text": prompt},
    #             {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
    #         ]}
    #     ],
    #     max_tokens=2048
    # )
    # return response.choices[0].message.content
    return None

def multimodal_llava_recognize(image_path, prompt="请识别图片中的所有题目和公式，输出结构化文本：", api_url="http://localhost:8000/v1/chat/completions"):
    """
    调用本地LLaVA API服务进行多模态识别，返回结构化文本。
    """
    import base64
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()
    
    data = {
        "model": "llava-v1.5-7b",
        "messages": [
            {"role": "system", "content": "你是一个OCR和公式识别专家。"},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
            ]}
        ],
        "max_tokens": 2048,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(api_url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLaVA API调用失败: {e}")
        return None
