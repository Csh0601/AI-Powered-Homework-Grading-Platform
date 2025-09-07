#!/usr/bin/env python3
"""
创建高质量种子数据
手动编写真实的教育数据作为基础
"""

import pandas as pd
import os
from datetime import datetime

def create_high_quality_math_data():
    """创建高质量数学数据"""
    
    # 高质量数学知识点
    knowledge_points = [
        {
            'id': 'math_kp_001',
            'name': '有理数的概念',
            'subject': '数学',
            'grade': 'Grade 7',
            'chapter': '第一章 有理数',
            'chapter_number': 1,
            'description': '理解有理数的定义，掌握正数、负数和零的概念，能够识别和分类有理数',
            'difficulty_level': 2,
            'importance_level': 5,
            'exam_frequency': 0.9,
            'learning_objectives': '能够正确识别有理数，理解有理数在实际生活中的意义',
            'common_mistakes': '混淆有理数和无理数，不理解零的性质',
            'learning_tips': '通过数轴和实际例子理解有理数概念',
            'keywords': '有理数|正数|负数|零|分数|整数'
        },
        {
            'id': 'math_kp_002',
            'name': '数轴',
            'subject': '数学',
            'grade': 'Grade 7',
            'chapter': '第一章 有理数',
            'chapter_number': 1,
            'description': '掌握数轴的概念，理解数轴上点与有理数的一一对应关系',
            'difficulty_level': 3,
            'importance_level': 4,
            'exam_frequency': 0.75,
            'learning_objectives': '能够在数轴上表示有理数，利用数轴比较数的大小',
            'common_mistakes': '不理解数轴的三要素，混淆点的坐标',
            'learning_tips': '记住数轴三要素：原点、正方向、单位长度',
            'keywords': '数轴|原点|正方向|单位长度|坐标'
        },
        {
            'id': 'math_kp_003',
            'name': '有理数的加法',
            'subject': '数学',
            'grade': 'Grade 7',
            'chapter': '第一章 有理数',
            'chapter_number': 1,
            'description': '掌握有理数加法法则，能够进行有理数的加法运算',
            'difficulty_level': 3,
            'importance_level': 5,
            'exam_frequency': 0.85,
            'learning_objectives': '熟练掌握同号、异号有理数的加法运算',
            'common_mistakes': '符号处理错误，不理解加法交换律和结合律',
            'learning_tips': '同号相加取相同符号，异号相加取绝对值大的符号',
            'keywords': '有理数加法|同号|异号|绝对值|运算法则'
        },
        {
            'id': 'math_kp_004',
            'name': '一元一次方程',
            'subject': '数学',
            'grade': 'Grade 7',
            'chapter': '第三章 一元一次方程',
            'chapter_number': 3,
            'description': '理解一元一次方程的概念，掌握解一元一次方程的方法',
            'difficulty_level': 4,
            'importance_level': 5,
            'exam_frequency': 0.95,
            'learning_objectives': '能够识别一元一次方程，熟练求解一元一次方程',
            'common_mistakes': '移项时符号错误，合并同类项出错',
            'learning_tips': '移项要变号，系数化为1',
            'keywords': '一元一次方程|移项|合并同类项|解方程'
        },
        {
            'id': 'math_kp_005',
            'name': '二次函数',
            'subject': '数学',
            'grade': 'Grade 9',
            'chapter': '第二十二章 二次函数',
            'chapter_number': 22,
            'description': '理解二次函数的定义，掌握二次函数的图像和性质',
            'difficulty_level': 5,
            'importance_level': 5,
            'exam_frequency': 0.98,
            'learning_objectives': '能够画出二次函数图像，分析二次函数的性质',
            'common_mistakes': '不理解开口方向与a的关系，混淆顶点坐标公式',
            'learning_tips': 'a>0开口向上，a<0开口向下；顶点坐标为(-b/2a, (4ac-b²)/4a)',
            'keywords': '二次函数|抛物线|开口方向|顶点|对称轴'
        }
    ]
    
    # 高质量数学题目
    questions = [
        {
            'question_id': 'math_q_001',
            'subject': '数学',
            'grade': 'Grade 7',
            'question_type': 'choice',
            'stem': '下列数中，有理数是（  ）',
            'options': ['A. π', 'B. √2', 'C. -1/3', 'D. √3'],
            'correct_answer': 'C',
            'explanation': '有理数包括正有理数、负有理数和零。-1/3是分数，属于有理数。π、√2、√3都是无理数。',
            'difficulty_level': 2,
            'knowledge_points': ['有理数的概念'],
            'source': '手工编写',
            'tags': ['基础概念', '分类识别']
        },
        {
            'question_id': 'math_q_002',
            'subject': '数学',
            'grade': 'Grade 7',
            'question_type': 'fill_blank',
            'stem': '在数轴上，点A表示的数是-3，点B表示的数是2，则线段AB的长度是______。',
            'options': [],
            'correct_answer': '5',
            'explanation': '线段AB的长度等于两点坐标差的绝对值，即|2-(-3)|=|5|=5。',
            'difficulty_level': 3,
            'knowledge_points': ['数轴'],
            'source': '手工编写',
            'tags': ['数轴应用', '距离计算']
        },
        {
            'question_id': 'math_q_003',
            'subject': '数学',
            'grade': 'Grade 7',
            'question_type': 'calculation',
            'stem': '计算：(-3) + 5 + (-7) + 2',
            'options': [],
            'correct_answer': '-3',
            'explanation': '按照有理数加法法则：(-3) + 5 + (-7) + 2 = (-3 - 7) + (5 + 2) = -10 + 7 = -3',
            'difficulty_level': 3,
            'knowledge_points': ['有理数的加法'],
            'source': '手工编写',
            'tags': ['运算', '有理数加法']
        },
        {
            'question_id': 'math_q_004',
            'subject': '数学',
            'grade': 'Grade 7',
            'question_type': 'calculation',
            'stem': '解方程：2x + 3 = 7',
            'options': [],
            'correct_answer': 'x = 2',
            'explanation': '移项得：2x = 7 - 3，即2x = 4，所以x = 2',
            'difficulty_level': 3,
            'knowledge_points': ['一元一次方程'],
            'source': '手工编写',
            'tags': ['解方程', '移项']
        },
        {
            'question_id': 'math_q_005',
            'subject': '数学',
            'grade': 'Grade 9',
            'question_type': 'choice',
            'stem': '二次函数y = -2x² + 4x + 1的对称轴是（  ）',
            'options': ['A. x = 1', 'B. x = -1', 'C. x = 2', 'D. x = -2'],
            'correct_answer': 'A',
            'explanation': '对称轴公式为x = -b/(2a)，这里a = -2，b = 4，所以x = -4/(2×(-2)) = 1',
            'difficulty_level': 4,
            'knowledge_points': ['二次函数'],
            'source': '手工编写',
            'tags': ['二次函数', '对称轴']
        }
    ]
    
    return knowledge_points, questions

