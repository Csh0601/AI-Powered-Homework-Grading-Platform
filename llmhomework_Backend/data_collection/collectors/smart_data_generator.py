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
from datetime import datetime
from typing import List, Dict, Any, Set

class SmartDataGenerator:
    """智能数据生成器"""
    
    def __init__(self, use_cache: bool = True):
        self.base_dir = os.path.dirname(__file__)
        self.raw_dir = os.path.join(self.base_dir, '..', '..', 'raw', 'subjects')  # 修正路径
        self.use_cache = use_cache

        # 确保目录结构存在
        self.ensure_directory_structure()

        # 持久化存储已生成的内容，避免重复
        self.generated_cache_file = os.path.join(self.base_dir, 'generated_cache.json')

        if use_cache:
            self.generated_knowledge_points: Set[str] = self._load_generated_cache()
        else:
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

    def _load_generated_cache(self) -> Set[str]:
        """加载已生成的知识点缓存"""
        try:
            if os.path.exists(self.generated_cache_file):
                with open(self.generated_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('knowledge_points', []))
        except Exception as e:
            print(f"⚠️ 加载缓存失败: {e}")
        return set()

    def _save_generated_cache(self):
        """保存已生成的知识点缓存"""
        try:
            cache_data = {
                'knowledge_points': list(self.generated_knowledge_points),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.generated_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")
    
    def ensure_directory_structure(self):
        """确保目录结构存在"""
        subjects = ['math', 'chinese', 'english', 'physics', 'chemistry',
                   'biology', 'history', 'geography', 'politics']

        for subject in subjects:
            subject_dir = os.path.join(self.raw_dir, subject)
            for subdir in ['knowledge_points', 'exam_questions', 'mock_questions']:
                dir_path = os.path.join(subject_dir, subdir)
                os.makedirs(dir_path, exist_ok=True)

        # 确保reports目录存在
        reports_dir = os.path.join(self.base_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
    
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
            },
            'physics': {
                'Grade 7': {
                    '力学基础': {
                        'concepts': [
                            '力的概念', '力的三要素', '力的单位', '力的分类',
                            '重力', '摩擦力', '弹力', '力的合成与分解'
                        ],
                        'properties': [
                            '力的方向', '力的作用点', '力的效果', '力的平衡',
                            '力的测量', '力的图示', '力的计算'
                        ],
                        'applications': [
                            '日常生活中的力', '交通中的力', '体育运动中的力'
                        ]
                    },
                    '运动学': {
                        'concepts': [
                            '机械运动', '参照物', '运动的相对性', '路程和位移',
                            '速度', '平均速度', '瞬时速度', '加速度'
                        ],
                        'measurements': [
                            '速度测量', '时间测量', '距离测量', '运动状态判断'
                        ],
                        'applications': [
                            '交通速度计算', '体育运动分析', '机械运动分析'
                        ]
                    }
                },
                'Grade 8': {
                    '光学': {
                        'concepts': [
                            '光的直线传播', '光的反射', '光的折射', '光的色散',
                            '平面镜成像', '凸透镜成像', '凹透镜成像'
                        ],
                        'laws': [
                            '光的反射定律', '光的折射定律', '全反射现象',
                            '光的颜色', '光的波粒二象性'
                        ],
                        'applications': [
                            '照相机原理', '显微镜原理', '眼镜的用途'
                        ]
                    },
                    '热学': {
                        'concepts': [
                            '温度', '热量', '比热容', '热传递',
                            '物态变化', '热机', '热效率'
                        ],
                        'measurements': [
                            '温度测量', '热量计算', '效率计算'
                        ],
                        'applications': [
                            '日常生活中的热', '工业中的热', '环境保护'
                        ]
                    }
                }
            },
            'chemistry': {
                'Grade 7': {
                    '物质的性质': {
                        'concepts': [
                            '物质的三态', '物理性质', '化学性质', '物质的分类',
                            '元素', '化合物', '混合物', '纯净物'
                        ],
                        'identification': [
                            '物质的鉴别', '性质的观察', '实验的设计'
                        ],
                        'applications': [
                            '日常生活中的物质', '工业生产中的物质'
                        ]
                    },
                    '化学反应': {
                        'concepts': [
                            '化学反应的特征', '化学反应的类型', '化学方程式',
                            '质量守恒定律', '反应物和生成物'
                        ],
                        'equations': [
                            '化学方程式的书写', '化学方程式的配平',
                            '化学方程式的意义'
                        ],
                        'applications': [
                            '工业生产中的反应', '环境保护中的反应'
                        ]
                    }
                },
                'Grade 8': {
                    '元素化合物': {
                        'concepts': [
                            '金属', '非金属', '金属活动性', '置换反应',
                            '化合反应', '分解反应', '复分解反应'
                        ],
                        'properties': [
                            '金属的物理性质', '金属的化学性质',
                            '非金属的物理性质', '非金属的化学性质'
                        ],
                        'applications': [
                            '金属在生活中的应用', '非金属在生活中的应用'
                        ]
                    },
                    '溶液': {
                        'concepts': [
                            '溶液的组成', '溶液的浓度', '溶解度', '饱和溶液',
                            '不饱和溶液', '溶剂和溶质'
                        ],
                        'calculations': [
                            '溶液浓度的计算', '溶解度的计算', '稀释和浓缩'
                        ],
                        'applications': [
                            '日常生活中的溶液', '工业生产中的溶液'
                        ]
                    }
                }
            },
            'biology': {
                'Grade 7': {
                    '生命的基础': {
                        'concepts': [
                            '生命的特征', '生物的分类', '细胞的基本结构',
                            '细胞的生理功能', '新陈代谢', '生长发育'
                        ],
                        'structures': [
                            '细胞壁', '细胞膜', '细胞质', '细胞核',
                            '细胞器', '组织器官系统'
                        ],
                        'processes': [
                            '光合作用', '呼吸作用', '物质运输', '能量转换'
                        ]
                    },
                    '生物多样性': {
                        'concepts': [
                            '生物的多样性', '生态系统', '食物链', '食物网',
                            '生物与环境', '环境保护'
                        ],
                        'ecosystems': [
                            '生态平衡', '生物圈', '环境保护', '可持续发展'
                        ],
                        'applications': [
                            '环境保护', '资源利用', '生态保护'
                        ]
                    }
                },
                'Grade 8': {
                    '遗传与进化': {
                        'concepts': [
                            '遗传信息的传递', 'DNA和RNA', '基因', '染色体',
                            '遗传规律', '变异', '进化'
                        ],
                        'mechanisms': [
                            '减数分裂', '有丝分裂', '基因重组', '自然选择'
                        ],
                        'applications': [
                            '遗传病预防', '育种技术', '进化理论'
                        ]
                    },
                    '人体生理': {
                        'concepts': [
                            '消化系统', '呼吸系统', '循环系统', '神经系统',
                            '内分泌系统', '生殖系统', '免疫系统'
                        ],
                        'functions': [
                            '各系统的功能', '系统间的协调', '人体稳态'
                        ],
                        'health': [
                            '健康生活方式', '疾病预防', '医疗保健'
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
            },
            'physics': {
                'choice_templates': [
                    {
                        'pattern': '下列关于{concept}的说法，正确的是（  ）',
                        'options_generator': self._generate_physics_concept_options,
                        'knowledge_area': 'physics_concepts'
                    },
                    {
                        'pattern': '一个质量为{value}的物体，{situation}，其{property}是多少？',
                        'options_generator': self._generate_physics_calculation_options,
                        'knowledge_area': 'physics_calculations'
                    }
                ],
                'fill_blank_templates': [
                    {
                        'pattern': '力的单位是______',
                        'answer_generator': lambda: '牛顿',
                        'knowledge_area': 'force_units'
                    },
                    {
                        'pattern': '速度的计算公式是______',
                        'answer_generator': lambda: 'v = s/t',
                        'knowledge_area': 'speed_formula'
                    }
                ]
            },
            'chemistry': {
                'choice_templates': [
                    {
                        'pattern': '下列物质中，{property}的是（  ）',
                        'options_generator': self._generate_chemistry_property_options,
                        'knowledge_area': 'chemistry_properties'
                    },
                    {
                        'pattern': '化学反应{reaction_type}的特征是（  ）',
                        'options_generator': self._generate_chemistry_reaction_options,
                        'knowledge_area': 'chemistry_reactions'
                    }
                ],
                'fill_blank_templates': [
                    {
                        'pattern': '化学方程式的配平原则是______',
                        'answer_generator': lambda: '质量守恒定律',
                        'knowledge_area': 'balancing_equations'
                    },
                    {
                        'pattern': '溶液的浓度单位有______',
                        'answer_generator': lambda: 'mol/L、g/L等',
                        'knowledge_area': 'solution_concentration'
                    }
                ]
            },
            'biology': {
                'choice_templates': [
                    {
                        'pattern': '细胞的{structure}功能是（  ）',
                        'options_generator': self._generate_biology_structure_options,
                        'knowledge_area': 'cell_structure'
                    },
                    {
                        'pattern': '生态系统中，{role}的是（  ）',
                        'options_generator': self._generate_biology_ecology_options,
                        'knowledge_area': 'ecology'
                    }
                ],
                'fill_blank_templates': [
                    {
                        'pattern': '光合作用的反应式是______',
                        'answer_generator': lambda: 'CO₂ + H₂O → C₆H₁₂O₆ + O₂',
                        'knowledge_area': 'photosynthesis'
                    },
                    {
                        'pattern': 'DNA的全称是______',
                        'answer_generator': lambda: '脱氧核糖核酸',
                        'knowledge_area': 'dna_structure'
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
            # 有理数与无理数分类
            numbers = ['-3', '√2', 'π', '0', '1/2', '-5.5', '√3', '3.14']
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

            explanation = f"{correct}是{condition.replace('是', '')}，因为{self._get_number_classification_explanation(correct)}"

            return stem, options, correct_answer, explanation

        elif template['knowledge_area'] == 'calculation':
            # 数值计算题目
            calculations = [
                ('(-3) + 5', '2'),
                ('8 - (-2)', '10'),
                ('3 × (-4)', '-12'),
                ('(-6) ÷ 2', '-3'),
                ('(-2)²', '4'),
                ('|-5|', '5')
            ]
            calc, answer = calculations[index % len(calculations)]
            stem = f"计算{calc}的结果是（  ）"

            # 生成相似但错误的选项
            wrong_answers = []
            if calc.startswith('(-3)'):
                wrong_answers = ['-2', '-8', '8']
            elif '×' in calc:
                wrong_answers = ['12', '-3', '4']
            elif '÷' in calc:
                wrong_answers = ['3', '-6', '2']
            else:
                wrong_answers = ['-4', '6', '-6']

            options = [f"A. {wrong_answers[0]}", f"B. {wrong_answers[1]}", f"C. {answer}", f"D. {wrong_answers[2]}"]
            random.shuffle(options)

            # 找到正确答案的位置
            correct_answer = None
            for opt in options:
                if answer in opt:
                    correct_answer = opt[0]
                    break

            explanation = f"{calc}的计算过程：{self._get_calculation_explanation(calc)} = {answer}"
            return stem, options, correct_answer, explanation

        elif template['knowledge_area'] == 'operations':
            # 运算规则题目
            operations = [
                ('有理数加法交换律', 'a + b = b + a'),
                ('有理数乘法交换律', 'a × b = b × a'),
                ('有理数乘法结合律', '(a × b) × c = a × (b × c)'),
                ('加法分配律', 'a × (b + c) = a × b + a × c')
            ]
            concept, rule = operations[index % len(operations)]
            stem = f"下列属于{concept}的是（  ）"

            # 生成错误的运算规则
            wrong_rules = []
            if '交换律' in concept:
                wrong_rules = ['a + b = a - b', 'a × b = a ÷ b', 'a + b = b - a']
            elif '结合律' in concept:
                wrong_rules = ['(a + b) + c = a + (b - c)', 'a × (b × c) = (a × b) × c', '(a × b) × c = a × (b + c)']
            else:
                wrong_rules = ['a × (b + c) = a × b - a × c', 'a + (b × c) = (a + b) × (a + c)', 'a × (b - c) = a × b - a × c']

            options = [f"A. {wrong_rules[0]}", f"B. {wrong_rules[1]}", f"C. {rule}", f"D. {wrong_rules[2]}"]
            random.shuffle(options)

            # 找到正确答案的位置
            correct_answer = None
            for opt in options:
                if rule in opt:
                    correct_answer = opt[0]
                    break

            explanation = f"{concept}的正确表述是：{rule}，这是有理数运算的基本规律"
            return stem, options, correct_answer, explanation


        # 其他学科的题目生成
        knowledge_area = template.get('knowledge_area', '')

        if knowledge_area == 'physics_concepts':
            concept = ['力的概念', '光的反射', '机械运动', '牛顿第一定律'][index % 4]
            options, correct_answer, explanation = self._generate_physics_concept_options(concept, index)
            return f"下列关于{concept}的说法，正确的是（  ）", options, correct_answer, explanation

        elif knowledge_area == 'physics_calculations':
            values = ['5kg', '10m/s', '100J', '20°C']
            situations = ['在水平地面上静止', '自由下落', '加热过程', '恒温过程']
            properties = ['重力', '速度', '内能', '温度']

            value = values[index % len(values)]
            situation = situations[index % len(situations)]
            property_name = properties[index % len(properties)]

            options, correct_answer, explanation = self._generate_physics_calculation_options(value, situation, property_name, index)
            return f"一个{property_name}为{value}的物体，{situation}，其{property_name}是多少？", options, correct_answer, explanation

        elif knowledge_area == 'chemistry_properties':
            properties = ['金属', '酸', '碱', '盐']
            property_name = properties[index % len(properties)]
            options, correct_answer, explanation = self._generate_chemistry_property_options(property_name, index)
            return f"下列物质中，{property_name}的是（  ）", options, correct_answer, explanation

        elif knowledge_area == 'chemistry_reactions':
            reactions = ['氧化反应', '还原反应', '化合反应']
            reaction_type = reactions[index % len(reactions)]
            options, correct_answer, explanation = self._generate_chemistry_reaction_options(reaction_type, index)
            return f"化学反应{reaction_type}的特征是（  ）", options, correct_answer, explanation

        elif knowledge_area == 'cell_structure':
            structures = ['细胞膜', '细胞核', '叶绿体', '线粒体']
            structure = structures[index % len(structures)]
            options, correct_answer, explanation = self._generate_biology_structure_options(structure, index)
            return f"细胞的{structure}功能是（  ）", options, correct_answer, explanation

        elif knowledge_area == 'ecology':
            roles = ['生产者', '消费者', '分解者']
            role = roles[index % len(roles)]
            options, correct_answer, explanation = self._generate_biology_ecology_options(role, index)
            return f"生态系统中，{role}的是（  ）", options, correct_answer, explanation

        # 默认情况
        return "默认题干", ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"], "A", "默认解析"
    
    def _generate_fill_blank_question(self, template: Dict, index: int) -> tuple:
        """生成填空题"""
        knowledge_area = template.get('knowledge_area', '')

        if knowledge_area == 'opposite_numbers':
            number = random.randint(-10, 10)
            while number == 0:
                number = random.randint(-10, 10)

            stem = f"{number}的相反数是______"
            answer = str(-number)
            explanation = f"相反数是与原数相加等于0的数，{number}+({answer})=0"

            return stem, answer, explanation

        elif knowledge_area == 'absolute_value':
            number = random.randint(-20, 20)
            stem = f"|{number}|=______"
            answer = str(abs(number))
            explanation = f"绝对值是去掉符号取正数，{number}的绝对值是{answer}"

            return stem, answer, explanation

        elif knowledge_area == 'force_units':
            stem = "力的单位是______"
            answer = "牛顿"
            explanation = "力的国际单位是牛顿，符号是N"

            return stem, answer, explanation

        elif knowledge_area == 'speed_formula':
            stem = "速度的计算公式是______"
            answer = "v = s/t"
            explanation = "速度等于路程除以时间"

            return stem, answer, explanation

        elif knowledge_area == 'balancing_equations':
            stem = "化学方程式的配平原则是______"
            answer = "质量守恒定律"
            explanation = "化学反应前后原子种类和数量不变"

            return stem, answer, explanation

        elif knowledge_area == 'solution_concentration':
            stem = "溶液的浓度单位有______"
            answer = "mol/L、g/L等"
            explanation = "常见浓度单位包括摩尔浓度、质量浓度等"

            return stem, answer, explanation

        elif knowledge_area == 'photosynthesis':
            stem = "光合作用的反应式是______"
            answer = "CO₂ + H₂O → C₆H₁₂O₆ + O₂"
            explanation = "植物通过光合作用将二氧化碳和水转化为葡萄糖和氧气"

            return stem, answer, explanation

        elif knowledge_area == 'dna_structure':
            stem = "DNA的全称是______"
            answer = "脱氧核糖核酸"
            explanation = "DNA是遗传物质的主要载体"

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
    
    # 选择题选项生成器
    def _generate_number_options(self, condition: str, index: int):
        """生成数分类选项"""
        numbers = ['-3', '√2', 'π', '0', '1/2', '-5.5', '√3', '3.14']
        target_num = numbers[index % len(numbers)]

        if target_num in ['-3', '0', '1/2', '-5.5']:
            correct = target_num
            wrong_nums = ['√2', 'π', '√3']
        else:
            correct = target_num
            wrong_nums = ['-3', '0', '1/2']

        options = [f"A. {wrong_nums[0]}", f"B. {correct}", f"C. {wrong_nums[1]}", f"D. {wrong_nums[2]}"]
        random.shuffle(options)

        # 找到正确答案的位置
        correct_answer = None
        for opt in options:
            if correct in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"{correct}是{condition.replace('是', '')}，因为{self._get_number_classification_explanation(correct)}"

    def _generate_calculation_options(self, expression: str, index: int):
        """生成计算题选项"""
        calculations = [
            ('(-3) + 5', '2'),
            ('8 - (-2)', '10'),
            ('3 × (-4)', '-12'),
            ('(-6) ÷ 2', '-3'),
            ('(-2)²', '4'),
            ('|-5|', '5')
        ]
        calc, answer = calculations[index % len(calculations)]

        wrong_answers = []
        if calc.startswith('(-3)'):
            wrong_answers = ['-2', '-8', '8']
        elif '×' in calc:
            wrong_answers = ['12', '-3', '4']
        elif '÷' in calc:
            wrong_answers = ['3', '-6', '2']
        else:
            wrong_answers = ['-4', '6', '-6']

        options = [f"A. {wrong_answers[0]}", f"B. {wrong_answers[1]}", f"C. {answer}", f"D. {wrong_answers[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if answer in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"{calc}的计算过程：{self._get_calculation_explanation(calc)} = {answer}"

    def _generate_operation_options(self, index: int):
        """生成运算规则选项"""
        operations = [
            ('有理数加法交换律', 'a + b = b + a'),
            ('有理数乘法交换律', 'a × b = b × a'),
            ('有理数乘法结合律', '(a × b) × c = a × (b × c)'),
            ('加法分配律', 'a × (b + c) = a × b + a × c')
        ]
        concept, rule = operations[index % len(operations)]

        wrong_rules = []
        if '交换律' in concept:
            wrong_rules = ['a + b = a - b', 'a × b = a ÷ b', 'a + b = b - a']
        elif '结合律' in concept:
            wrong_rules = ['(a + b) + c = a + (b - c)', 'a × (b × c) = (a × b) × c', '(a × b) × c = a × (b + c)']
        else:
            wrong_rules = ['a × (b + c) = a × b - a × c', 'a + (b × c) = (a + b) × (a + c)', 'a × (b - c) = a × b - a × c']

        options = [f"A. {wrong_rules[0]}", f"B. {wrong_rules[1]}", f"C. {rule}", f"D. {wrong_rules[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if rule in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"{concept}的正确表述是：{rule}，这是有理数运算的基本规律"

    def _generate_author_options(self, work: str, index: int):
        """生成作者选项"""
        authors = ['鲁迅', '老舍', '巴金', '茅盾', '沈从文', '朱自清', '冰心']
        correct_author = authors[index % len(authors)]

        wrong_authors = [a for a in authors if a != correct_author]
        random.shuffle(wrong_authors)

        options = [f"A. {wrong_authors[0]}", f"B. {wrong_authors[1]}", f"C. {correct_author}", f"D. {wrong_authors[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if correct_author in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"《{work}》的作者是{correct_author}，这是中国现代文学的经典作品"

    def _generate_character_options(self, index: int):
        """生成字词辨析选项"""
        correct_words = ['正确', '准确', '精确', '标准', '规范']
        wrong_words = ['错误', '错别字', '别字', '误写']

        correct_word = correct_words[index % len(correct_words)]
        wrong_sample = wrong_words[index % len(wrong_words)]

        # 构造有错别字的选项
        wrong_options = [
            correct_word.replace('确', '却'),
            correct_word.replace('准', '淮'),
            correct_word.replace('精', '菁'),
            wrong_sample
        ]

        options = [f"A. {wrong_options[0]}", f"B. {correct_word}", f"C. {wrong_options[1]}", f"D. {wrong_options[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if correct_word in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"'{correct_word}'是正确的写法，没有错别字"

    def _generate_verb_options(self, verb_phrase: str, index: int):
        """生成动词形式选项"""
        verb_forms = ['am', 'is', 'are', 'was', 'were', 'be', 'been']
        correct_form = verb_forms[index % len(verb_forms)]

        wrong_forms = [f for f in verb_forms if f != correct_form]
        random.shuffle(wrong_forms)

        options = [f"A. {wrong_forms[0]}", f"B. {wrong_forms[1]}", f"C. {correct_form}", f"D. {wrong_forms[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if correct_form in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"正确的使用{correct_form}，这是英语系动词的基本用法"

    def _generate_tense_options(self, subject: str, verb_phrase: str, index: int):
        """生成时态选项"""
        tenses = ['is going', 'goes', 'went', 'will go']
        correct_tense = tenses[index % len(tenses)]

        wrong_tenses = [t for t in tenses if t != correct_tense]
        random.shuffle(wrong_tenses)

        options = [f"A. {wrong_tenses[0]}", f"B. {wrong_tenses[1]}", f"C. {correct_tense}", f"D. {wrong_tenses[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if correct_tense in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"使用{correct_tense}表示正确的时态，这是英语语法的基本要求"

    # 新增的学科选项生成器
    def _generate_physics_concept_options(self, concept: str, index: int):
        """生成物理概念选项"""
        physics_concepts = {
            '力的概念': ('力是物体间的相互作用', ['能量', '质量', '时间']),
            '光的反射': ('光遇到两种介质的分界面时会改变传播方向', ['折射', '衍射', '干涉']),
            '机械运动': ('物体位置随时间的变化', ['化学变化', '生物过程', '地理现象']),
            '牛顿第一定律': ('物体保持静止或匀速直线运动状态', ['加速度', '力', '能量'])
        }

        if concept in physics_concepts:
            correct_def, wrong_items = physics_concepts[concept]
            options = [f"A. {wrong_items[0]}", f"B. {wrong_items[1]}", f"C. {correct_def}", f"D. {wrong_items[2]}"]
            random.shuffle(options)

            correct_answer = None
            for opt in options:
                if correct_def in opt:
                    correct_answer = opt[0]
                    break

            return options, correct_answer, f"{concept}的正确定义是：{correct_def}"

        return ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"], "C", "默认解释"

    def _generate_physics_calculation_options(self, value: str, situation: str, property_name: str, index: int):
        """生成物理计算选项"""
        calculations = [
            ('5kg', '在水平地面上静止', '重力', '50N'),
            ('10m/s', '自由下落', '速度', '10m/s'),
            ('100J', '加热过程', '内能', '100J'),
            ('20°C', '恒温过程', '温度', '20°C')
        ]

        mass, sit, prop, answer = calculations[index % len(calculations)]

        wrong_answers = []
        if 'kg' in mass:
            wrong_answers = ['25N', '100N', '5N']
        elif 'm/s' in mass:
            wrong_answers = ['5m/s', '15m/s', '20m/s']
        elif 'J' in mass:
            wrong_answers = ['50J', '200J', '0J']
        else:
            wrong_answers = ['10°C', '30°C', '0°C']

        options = [f"A. {wrong_answers[0]}", f"B. {wrong_answers[1]}", f"C. {answer}", f"D. {wrong_answers[2]}"]
        random.shuffle(options)

        correct_answer = None
        for opt in options:
            if answer in opt:
                correct_answer = opt[0]
                break

        return options, correct_answer, f"根据{property_name}计算，{mass}物体{sit}时{property_name}为{answer}"

    def _generate_chemistry_property_options(self, property_name: str, index: int):
        """生成化学性质选项"""
        chemistry_properties = {
            '金属': ('能与酸反应产生氢气', ['能与碱反应', '不导电', '易溶于水']),
            '酸': ('能与碱反应产生盐和水', ['能与金属反应', '呈碱性', '不导电']),
            '碱': ('能与酸反应产生盐和水', ['能与金属反应', '呈酸性', '易挥发']),
            '盐': ('由金属离子和酸根离子组成', ['由非金属组成', '呈酸性', '易分解'])
        }

        if property_name in chemistry_properties:
            correct_def, wrong_items = chemistry_properties[property_name]
            options = [f"A. {wrong_items[0]}", f"B. {wrong_items[1]}", f"C. {correct_def}", f"D. {wrong_items[2]}"]
            random.shuffle(options)

            correct_answer = None
            for opt in options:
                if correct_def in opt:
                    correct_answer = opt[0]
                    break

            return options, correct_answer, f"{property_name}的典型性质是：{correct_def}"

        return ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"], "C", "默认解释"

    def _generate_chemistry_reaction_options(self, reaction_type: str, index: int):
        """生成化学反应选项"""
        reactions = {
            '氧化反应': ('物质与氧气反应', ['物质与水反应', '物质自身反应', '物质与酸反应']),
            '还原反应': ('物质得到电子', ['物质失去电子', '物质与氧反应', '物质分解']),
            '化合反应': ('两种或多种物质生成一种物质', ['一种物质生成两种物质', '物质不变', '物质溶解'])
        }

        if reaction_type in reactions:
            correct_def, wrong_items = reactions[reaction_type]
            options = [f"A. {wrong_items[0]}", f"B. {wrong_items[1]}", f"C. {correct_def}", f"D. {wrong_items[2]}"]
            random.shuffle(options)

            correct_answer = None
            for opt in options:
                if correct_def in opt:
                    correct_answer = opt[0]
                    break

            return options, correct_answer, f"{reaction_type}的特征是：{correct_def}"

        return ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"], "C", "默认解释"

    def _generate_biology_structure_options(self, structure: str, index: int):
        """生成生物结构选项"""
        structures = {
            '细胞膜': ('控制物质进出细胞', ['产生能量', '遗传信息', '合成蛋白质']),
            '细胞核': ('储存遗传信息', ['光合作用', '呼吸作用', '物质运输']),
            '叶绿体': ('进行光合作用', ['细胞呼吸', '蛋白质合成', '物质运输']),
            '线粒体': ('进行细胞呼吸', ['光合作用', '遗传信息', '物质运输'])
        }

        if structure in structures:
            correct_func, wrong_items = structures[structure]
            options = [f"A. {wrong_items[0]}", f"B. {wrong_items[1]}", f"C. {correct_func}", f"D. {wrong_items[2]}"]
            random.shuffle(options)

            correct_answer = None
            for opt in options:
                if correct_func in opt:
                    correct_answer = opt[0]
                    break

            return options, correct_answer, f"{structure}的主要功能是：{correct_func}"

        return ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"], "C", "默认解释"

    def _generate_biology_ecology_options(self, role: str, index: int):
        """生成生态学选项"""
        roles = {
            '生产者': ('能制造有机物', ['消费有机物', '分解有机物', '运输物质']),
            '消费者': ('摄取有机物', ['制造有机物', '分解有机物', '产生能量']),
            '分解者': ('分解有机物', ['制造有机物', '摄取有机物', '运输物质'])
        }

        if role in roles:
            correct_def, wrong_items = roles[role]
            options = [f"A. {wrong_items[0]}", f"B. {wrong_items[1]}", f"C. {correct_def}", f"D. {wrong_items[2]}"]
            random.shuffle(options)

            correct_answer = None
            for opt in options:
                if correct_def in opt:
                    correct_answer = opt[0]
                    break

            return options, correct_answer, f"在生态系统中，{role}的定义是：{correct_def}"

        return ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"], "C", "默认解释"

    # 题目生成辅助方法
    def _get_number_classification_explanation(self, number: str) -> str:
        """获取数分类的详细解释"""
        explanations = {
            '-3': '有理数是有理数集中的数，可以写成分数形式',
            '√2': '无理数是无限不循环小数，不能写成分数形式',
            'π': '圆周率π是无理数',
            '0': '0是有理数，是整数的特殊形式',
            '1/2': '分数是有理数的一种形式',
            '-5.5': '负小数是有理数',
            '√3': '立方根也是无理数',
            '3.14': '有限小数是有理数'
        }
        return explanations.get(number, '根据数的性质进行分类')

    def _get_calculation_explanation(self, expression: str) -> str:
        """获取计算过程的详细解释"""
        explanations = {
            '(-3) + 5': '负数加法：-3 + 5 = 2',
            '8 - (-2)': '减去负数等于加上正数：8 + 2 = 10',
            '3 × (-4)': '正数乘以负数等于负数：3 × -4 = -12',
            '(-6) ÷ 2': '负数除以正数等于负数：-6 ÷ 2 = -3',
            '(-2)²': '负数的平方等于正数：(-2) × (-2) = 4',
            '|-5|': '绝对值运算：去掉符号取正数'
        }
        return explanations.get(expression, '按照运算规则计算')

    
    def generate_full_dataset(self, subjects: List[str] = None, kp_per_subject: int = 100, q_per_subject: int = 200):
        """生成完整数据集（增加数量）"""
        if subjects is None:
            subjects = ['math', 'chinese', 'english', 'physics', 'chemistry', 'biology']

        print("🚀 开始智能数据生成...")
        print(f"📋 目标: {len(subjects)}个学科，每科{kp_per_subject}个知识点，{q_per_subject}道题目")

        # 根据配置决定是否清空缓存
        if not self.use_cache:
            self.generated_knowledge_points.clear()
            print("🔄 已清空缓存，开始生成新数据...")
        else:
            print(f"📋 使用缓存模式，已有 {len(self.generated_knowledge_points)} 个知识点")

        # 预先生成所有内容，避免重复
        all_subjects_data = {}

        for subject in subjects:
            print(f"\n📚 正在生成{self._get_chinese_subject_name(subject)}数据...")

            # 为每个年级生成知识点（增加数量）
            all_kp = []
            for grade in ['Grade 7', 'Grade 8', 'Grade 9']:
                # 每个年级生成更多知识点
                grade_kp_count = max(kp_per_subject // 2, 30)  # 至少30个
                kp_data = self.generate_diverse_knowledge_points(
                    subject, grade, grade_kp_count
                )
                all_kp.extend(kp_data)
                print(f"    📖 {grade}: {len(kp_data)}个知识点")

            # 生成更多题目
            q_data = self.generate_diverse_questions(subject, q_per_subject)

            all_subjects_data[subject] = {
                'knowledge_points': all_kp,
                'questions': q_data
            }

            # 更新统计
            self.generation_stats['subjects_processed'] += 1
            self.generation_stats['knowledge_points_generated'] += len(all_kp)
            self.generation_stats['questions_generated'] += len(q_data)

            print(f"  ✅ 完成: {len(all_kp)}个知识点, {len(q_data)}道题目")

        # 统一保存到目录结构
        for subject, data in all_subjects_data.items():
            self.save_to_directory_structure(subject, data['knowledge_points'], data['questions'])

        # 保存缓存
        self._save_generated_cache()

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
    import sys

    print("🧠 启动智能数据生成器...")

    # 检查命令行参数
    use_cache = '--no-cache' not in sys.argv
    force_regenerate = '--force' in sys.argv

    if force_regenerate:
        print("🔄 强制重新生成模式：将清空缓存")
        use_cache = False

    try:
        generator = SmartDataGenerator(use_cache=use_cache)

        if not use_cache:
            print("⚠️ 缓存已禁用，将生成新数据")

        # 生成数据
        generator.generate_full_dataset(
            subjects=['math', 'chinese', 'english', 'physics', 'chemistry', 'biology'],  # 所有学科
            kp_per_subject=100,  # 每科100个知识点
            q_per_subject=200    # 每科200道题目
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
