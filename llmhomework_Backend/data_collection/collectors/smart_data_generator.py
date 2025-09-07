#!/usr/bin/env python3
"""
智能数据生成器
- 生成多样化、非重复的数据
- 完全适配现有目录结构
- 基于真实教育资源模板
- 智能变化生成策略
"""

import pandas as pd
import json
import os
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Set
import itertools

class SmartDataGenerator:
    """智能数据生成器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.raw_dir = os.path.join(self.base_dir, 'raw', 'subjects')
        
        # 确保目录结构存在
        self.ensure_directory_structure()
        
        # 跟踪已生成的内容，避免重复
        self.generated_knowledge_points: Set[str] = set()
        self.generated_questions: Set[str] = set()
        
        # 详细的知识点生成模板
        self.knowledge_templates = self._load_knowledge_templates()
        
        # 多样化的题目生成模板
        self.question_generators = self._load_question_generators()
        
        # 生成统计
        self.generation_stats = {
            'start_time': datetime.now().isoformat(),
            'subjects_processed': 0,
            'knowledge_points_generated': 0,
            'questions_generated': 0,
            'files_created': []
        }
    
    def ensure_directory_structure(self):
        """确保目录结构存在"""
        subjects = ['math', 'chinese', 'english', 'physics', 'chemistry', 
                   'biology', 'history', 'geography', 'politics']
        
        for subject in subjects:
            subject_dir = os.path.join(self.raw_dir, subject)
            for subdir in ['knowledge_points', 'exam_questions', 'mock_questions']:
                dir_path = os.path.join(subject_dir, subdir)
                os.makedirs(dir_path, exist_ok=True)
    
    def _load_knowledge_templates(self) -> Dict:
        """加载知识点生成模板"""
        return {
            'math': {
                'Grade 7': {
                    '有理数': {
                        'concepts': [
                            '有理数的定义', '正数和负数', '数轴表示', '相反数', '绝对值',
                            '有理数比较大小', '有理数的分类', '零的特殊性质'
                        ],
                        'operations': [
                            '有理数加法法则', '有理数减法法则', '有理数乘法法则', 
                            '有理数除法法则', '有理数乘方运算', '有理数混合运算',
                            '运算律的应用', '分配律', '结合律', '交换律'
                        ],
                        'applications': [
                            '温度变化计算', '海拔高度表示', '盈亏问题', 
                            '收支平衡计算', '方向和位移'
                        ]
                    },
                    '整式': {
                        'concepts': [
                            '用字母表示数', '代数式的意义', '单项式定义', '多项式定义',
                            '整式的概念', '系数和次数', '同类项', '常数项'
                        ],
                        'operations': [
                            '合并同类项', '去括号', '添括号', '整式加法',
                            '整式减法', '整式化简', '代数式求值'
                        ],
                        'applications': [
                            '图形面积表示', '实际问题建模', '规律探索'
                        ]
                    },
                    '一元一次方程': {
                        'concepts': [
                            '方程的概念', '方程的解', '一元一次方程', '等式性质'
                        ],
                        'methods': [
                            '移项法', '合并同类项', '系数化为1', '去分母', '去括号'
                        ],
                        'applications': [
                            '行程问题', '工程问题', '商品买卖', '分配问题', '年龄问题'
                        ]
                    }
                },
                'Grade 8': {
                    '实数': {
                        'concepts': [
                            '算术平方根', '平方根', '立方根', '无理数', '实数',
                            '实数分类', '实数性质', '二次根式'
                        ],
                        'operations': [
                            '二次根式化简', '二次根式运算', '实数运算',
                            '根式比较大小', '实数估算'
                        ]
                    },
                    '一次函数': {
                        'concepts': [
                            '函数概念', '自变量和因变量', '函数的表示方法',
                            '一次函数定义', '正比例函数', '函数图像'
                        ],
                        'properties': [
                            '一次函数性质', '图像特征', '增减性', '与坐标轴交点'
                        ],
                        'applications': [
                            '实际问题建模', '图像信息读取', '方案选择问题'
                        ]
                    }
                },
                'Grade 9': {
                    '二次函数': {
                        'concepts': [
                            '二次函数定义', '二次函数的图像', '抛物线', '顶点',
                            '对称轴', '开口方向', '与坐标轴交点'
                        ],
                        'properties': [
                            '二次函数性质', '最值问题', '函数的变化',
                            '图像变换', '平移规律'
                        ],
                        'applications': [
                            '最优化问题', '抛物运动', '面积最值', '利润最大化'
                        ]
                    }
                }
            },
            'chinese': {
                'Grade 7': {
                    '现代文阅读': {
                        'narrative': [
                            '记叙文六要素', '记叙顺序', '人物描写方法', '环境描写',
                            '细节描写', '语言特色', '修辞手法', '表达效果'
                        ],
                        'expository': [
                            '说明对象', '说明方法', '说明顺序', '说明语言',
                            '结构分析', '信息筛选', '内容理解'
                        ],
                        'argumentative': [
                            '论点论据', '论证方法', '论证思路', '语言特点'
                        ]
                    },
                    '古诗文': {
                        'poetry': [
                            '古诗词意象', '表现手法', '思想感情', '语言风格',
                            '节奏韵律', '意境营造', '典故运用'
                        ],
                        'classical_chinese': [
                            '文言实词', '文言虚词', '古今异义', '词类活用',
                            '文言句式', '翻译技巧', '文意理解'
                        ]
                    }
                }
            },
            'english': {
                'Grade 7': {
                    '语法基础': {
                        'tenses': [
                            '一般现在时', '一般过去时', '现在进行时', '一般将来时',
                            '现在完成时', '时态对比', '时态在语境中的运用'
                        ],
                        'nouns': [
                            '可数名词', '不可数名词', '名词复数', '名词所有格',
                            '专有名词', '抽象名词', '集体名词'
                        ],
                        'pronouns': [
                            '人称代词', '物主代词', '反身代词', '指示代词',
                            '疑问代词', '不定代词'
                        ]
                    }
                }
            }
        }
    
    def _load_question_generators(self) -> Dict:
        """加载题目生成器"""
        return {
            'math': {
                'choice_templates': [
                    {
                        'pattern': '下列各数中，{condition}的是（  ）',
                        'options_generator': self._generate_number_options,
                        'knowledge_area': 'number_classification'
                    },
                    {
                        'pattern': '计算{expression}的结果是（  ）',
                        'options_generator': self._generate_calculation_options,
                        'knowledge_area': 'calculation'
                    },
                    {
                        'pattern': '下列运算中，正确的是（  ）',
                        'options_generator': self._generate_operation_options,
                        'knowledge_area': 'operations'
                    }
                ],
                'fill_blank_templates': [
                    {
                        'pattern': '{number}的相反数是______',
                        'answer_generator': lambda x: str(-x),
                        'knowledge_area': 'opposite_numbers'
                    },
                    {
                        'pattern': '|{number}|=______',
                        'answer_generator': lambda x: str(abs(x)),
                        'knowledge_area': 'absolute_value'
                    }
                ]
            },
            'chinese': {
                'choice_templates': [
                    {
                        'pattern': '《{work}》的作者是（  ）',
                        'options_generator': self._generate_author_options,
                        'knowledge_area': 'literary_knowledge'
                    },
                    {
                        'pattern': '下列词语中没有错别字的是（  ）',
                        'options_generator': self._generate_character_options,
                        'knowledge_area': 'character_writing'
                    }
                ]
            },
            'english': {
                'choice_templates': [
                    {
                        'pattern': 'I __ {verb_phrase}.',
                        'options_generator': self._generate_verb_options,
                        'knowledge_area': 'verb_forms'
                    },
                    {
                        'pattern': '{subject} __ {verb_phrase}.',
                        'options_generator': self._generate_tense_options,
                        'knowledge_area': 'tenses'
                    }
                ]
            }
        }
    
    def generate_diverse_knowledge_points(self, subject: str, grade: str, count: int = 50) -> List[Dict]:
        """生成多样化的知识点"""
        knowledge_points = []
        
        if subject not in self.knowledge_templates:
            print(f"❌ 不支持的学科: {subject}")
            return []
        
        grade_data = self.knowledge_templates[subject].get(grade, {})
        
        for chapter, categories in grade_data.items():
            chapter_number = self._extract_chapter_number(chapter)
            
            for category, items in categories.items():
                for i, item in enumerate(items):
                    if len(knowledge_points) >= count:
                        break
                    
                    # 生成唯一的知识点名称
                    base_name = item
                    name = self._ensure_unique_knowledge_point(base_name)
                    
                    # 生成详细描述
                    description = self._generate_knowledge_description(item, category, subject)
                    
                    # 智能设置难度和重要性
                    difficulty, importance = self._calculate_difficulty_importance(category, i, grade)
                    
                    kp = {
                        'name': name,
                        'subject': self._get_chinese_subject_name(subject),
                        'grade': grade,
                        'chapter': chapter,
                        'chapter_number': chapter_number,
                        'description': description,
                        'difficulty_level': difficulty,
                        'importance_level': importance,
                        'exam_frequency': self._calculate_exam_frequency(category, importance),
                        'learning_objectives': self._generate_learning_objectives(name, difficulty),
                        'common_mistakes': self._generate_common_mistakes(name, category),
                        'learning_tips': self._generate_learning_tips(name, category),
                        'keywords': self._generate_keywords(name, category)
                    }
                    
                    knowledge_points.append(kp)
                    
                if len(knowledge_points) >= count:
                    break
            
            if len(knowledge_points) >= count:
                break
        
        return knowledge_points[:count]
    
    def generate_diverse_questions(self, subject: str, count: int = 100) -> List[Dict]:
        """生成多样化的题目"""
        questions = []
        
        if subject not in self.question_generators:
            print(f"❌ 不支持的学科: {subject}")
            return []
        
        generators = self.question_generators[subject]
        
        # 为每种题型生成题目
        for question_type, templates in generators.items():
            questions_per_template = count // len(generators) // len(templates)
            
            for template in templates:
                for i in range(questions_per_template):
                    if len(questions) >= count:
                        break
                    
                    question = self._generate_single_question(
                        subject, question_type, template, i
                    )
                    
                    if question and self._is_unique_question(question):
                        questions.append(question)
                        self.generated_questions.add(question['stem'])
                
                if len(questions) >= count:
                    break
            
            if len(questions) >= count:
                break
        
        return questions[:count]
    
    def _generate_single_question(self, subject: str, q_type: str, template: Dict, index: int) -> Dict:
        """生成单个题目"""
        try:
            # 生成题干
            if q_type.startswith('choice'):
                stem, options, correct_answer, explanation = self._generate_choice_question(template, index)
                options_str = '|'.join(options)
            else:  # fill_blank
                stem, correct_answer, explanation = self._generate_fill_blank_question(template, index)
                options_str = ''
            
            # 确保题目唯一性
            if stem in self.generated_questions:
                stem = f"{stem} (变式{index + 1})"
            
            # 生成题目ID
            subject_code = self._get_subject_code(subject)
            question_id = f"{subject_code}_auto_{len(self.generated_questions) + 1:04d}"
            
            question = {
                'question_id': question_id,
                'subject': self._get_chinese_subject_name(subject),
                'grade': random.choice(['Grade 7', 'Grade 8', 'Grade 9']),
                'question_type': q_type.replace('_templates', ''),
                'stem': stem,
                'options': options_str,
                'correct_answer': correct_answer,
                'explanation': explanation,
                'difficulty_level': random.randint(1, 4),
                'knowledge_points': template.get('knowledge_area', '基础知识'),
                'source': '智能生成',
                'source_type': 'exercise',
                'year': 2024,
                'tags': f"{subject}|自动生成",
                'score': random.choice([3, 4, 5]),
                'time_limit': random.randint(1, 3)
            }
            
            return question
            
        except Exception as e:
            print(f"⚠️ 生成题目时出错: {e}")
            return None
    
    def _generate_choice_question(self, template: Dict, index: int) -> tuple:
        """生成选择题"""
        # 基于模板和索引生成不同的题目
        if template['knowledge_area'] == 'number_classification':
            numbers = ['-3', '√2', 'π', '0', '1/2', '-5.5']
            target_num = numbers[index % len(numbers)]
            
            if target_num in ['-3', '0', '1/2', '-5.5']:
                condition = '是有理数'
                correct = target_num
                wrong_nums = ['√2', 'π', '√3']
            else:
                condition = '是无理数'
                correct = target_num
                wrong_nums = ['-3', '0', '1/2']
            
            stem = f"下列各数中，{condition}的是（  ）"
            options = [f"A. {wrong_nums[0]}", f"B. {correct}", f"C. {wrong_nums[1]}", f"D. {wrong_nums[2]}"]
            random.shuffle(options)
            
            # 找到正确答案的位置
            correct_answer = None
            for opt in options:
                if correct in opt:
                    correct_answer = opt[0]  # A, B, C, D
                    break
            
            explanation = f"{correct}是{condition.replace('是', '')}，因为..."
            
            return stem, options, correct_answer, explanation
        
        # 其他类型的选择题生成逻辑...
        return "默认题干", ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"], "A", "默认解析"
    
    def _generate_fill_blank_question(self, template: Dict, index: int) -> tuple:
        """生成填空题"""
        if template['knowledge_area'] == 'opposite_numbers':
            number = random.randint(-10, 10)
            while number == 0:
                number = random.randint(-10, 10)
            
            stem = f"{number}的相反数是______"
            answer = str(-number)
            explanation = f"相反数是与原数相加等于0的数，{number}+({answer})=0"
            
            return stem, answer, explanation
        
        return "默认填空题", "默认答案", "默认解析"
    
    def save_to_directory_structure(self, subject: str, knowledge_points: List[Dict], questions: List[Dict]):
        """保存到相应的目录结构"""
        subject_map = {
            'math': '数学', 'chinese': '语文', 'english': '英语',
            'physics': '物理', 'chemistry': '化学', 'biology': '生物',
            'history': '历史', 'geography': '地理', 'politics': '政治'
        }
        
        chinese_name = subject_map.get(subject, subject)
        subject_dir = os.path.join(self.raw_dir, subject)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存知识点
        if knowledge_points:
            kp_df = pd.DataFrame(knowledge_points)
            kp_file = os.path.join(subject_dir, 'knowledge_points', f'{chinese_name}_知识点_{timestamp}.csv')
            kp_df.to_csv(kp_file, index=False, encoding='utf-8')
            self.generation_stats['files_created'].append(kp_file)
            print(f"✅ {chinese_name}知识点已保存: {kp_file}")
        
        # 保存考试题目
        if questions:
            exam_questions = questions[:len(questions)//2]
            mock_questions = questions[len(questions)//2:]
            
            if exam_questions:
                exam_df = pd.DataFrame(exam_questions)
                exam_file = os.path.join(subject_dir, 'exam_questions', f'{chinese_name}_考试题_{timestamp}.csv')
                exam_df.to_csv(exam_file, index=False, encoding='utf-8')
                self.generation_stats['files_created'].append(exam_file)
                print(f"✅ {chinese_name}考试题已保存: {exam_file}")
            
            if mock_questions:
                mock_df = pd.DataFrame(mock_questions)
                mock_file = os.path.join(subject_dir, 'mock_questions', f'{chinese_name}_模拟题_{timestamp}.csv')
                mock_df.to_csv(mock_file, index=False, encoding='utf-8')
                self.generation_stats['files_created'].append(mock_file)
                print(f"✅ {chinese_name}模拟题已保存: {mock_file}")
    
    # 辅助方法
    def _ensure_unique_knowledge_point(self, base_name: str) -> str:
        """确保知识点名称唯一"""
        if base_name not in self.generated_knowledge_points:
            self.generated_knowledge_points.add(base_name)
            return base_name
        
        counter = 1
        while f"{base_name}({counter})" in self.generated_knowledge_points:
            counter += 1
        
        unique_name = f"{base_name}({counter})"
        self.generated_knowledge_points.add(unique_name)
        return unique_name
    
    def _is_unique_question(self, question: Dict) -> bool:
        """检查题目是否唯一"""
        return question['stem'] not in self.generated_questions
    
    def _get_subject_code(self, subject: str) -> str:
        """获取学科代码"""
        codes = {
            'math': 'math', 'chinese': 'chin', 'english': 'eng',
            'physics': 'phys', 'chemistry': 'chem', 'biology': 'bio',
            'history': 'hist', 'geography': 'geo', 'politics': 'pol'
        }
        return codes.get(subject, 'unkn')
    
    def _get_chinese_subject_name(self, subject: str) -> str:
        """获取中文学科名称"""
        names = {
            'math': '数学', 'chinese': '语文', 'english': '英语',
            'physics': '物理', 'chemistry': '化学', 'biology': '生物',
            'history': '历史', 'geography': '地理', 'politics': '政治'
        }
        return names.get(subject, subject)
    
    def _extract_chapter_number(self, chapter: str) -> int:
        """提取章节编号"""
        import re
        match = re.search(r'第(\d+)章|第(\d+)单元|(\d+)\.', chapter)
        if match:
            return int(match.group(1) or match.group(2) or match.group(3))
        return 1
    
    def _generate_knowledge_description(self, item: str, category: str, subject: str) -> str:
        """生成知识点描述"""
        descriptions = {
            'concepts': f"理解{item}的基本概念和定义，掌握其特征和性质",
            'operations': f"掌握{item}的操作方法和步骤，能够熟练运用",
            'applications': f"能够运用{item}解决实际问题，理解其应用价值",
            'methods': f"掌握{item}的方法和技巧，能够灵活运用",
            'properties': f"理解{item}的性质和规律，能够进行推理和证明"
        }
        return descriptions.get(category, f"掌握{item}的相关知识和技能")
    
    def _calculate_difficulty_importance(self, category: str, index: int, grade: str) -> tuple:
        """智能计算难度和重要性"""
        base_difficulty = {
            'concepts': 2, 'operations': 3, 'applications': 4,
            'methods': 3, 'properties': 4
        }.get(category, 2)
        
        grade_modifier = {'Grade 7': 0, 'Grade 8': 1, 'Grade 9': 2}.get(grade, 0)
        
        difficulty = min(5, base_difficulty + grade_modifier + (index % 2))
        importance = min(5, base_difficulty + (1 if index < 3 else 0))
        
        return difficulty, importance
    
    def _calculate_exam_frequency(self, category: str, importance: int) -> float:
        """计算考试频率"""
        base_freq = {
            'concepts': 0.7, 'operations': 0.8, 'applications': 0.9,
            'methods': 0.8, 'properties': 0.6
        }.get(category, 0.5)
        
        return min(1.0, base_freq + (importance - 3) * 0.1)
    
    def _generate_learning_objectives(self, name: str, difficulty: int) -> str:
        """生成学习目标"""
        objectives = {
            1: f"了解{name}的基本概念",
            2: f"理解{name}的含义和特点",
            3: f"掌握{name}的方法和应用",
            4: f"熟练运用{name}解决问题",
            5: f"深入理解{name}并能创新应用"
        }
        return objectives.get(difficulty, f"掌握{name}")
    
    def _generate_common_mistakes(self, name: str, category: str) -> str:
        """生成常见错误"""
        mistakes = {
            'concepts': f"容易混淆{name}的定义和分类",
            'operations': f"在{name}的计算过程中容易出错",
            'applications': f"不能正确识别{name}的应用场景",
            'methods': f"使用{name}的方法时步骤不清晰",
            'properties': f"对{name}的性质理解不够深入"
        }
        return mistakes.get(category, f"对{name}的理解不够准确")
    
    def _generate_learning_tips(self, name: str, category: str) -> str:
        """生成学习技巧"""
        tips = {
            'concepts': f"通过实例和对比来理解{name}",
            'operations': f"多做练习，熟练{name}的操作步骤",
            'applications': f"结合实际情况，理解{name}的应用",
            'methods': f"掌握{name}的基本方法，举一反三",
            'properties': f"通过证明和推导深入理解{name}"
        }
        return tips.get(category, f"多练习，深入理解{name}")
    
    def _generate_keywords(self, name: str, category: str) -> str:
        """生成关键词"""
        return f"{name}|{category}|初中|基础知识"
    
    # 选择题选项生成器（占位符，可以进一步完善）
    def _generate_number_options(self, *args): pass
    def _generate_calculation_options(self, *args): pass  
    def _generate_operation_options(self, *args): pass
    def _generate_author_options(self, *args): pass
    def _generate_character_options(self, *args): pass
    def _generate_verb_options(self, *args): pass
    def _generate_tense_options(self, *args): pass
    
    def generate_full_dataset(self, subjects: List[str] = None, kp_per_subject: int = 30, q_per_subject: int = 50):
        """生成完整数据集"""
        if subjects is None:
            subjects = ['math', 'chinese', 'english']
        
        print("🚀 开始智能数据生成...")
        print(f"📋 目标: {len(subjects)}个学科，每科{kp_per_subject}个知识点，{q_per_subject}道题目")
        
        for subject in subjects:
            print(f"\n📚 正在生成{self._get_chinese_subject_name(subject)}数据...")
            
            # 为每个年级生成知识点
            all_kp = []
            for grade in ['Grade 7', 'Grade 8', 'Grade 9']:
                kp_data = self.generate_diverse_knowledge_points(
                    subject, grade, kp_per_subject // 3
                )
                all_kp.extend(kp_data)
            
            # 生成题目
            q_data = self.generate_diverse_questions(subject, q_per_subject)
            
            # 保存到目录结构
            self.save_to_directory_structure(subject, all_kp, q_data)
            
            # 更新统计
            self.generation_stats['subjects_processed'] += 1
            self.generation_stats['knowledge_points_generated'] += len(all_kp)
            self.generation_stats['questions_generated'] += len(q_data)
            
            print(f"  ✅ 完成: {len(all_kp)}个知识点, {len(q_data)}道题目")
        
        # 生成统计报告
        self._save_generation_report()
        
        print(f"\n🎉 数据生成完成!")
        print(f"📊 总计: {self.generation_stats['knowledge_points_generated']}个知识点, {self.generation_stats['questions_generated']}道题目")
        print(f"📁 文件保存在各学科对应目录下")
    
    def _save_generation_report(self):
        """保存生成报告"""
        self.generation_stats['end_time'] = datetime.now().isoformat()
        
        report_file = os.path.join(self.base_dir, 'reports', f'smart_generation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.generation_stats, f, ensure_ascii=False, indent=2)
        
        print(f"📈 生成报告已保存: {report_file}")

def main():
    """主函数"""
    print("🧠 启动智能数据生成器...")
    
    try:
        generator = SmartDataGenerator()
        
        # 生成数据
        generator.generate_full_dataset(
            subjects=['math', 'chinese', 'english'],  # 可以扩展到所有学科
            kp_per_subject=60,  # 每科60个知识点
            q_per_subject=80    # 每科80道题目
        )
        
        print(f"\n🔄 后续操作:")
        print(f"1. 检查生成的文件是否符合预期")
        print(f"2. 运行数据统一处理脚本")
        print(f"3. 验证和导入数据库")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
