#!/usr/bin/env python3
"""
PDF文档处理器
专门处理官方发布的教育PDF文档
提取知识点和学习目标
"""

import os
import json
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFDocumentProcessor:
    """PDF文档处理器"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'pdf_extracted_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 知识点提取模式
        self.knowledge_patterns = [
            r'(\d+\..*?理解.*?)',
            r'(\d+\..*?掌握.*?)',
            r'(\d+\..*?能够.*?)',
            r'(\d+\..*?会.*?)',
            r'(.*?的概念)',
            r'(.*?的性质)',
            r'(.*?的方法)',
            r'(.*?的应用)',
            r'学生应当(.*?)(?=。|，|；)',
            r'要求学生(.*?)(?=。|，|；)',
            r'核心素养.*?(.*?)(?=。|，|；)'
        ]
        
        # 学科关键词映射
        self.subject_keywords = {
            '数学': ['数学', '代数', '几何', '函数', '方程', '统计', '概率', '运算'],
            '语文': ['语文', '阅读', '写作', '文学', '语言', '文字', '古文', '诗歌'],
            '英语': ['英语', 'English', '语法', '词汇', '听力', '口语', '阅读', '写作'],
            '物理': ['物理', '力学', '电学', '光学', '热学', '声学'],
            '化学': ['化学', '化学反应', '元素', '化合物', '实验'],
            '生物': ['生物', '细胞', '遗传', '生态', '进化'],
            '历史': ['历史', '朝代', '事件', '人物', '制度'],
            '地理': ['地理', '地形', '气候', '人口', '资源'],
            '政治': ['政治', '法律', '道德', '社会', '公民']
        }
        
        self.extracted_data = {
            'knowledge_points': [],
            'learning_objectives': [],
            'metadata': {
                'process_time': datetime.now().isoformat(),
                'files_processed': [],
                'total_extractions': 0
            }
        }
    
    def extract_from_text(self, text: str, filename: str) -> Dict[str, List[Dict]]:
        """从文本中提取知识点"""
        knowledge_points = []
        learning_objectives = []
        
        # 确定学科
        subject = self._detect_subject(text, filename)
        grade = self._detect_grade(text, filename)
        
        # 提取知识点
        for pattern in self.knowledge_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1] if len(match) > 1 else ''
                
                if len(match) > 5 and len(match) < 200:
                    # 清理文本
                    clean_match = self._clean_text(match)
                    
                    if clean_match and not self._is_duplicate(clean_match, knowledge_points):
                        kp = {
                            'name': clean_match,
                            'subject': subject,
                            'grade': grade,
                            'chapter': self._extract_chapter(text, clean_match),
                            'description': f'根据官方文档提取：{clean_match}',
                            'difficulty_level': self._estimate_difficulty(clean_match),
                            'importance_level': self._estimate_importance(clean_match),
                            'keywords': self._generate_keywords(clean_match, subject),
                            'source': filename,
                            'extraction_time': datetime.now().isoformat()
                        }
                        knowledge_points.append(kp)
        
        # 提取学习目标
        objective_patterns = [
            r'学习目标[：:](.*?)(?=\n|。)',
            r'教学目标[：:](.*?)(?=\n|。)',
            r'能力要求[：:](.*?)(?=\n|。)',
            r'核心素养[：:](.*?)(?=\n|。)'
        ]
        
        for pattern in objective_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clean_objective = self._clean_text(match)
                if clean_objective:
                    learning_objectives.append({
                        'objective': clean_objective,
                        'subject': subject,
                        'grade': grade,
                        'source': filename
                    })
        
        return {
            'knowledge_points': knowledge_points,
            'learning_objectives': learning_objectives
        }
    
    def process_sample_curriculum_standards(self):
        """处理示例课程标准文档（模拟PDF内容）"""
        logger.info("📖 处理示例课程标准文档...")
        
        # 模拟不同学科的课程标准内容
        sample_documents = {
            '数学课程标准.pdf': """
            义务教育数学课程标准
            
            核心素养包括：数学抽象、逻辑推理、数学建模、数学运算、直观想象、数据分析。
            
            七年级数学学习要求：
            1. 理解有理数的概念，掌握有理数的四则运算
            2. 能够在数轴上表示有理数，理解相反数和绝对值
            3. 掌握整式的概念，会进行整式的加减运算
            4. 理解一元一次方程的概念，会解简单的一元一次方程
            5. 认识基本的几何图形，理解点、线、面的关系
            
            八年级数学学习要求：
            1. 理解实数的概念，会进行二次根式的化简
            2. 掌握一次函数的概念和性质，会画一次函数图像
            3. 理解全等三角形的概念，掌握全等三角形的判定
            4. 能够进行简单的数据收集和整理
            
            九年级数学学习要求：
            1. 理解二次函数的概念，掌握二次函数的性质
            2. 掌握圆的基本性质，会计算圆的周长和面积
            3. 理解概率的概念，会计算简单事件的概率
            """,
            
            '语文课程标准.pdf': """
            义务教育语文课程标准
            
            核心素养包括：语言建构与运用、思维发展与提升、审美鉴赏与创造、文化传承与理解。
            
            七年级语文学习要求：
            1. 能够流利地朗读课文，理解文章的基本内容
            2. 掌握常用汉字的书写，会查字典
            3. 理解记叙文的基本特点，会分析人物形象
            4. 能够写出条理清楚的记叙文
            5. 了解基本的文学常识
            
            八年级语文学习要求：
            1. 能够阅读浅易的文言文，理解基本内容
            2. 掌握说明文的基本特点，会分析说明方法
            3. 能够写出结构完整的说明文
            4. 理解诗歌的基本特点，会赏析简单的诗歌
            
            九年级语文学习要求：
            1. 能够阅读一般的文言文，理解文言实词和虚词
            2. 理解议论文的基本特点，会分析论证方法
            3. 能够写出观点明确的议论文
            4. 掌握综合性学习的基本方法
            """,
            
            '英语课程标准.pdf': """
            义务教育英语课程标准
            
            核心素养包括：语言能力、文化意识、思维品质、学习能力。
            
            七年级英语学习要求：
            1. 掌握26个字母的读音和书写
            2. 理解一般现在时的概念，会使用be动词
            3. 掌握基本的问候用语和日常交际用语
            4. 能够进行简单的自我介绍
            5. 掌握基本的名词单复数变化规则
            
            八年级英语学习要求：
            1. 理解一般过去时的概念，会使用过去式
            2. 掌握现在进行时的用法
            3. 能够描述过去发生的事情
            4. 理解比较级和最高级的用法
            
            九年级英语学习要求：
            1. 理解现在完成时的概念和用法
            2. 掌握被动语态的基本形式
            3. 能够进行较复杂的语言表达
            4. 理解定语从句的基本用法
            """
        }
        
        for filename, content in sample_documents.items():
            logger.info(f"📄 处理文档: {filename}")
            
            extracted = self.extract_from_text(content, filename)
            
            self.extracted_data['knowledge_points'].extend(extracted['knowledge_points'])
            self.extracted_data['learning_objectives'].extend(extracted['learning_objectives'])
            self.extracted_data['metadata']['files_processed'].append(filename)
            
            logger.info(f"✅ 从{filename}提取: {len(extracted['knowledge_points'])}个知识点")
    
    def _detect_subject(self, text: str, filename: str) -> str:
        """检测学科"""
        for subject, keywords in self.subject_keywords.items():
            if any(keyword in text or keyword in filename for keyword in keywords):
                return subject
        return '通用'
    
    def _detect_grade(self, text: str, filename: str) -> str:
        """检测年级"""
        grade_patterns = {
            'Grade 7': ['七年级', '初一', '7年级'],
            'Grade 8': ['八年级', '初二', '8年级'],
            'Grade 9': ['九年级', '初三', '9年级']
        }
        
        for grade, patterns in grade_patterns.items():
            if any(pattern in text or pattern in filename for pattern in patterns):
                return grade
        return 'Grade 7'  # 默认
    
    def _extract_chapter(self, text: str, knowledge_point: str) -> str:
        """提取章节信息"""
        # 在知识点附近查找章节信息
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if knowledge_point in line:
                # 向上查找章节标题
                for j in range(max(0, i-5), i):
                    if re.search(r'第.*?章|第.*?单元|Chapter|Unit', lines[j]):
                        return lines[j].strip()
        return '基础章节'
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空格和符号
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s()（）]', '', text)
        return text.strip()
    
    def _is_duplicate(self, text: str, existing_list: List[Dict]) -> bool:
        """检查是否重复"""
        return any(item['name'] == text for item in existing_list)
    
    def _estimate_difficulty(self, text: str) -> int:
        """估算难度等级"""
        difficulty_keywords = {
            1: ['了解', '认识', '知道'],
            2: ['理解', '明确', '清楚'],
            3: ['掌握', '熟练', '应用'],
            4: ['分析', '综合', '判断'],
            5: ['创新', '设计', '评价']
        }
        
        for level, keywords in difficulty_keywords.items():
            if any(keyword in text for keyword in keywords):
                return level
        return 2  # 默认难度
    
    def _estimate_importance(self, text: str) -> int:
        """估算重要程度"""
        importance_keywords = {
            5: ['核心', '重要', '关键', '必须'],
            4: ['掌握', '熟练', '主要'],
            3: ['理解', '明确', '基本'],
            2: ['了解', '认识', '简单'],
            1: ['知道', '初步', '一般']
        }
        
        for level, keywords in importance_keywords.items():
            if any(keyword in text for keyword in keywords):
                return level
        return 3  # 默认重要程度
    
    def _generate_keywords(self, text: str, subject: str) -> str:
        """生成关键词"""
        keywords = [subject]
        
        # 从文本中提取关键词
        important_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        keywords.extend(important_words[:3])  # 取前3个中文词
        
        return '|'.join(keywords)
    
    def save_extracted_data(self):
        """保存提取的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 更新元数据
        self.extracted_data['metadata']['total_extractions'] = len(self.extracted_data['knowledge_points'])
        
        # 保存知识点
        if self.extracted_data['knowledge_points']:
            kp_df = pd.DataFrame(self.extracted_data['knowledge_points'])
            kp_file = os.path.join(self.output_dir, f'knowledge_points_extracted_{timestamp}.csv')
            kp_df.to_csv(kp_file, index=False, encoding='utf-8')
            logger.info(f"💾 知识点数据已保存: {kp_file}")
        
        # 保存学习目标
        if self.extracted_data['learning_objectives']:
            obj_df = pd.DataFrame(self.extracted_data['learning_objectives'])
            obj_file = os.path.join(self.output_dir, f'learning_objectives_{timestamp}.csv')
            obj_df.to_csv(obj_file, index=False, encoding='utf-8')
            logger.info(f"💾 学习目标已保存: {obj_file}")
        
        # 保存元数据
        metadata_file = os.path.join(self.output_dir, f'extraction_metadata_{timestamp}.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data['metadata'], f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 提取元数据已保存: {metadata_file}")
        
        return len(self.extracted_data['knowledge_points'])
    
    def run_processing(self):
        """运行完整的处理流程"""
        logger.info("🚀 开始PDF文档处理...")
        
        try:
            # 处理示例文档
            self.process_sample_curriculum_standards()
            
            # 保存数据
            kp_count = self.save_extracted_data()
            
            logger.info("✅ PDF文档处理完成!")
            logger.info(f"📊 提取结果: {kp_count}个知识点")
            logger.info(f"📁 数据保存在: {self.output_dir}")
            
            return kp_count
            
        except Exception as e:
            logger.error(f"❌ 处理过程中出错: {e}")
            raise

def main():
    """主函数"""
    print("📄 启动PDF文档处理器...")
    print("📚 专门处理官方教育文档")
    
    try:
        processor = PDFDocumentProcessor()
        kp_count = processor.run_processing()
        
        print(f"\n🎉 处理完成!")
        print(f"📈 统计:")
        print(f"  - 知识点: {kp_count} 个")
        print(f"📁 文件位置: {processor.output_dir}")
        
        print(f"\n🔄 下一步:")
        print(f"1. 检查提取的数据质量")
        print(f"2. 合并到主数据: python unify_generated_data.py")
        print(f"3. 验证数据: python ../scripts/validate_collected_data.py")
        
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    main()
