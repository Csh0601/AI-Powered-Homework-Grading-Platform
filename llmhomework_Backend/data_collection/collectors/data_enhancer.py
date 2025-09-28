#!/usr/bin/env python3
"""
数据增强和质量提升模块
- 基于现有数据生成更高质量的变体
- 提升数据多样性和覆盖度
- 增强题目难度和复杂度
- 优化知识点描述和解析
"""

import pandas as pd
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Any, Set
from pathlib import Path
import re

class DataEnhancer:
    """数据增强器"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.processed_dir = os.path.join(self.base_dir, '..', 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)

        # 增强统计
        self.enhancement_stats = {
            'start_time': datetime.now().isoformat(),
            'knowledge_points_enhanced': 0,
            'questions_enhanced': 0,
            'variants_created': 0,
            'quality_improvements': 0
        }

    def enhance_knowledge_points(self, input_file: str = None) -> str:
        """增强知识点数据质量"""
        if input_file is None:
            # 查找最新的知识点文件
            input_file = self._find_latest_file('knowledge_points_*.csv')

        if not input_file:
            print("❌ 未找到知识点文件")
            return ""

        print(f"🔍 增强知识点数据: {input_file}")

        try:
            df = pd.read_csv(input_file)
            enhanced_kp = []

            for index, row in df.iterrows():
                # 原始知识点
                original_kp = self._create_knowledge_point_dict(row)

                # 生成增强版本
                enhanced_versions = self._generate_knowledge_point_variants(original_kp)

                enhanced_kp.extend(enhanced_versions)

                # 更新统计
                self.enhancement_stats['knowledge_points_enhanced'] += 1
                self.enhancement_stats['variants_created'] += len(enhanced_versions)

            # 保存增强后的知识点
            output_file = self._save_enhanced_knowledge_points(enhanced_kp)

            print(f"✅ 知识点增强完成: {len(enhanced_kp)}个增强版本")
            return output_file

        except Exception as e:
            print(f"❌ 知识点增强失败: {e}")
            return ""

    def enhance_questions(self, input_file: str = None) -> str:
        """增强题目数据质量"""
        if input_file is None:
            # 查找最新的题目文件
            input_file = self._find_latest_file('questions_*.csv')

        if not input_file:
            print("❌ 未找到题目文件")
            return ""

        print(f"🔍 增强题目数据: {input_file}")

        try:
            df = pd.read_csv(input_file)
            enhanced_questions = []

            for index, row in df.iterrows():
                # 原始题目
                original_question = self._create_question_dict(row)

                # 生成增强版本
                enhanced_versions = self._generate_question_variants(original_question)

                enhanced_questions.extend(enhanced_versions)

                # 更新统计
                self.enhancement_stats['questions_enhanced'] += 1
                self.enhancement_stats['variants_created'] += len(enhanced_versions)

            # 保存增强后的题目
            output_file = self._save_enhanced_questions(enhanced_questions)

            print(f"✅ 题目增强完成: {len(enhanced_questions)}个增强版本")
            return output_file

        except Exception as e:
            print(f"❌ 题目增强失败: {e}")
            return ""

    def _create_knowledge_point_dict(self, row: pd.Series) -> Dict[str, Any]:
        """从DataFrame行创建知识点字典"""
        return {
            'name': str(row.get('name', '')),
            'subject': str(row.get('subject', '')),
            'grade': str(row.get('grade', '')),
            'chapter': str(row.get('chapter', '')),
            'description': str(row.get('description', '')),
            'difficulty_level': int(row.get('difficulty_level', 1)),
            'importance_level': int(row.get('importance_level', 1)),
            'exam_frequency': float(row.get('exam_frequency', 0.0)),
            'keywords': str(row.get('keywords', '')),
            'learning_objectives': str(row.get('learning_objectives', '')),
            'common_mistakes': str(row.get('common_mistakes', '')),
            'learning_tips': str(row.get('learning_tips', ''))
        }

    def _create_question_dict(self, row: pd.Series) -> Dict[str, Any]:
        """从DataFrame行创建题目字典"""
        return {
            'question_id': str(row.get('question_id', '')),
            'subject': str(row.get('subject', '')),
            'grade': str(row.get('grade', '')),
            'question_type': str(row.get('question_type', '')),
            'stem': str(row.get('stem', '')),
            'options': str(row.get('options', '')),
            'correct_answer': str(row.get('correct_answer', '')),
            'explanation': str(row.get('explanation', '')),
            'difficulty_level': int(row.get('difficulty_level', 1)),
            'knowledge_points': str(row.get('knowledge_points', '')),
            'source': str(row.get('source', ''))
        }

    def _generate_knowledge_point_variants(self, kp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成知识点变体"""
        variants = [kp]  # 包含原始版本

        # 1. 增强描述
        enhanced_desc = self._enhance_knowledge_description(kp['description'], kp['subject'])
        if enhanced_desc != kp['description']:
            variant = kp.copy()
            variant['description'] = enhanced_desc
            variant['name'] = f"{kp['name']} (增强版)"
            variants.append(variant)

        # 2. 扩展关键词
        enhanced_keywords = self._enhance_keywords(kp['keywords'], kp['subject'])
        if enhanced_keywords != kp['keywords']:
            variant = kp.copy()
            variant['keywords'] = enhanced_keywords
            variants.append(variant)

        # 3. 优化学习目标
        enhanced_objectives = self._enhance_learning_objectives(kp['learning_objectives'], kp['difficulty_level'])
        if enhanced_objectives != kp['learning_objectives']:
            variant = kp.copy()
            variant['learning_objectives'] = enhanced_objectives
            variants.append(variant)

        return variants

    def _generate_question_variants(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成题目变体"""
        variants = [question]  # 包含原始版本

        # 1. 增强题目描述
        enhanced_stem = self._enhance_question_stem(question['stem'], question['subject'])
        if enhanced_stem != question['stem']:
            variant = question.copy()
            variant['stem'] = enhanced_stem
            variant['question_id'] = f"{question['question_id']}_enhanced"
            variants.append(variant)

        # 2. 增强解析
        enhanced_explanation = self._enhance_question_explanation(question['explanation'], question['subject'])
        if enhanced_explanation != question['explanation']:
            variant = question.copy()
            variant['explanation'] = enhanced_explanation
            variant['question_id'] = f"{question['question_id']}_detailed"
            variants.append(variant)

        # 3. 增加难度变体
        if question['question_type'] == 'choice' and question['difficulty_level'] < 4:
            harder_variant = self._create_harder_variant(question)
            if harder_variant:
                variants.append(harder_variant)

        return variants

    def _enhance_knowledge_description(self, description: str, subject: str) -> str:
        """增强知识点描述"""
        if not description or len(description) < 10:
            return description

        # 基于学科的描述增强模板
        enhancements = {
            '数学': [
                "在数学学习中，",
                "从基础概念到实际应用，",
                "通过理论学习和实践练习，"
            ],
            '语文': [
                "在语文学习过程中，",
                "通过阅读理解和语言运用，",
                "结合文学作品和语言规律，"
            ],
            '英语': [
                "在英语学习中，",
                "通过听说读写技能训练，",
                "结合语法知识和语言应用，"
            ],
            '物理': [
                "在物理学中，",
                "通过实验观察和理论分析，",
                "运用物理规律解决实际问题，"
            ],
            '化学': [
                "在化学学习中，",
                "通过实验操作和理论学习，",
                "理解物质变化和反应规律，"
            ],
            '生物': [
                "在生物学中，",
                "通过观察实验和理论学习，",
                "理解生命现象和生物规律，"
            ]
        }

        subject_enhancements = enhancements.get(subject, ["在学习过程中，"])
        enhancement = random.choice(subject_enhancements)

        if not description.startswith(tuple(subject_enhancements)):
            return f"{enhancement}{description}"

        return description

    def _enhance_keywords(self, keywords: str, subject: str) -> str:
        """增强关键词"""
        if not keywords:
            return keywords

        # 基于学科的关键词扩展
        keyword_expansions = {
            '数学': {
                '有理数': ['数与代数', '实数', '数值计算', '代数运算'],
                '几何': ['空间图形', '平面几何', '立体几何', '几何性质'],
                '函数': ['变量关系', '函数图像', '函数性质', '解析表达式']
            },
            '语文': {
                '阅读': ['理解能力', '分析能力', '鉴赏能力', '阅读技巧'],
                '写作': ['表达能力', '写作技巧', '文章结构', '语言运用'],
                '文学': ['文学常识', '文学作品', '文学鉴赏', '文学创作']
            },
            '英语': {
                '语法': ['语言结构', '句法规则', '语法运用', '语言规范'],
                '词汇': ['单词记忆', '词汇扩展', '词义辨析', '词汇运用'],
                '听说': ['听力技能', '口语表达', '语音语调', '交流能力']
            }
        }

        expanded_keywords = set(keywords.split('|'))

        # 添加相关扩展关键词
        for keyword in keywords.split('|'):
            expansions = keyword_expansions.get(subject, {}).get(keyword.strip(), [])
            expanded_keywords.update(expansions)

        return '|'.join(expanded_keywords)

    def _enhance_learning_objectives(self, objectives: str, difficulty: int) -> str:
        """增强学习目标"""
        if not objectives:
            return objectives

        # 基于难度等级的目标增强
        difficulty_templates = {
            1: "初步了解，基本认识",
            2: "理解概念，掌握基础",
            3: "熟练运用，灵活应用",
            4: "深入理解，综合运用",
            5: "创新应用，举一反三"
        }

        template = difficulty_templates.get(difficulty, "掌握知识，运用技能")

        if template not in objectives:
            return f"{template}：{objectives}"

        return objectives

    def _enhance_question_stem(self, stem: str, subject: str) -> str:
        """增强题目描述"""
        if not stem:
            return stem

        # 题目开头增强
        stem_enhancements = {
            '数学': ['计算', '求解', '判断', '比较', '分析'],
            '语文': ['理解', '分析', '鉴赏', '判断', '选择'],
            '英语': ['Choose', 'Complete', 'Translate', 'Match', 'Select'],
            '物理': ['计算', '分析', '判断', '求解', '比较'],
            '化学': ['判断', '计算', '分析', '比较', '选择'],
            '生物': ['判断', '分析', '比较', '理解', '选择']
        }

        enhancements = stem_enhancements.get(subject, ['请回答'])

        # 如果题目没有明确的开头，添加增强
        if not any(stem.startswith(enh) for enh in enhancements):
            enhancement = random.choice(enhancements)
            return f"{enhancement}：{stem}"

        return stem

    def _enhance_question_explanation(self, explanation: str, subject: str) -> str:
        """增强题目解析"""
        if not explanation:
            return explanation

        # 解析结尾增强
        explanation_endings = {
            '数学': ['根据数学原理得出结果', '通过计算验证答案', '运用数学方法求解'],
            '语文': ['根据文章内容分析判断', '结合语言知识理解', '运用语文技能解答'],
            '英语': ['根据语法规则判断', '结合语境理解', '运用英语知识解答'],
            '物理': ['运用物理规律分析', '通过物理原理求解', '根据物理知识判断'],
            '化学': ['运用化学原理分析', '根据化学规律判断', '通过化学知识解答'],
            '生物': ['根据生物学原理分析', '运用生物学知识判断', '通过生物学规律解答']
        }

        endings = explanation_endings.get(subject, ['根据相关知识分析'])

        if not any(explanation.endswith(ending) for ending in endings):
            ending = random.choice(endings)
            return f"{explanation}，{ending}。"

        return explanation

    def _create_harder_variant(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """创建更难的题目变体"""
        if question['question_type'] != 'choice' or question['difficulty_level'] >= 4:
            return None

        variant = question.copy()
        variant['question_id'] = f"{question['question_id']}_hard"
        variant['difficulty_level'] = min(5, question['difficulty_level'] + 1)

        # 增加题目复杂度
        if '计算' in question['stem']:
            # 增加计算步骤
            variant['stem'] = question['stem'].replace('计算', '先化简再计算')
        elif '判断' in question['stem']:
            # 增加判断条件
            variant['stem'] = question['stem'].replace('判断', '综合分析后判断')

        return variant

    def _find_latest_file(self, pattern: str) -> str:
        """查找最新的文件"""
        files = list(Path(self.processed_dir).glob(pattern))
        if not files:
            return ""

        # 按修改时间排序，返回最新的
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)

    def _save_enhanced_knowledge_points(self, enhanced_kp: List[Dict[str, Any]]) -> str:
        """保存增强后的知识点"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = os.path.join(
            self.processed_dir,
            f'enhanced_knowledge_points_{timestamp}.csv'
        )

        df = pd.DataFrame(enhanced_kp)
        df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"💾 增强知识点已保存: {output_file}")
        return output_file

    def _save_enhanced_questions(self, enhanced_questions: List[Dict[str, Any]]) -> str:
        """保存增强后的题目"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = os.path.join(
            self.processed_dir,
            f'enhanced_questions_{timestamp}.csv'
        )

        df = pd.DataFrame(enhanced_questions)
        df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"💾 增强题目已保存: {output_file}")
        return output_file

    def save_enhancement_report(self):
        """保存增强报告"""
        self.enhancement_stats['end_time'] = datetime.now().isoformat()

        report_file = os.path.join(
            self.processed_dir,
            f'data_enhancement_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.enhancement_stats, f, ensure_ascii=False, indent=2)

        print(f"📊 增强报告已保存: {report_file}")
        return report_file

    def run_full_enhancement(self):
        """运行完整的数据增强流程"""
        print("🚀 开始数据质量增强...")

        try:
            # 增强知识点
            kp_file = self.enhance_knowledge_points()

            # 增强题目
            q_file = self.enhance_questions()

            # 保存报告
            self.save_enhancement_report()

            print("✅ 数据增强完成！")
            print(f"📊 增强统计:")
            print(f"  - 知识点: {self.enhancement_stats['knowledge_points_enhanced']}")
            print(f"  - 题目: {self.enhancement_stats['questions_enhanced']}")
            print(f"  - 变体总数: {self.enhancement_stats['variants_created']}")
            print(f"  - 质量改进: {self.enhancement_stats['quality_improvements']}")

            return kp_file, q_file

        except Exception as e:
            print(f"❌ 数据增强失败: {e}")
            return "", ""

def main():
    """主函数"""
    print("🧠 启动数据增强器...")

    try:
        enhancer = DataEnhancer()
        kp_file, q_file = enhancer.run_full_enhancement()

        print("🔄 后续步骤:")
        print("1. 检查增强后的数据质量")
        print("2. 运行数据验证: python ../scripts/validate_data.py")
        print("3. 导入增强数据到数据库")
        print("4. 测试AI模型在新数据上的表现")

    except Exception as e:
        print(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