def create_high_quality_chinese_data():
    """创建高质量语文数据"""
    
    knowledge_points = [
        {
            'id': 'chinese_kp_001',
            'name': '记叙文阅读理解',
            'subject': '语文',
            'grade': 'Grade 7',
            'chapter': '现代文阅读',
            'chapter_number': 1,
            'description': '掌握记叙文的六要素，理解记叙顺序和人称，能够分析文章结构',
            'difficulty_level': 3,
            'importance_level': 5,
            'exam_frequency': 0.9,
            'learning_objectives': '能够分析记叙文的结构和内容，概括文章主旨',
            'common_mistakes': '不能准确概括文章主旨，混淆记叙顺序',
            'learning_tips': '抓住文章的时间、地点、人物、事件、原因、结果',
            'keywords': '记叙文|六要素|记叙顺序|人称|主旨'
        },
        {
            'id': 'chinese_kp_002',
            'name': '古诗词鉴赏',
            'subject': '语文',
            'grade': 'Grade 8',
            'chapter': '古代诗歌阅读',
            'chapter_number': 2,
            'description': '理解古诗词的思想感情，掌握常见的表现手法和修辞手法',
            'difficulty_level': 4,
            'importance_level': 5,
            'exam_frequency': 0.85,
            'learning_objectives': '能够分析诗歌的思想感情和艺术特色',
            'common_mistakes': '不理解诗歌的时代背景，混淆表现手法',
            'learning_tips': '结合时代背景理解诗歌，注意关键词的含义',
            'keywords': '古诗词|思想感情|表现手法|修辞手法|意境'
        }
    ]
    
    questions = [
        {
            'question_id': 'chinese_q_001',
            'subject': '语文',
            'grade': 'Grade 7',
            'question_type': 'choice',
            'stem': '《朝花夕拾》的作者是（  ）',
            'options': ['A. 鲁迅', 'B. 老舍', 'C. 巴金', 'D. 茅盾'],
            'correct_answer': 'A',
            'explanation': '《朝花夕拾》是鲁迅的回忆性散文集，收录了他青少年时期的回忆。',
            'difficulty_level': 2,
            'knowledge_points': ['文学常识'],
            'source': '手工编写',
            'tags': ['文学常识', '作家作品']
        },
        {
            'question_id': 'chinese_q_002',
            'subject': '语文',
            'grade': 'Grade 8',
            'question_type': 'application',
            'stem': '阅读下面的诗句："春风又绿江南岸，明月何时照我还？"这里运用了什么修辞手法？表达了诗人怎样的情感？',
            'options': [],
            'correct_answer': '运用了拟人的修辞手法，"绿"字把春风拟人化，生动形象。表达了诗人思念家乡、盼望归家的情感。',
            'explanation': '"绿"字是动词，把春风人格化，具有了使江南变绿的能力，这是拟人修辞。诗人通过对故乡春景的描写，表达了对家乡的思念。',
            'difficulty_level': 4,
            'knowledge_points': ['古诗词鉴赏'],
            'source': '手工编写',
            'tags': ['修辞手法', '诗歌鉴赏', '情感分析']
        }
    ]
    
    return knowledge_points, questions

def save_quality_data():
    """保存高质量数据"""
    print("🎯 开始创建高质量种子数据...")
    
    # 创建保存目录
    base_dir = os.path.join(os.path.dirname(__file__), "quality_seed_data")
    os.makedirs(base_dir, exist_ok=True)
    
    # 获取数据
    math_kp, math_q = create_high_quality_math_data()
    chinese_kp, chinese_q = create_high_quality_chinese_data()
    
    # 合并数据
    all_kp = math_kp + chinese_kp
    all_q = math_q + chinese_q
    
    # 保存知识点
    kp_df = pd.DataFrame(all_kp)
    kp_file = os.path.join(base_dir, f"quality_knowledge_points_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    kp_df.to_csv(kp_file, index=False, encoding='utf-8')
    print(f"✅ 高质量知识点已保存: {kp_file}")
    print(f"   📊 共 {len(all_kp)} 个知识点")
    
    # 保存题目
    q_df = pd.DataFrame(all_q)
    q_file = os.path.join(base_dir, f"quality_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    q_df.to_csv(q_file, index=False, encoding='utf-8')
    print(f"✅ 高质量题目已保存: {q_file}")
    print(f"   📊 共 {len(all_q)} 道题目")
    
    return kp_file, q_file

if __name__ == "__main__":
    save_quality_data()
    print("\n🎉 高质量种子数据创建完成！")
    print("\n📋 下一步建议:")
    print("1. 检查生成的数据质量")
    print("2. 将数据移动到processed目录")
    print("3. 导入数据库")
    print("4. 基于这些种子数据扩展更多内容")
