#!/usr/bin/env python3
"""
数据导入脚本
将收集和验证的数据导入到知识库数据库
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import uuid

# 添加项目根目录到路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from llmhomework_Backend.app.models.knowledge_base import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

class DataImporter:
    """数据导入器"""
    
    def __init__(self, database_url: str = None):
        """初始化数据导入器"""
        if database_url is None:
            # 默认使用MySQL数据库
            database_url = "mysql+pymysql://root:password@localhost:3306/llmhomework_knowledge_db"
        
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.data_dir = os.path.join(current_dir, '..', '..', 'data_collection', 'processed')
        
        self.import_stats = {
            'timestamp': datetime.now().isoformat(),
            'grades_imported': 0,
            'subjects_imported': 0,
            'chapters_imported': 0,
            'knowledge_points_imported': 0,
            'questions_imported': 0,
            'errors': []
        }
    
    def create_tables(self):
        """创建数据库表"""
        print("📦 创建数据库表...")
        try:
            Base.metadata.create_all(self.engine)
            print("✅ 数据库表创建成功")
        except Exception as e:
            error_msg = f"创建数据库表失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
            raise
    
    def setup_basic_data(self):
        """设置基础数据（年级、学科等）"""
        print("🏗️ 设置基础数据...")
        
        session = self.Session()
        try:
            # 创建年级数据
            grades_data = [
                {'name': '初一', 'code': 'grade7', 'description': '初中一年级', 'sort_order': 1},
                {'name': '初二', 'code': 'grade8', 'description': '初中二年级', 'sort_order': 2},
                {'name': '初三', 'code': 'grade9', 'description': '初中三年级', 'sort_order': 3}
            ]
            
            for grade_data in grades_data:
                existing_grade = session.query(Grade).filter_by(code=grade_data['code']).first()
                if not existing_grade:
                    grade = Grade(**grade_data)
                    session.add(grade)
                    self.import_stats['grades_imported'] += 1
            
            session.commit()
            
            # 创建学科数据
            subjects_data = [
                # 初一学科
                {'grade_code': 'grade7', 'name': '数学', 'code': 'math_7', 'difficulty_level': 3},
                {'grade_code': 'grade7', 'name': '语文', 'code': 'chinese_7', 'difficulty_level': 2},
                {'grade_code': 'grade7', 'name': '英语', 'code': 'english_7', 'difficulty_level': 2},
                {'grade_code': 'grade7', 'name': '生物', 'code': 'biology_7', 'difficulty_level': 2},
                {'grade_code': 'grade7', 'name': '历史', 'code': 'history_7', 'difficulty_level': 2},
                {'grade_code': 'grade7', 'name': '地理', 'code': 'geography_7', 'difficulty_level': 2},
                {'grade_code': 'grade7', 'name': '政治', 'code': 'politics_7', 'difficulty_level': 2},
                # 初二学科
                {'grade_code': 'grade8', 'name': '数学', 'code': 'math_8', 'difficulty_level': 4},
                {'grade_code': 'grade8', 'name': '语文', 'code': 'chinese_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '英语', 'code': 'english_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '物理', 'code': 'physics_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '生物', 'code': 'biology_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '历史', 'code': 'history_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '地理', 'code': 'geography_8', 'difficulty_level': 3},
                {'grade_code': 'grade8', 'name': '政治', 'code': 'politics_8', 'difficulty_level': 3},
                # 初三学科
                {'grade_code': 'grade9', 'name': '数学', 'code': 'math_9', 'difficulty_level': 5},
                {'grade_code': 'grade9', 'name': '语文', 'code': 'chinese_9', 'difficulty_level': 4},
                {'grade_code': 'grade9', 'name': '英语', 'code': 'english_9', 'difficulty_level': 4},
                {'grade_code': 'grade9', 'name': '物理', 'code': 'physics_9', 'difficulty_level': 4},
                {'grade_code': 'grade9', 'name': '化学', 'code': 'chemistry_9', 'difficulty_level': 4},
                {'grade_code': 'grade9', 'name': '历史', 'code': 'history_9', 'difficulty_level': 4},
                {'grade_code': 'grade9', 'name': '政治', 'code': 'politics_9', 'difficulty_level': 4}
            ]
            
            for subject_data in subjects_data:
                grade = session.query(Grade).filter_by(code=subject_data['grade_code']).first()
                if grade:
                    existing_subject = session.query(Subject).filter_by(code=subject_data['code']).first()
                    if not existing_subject:
                        subject = Subject(
                            grade_id=grade.id,
                            name=subject_data['name'],
                            code=subject_data['code'],
                            difficulty_level=subject_data['difficulty_level']
                        )
                        session.add(subject)
                        self.import_stats['subjects_imported'] += 1
            
            session.commit()
            print(f"✅ 基础数据设置完成")
            
        except Exception as e:
            session.rollback()
            error_msg = f"设置基础数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
        finally:
            session.close()
    
    def import_knowledge_points(self):
        """导入知识点数据"""
        print("📚 导入知识点数据...")
        
        csv_path = os.path.join(self.data_dir, 'knowledge_points.csv')
        if not os.path.exists(csv_path):
            print("❌ 知识点数据文件不存在")
            return
        
        session = self.Session()
        try:
            df = pd.read_csv(csv_path)
            
            for index, row in df.iterrows():
                try:
                    # 查找或创建学科
                    subject = session.query(Subject).filter(
                        Subject.name == row['subject']
                    ).first()
                    
                    if not subject:
                        print(f"⚠️ 未找到学科: {row['subject']}")
                        continue
                    
                    # 查找或创建章节
                    chapter = session.query(Chapter).filter(
                        Chapter.subject_id == subject.id,
                        Chapter.name == row['chapter']
                    ).first()
                    
                    if not chapter:
                        chapter = Chapter(
                            subject_id=subject.id,
                            name=row['chapter'],
                            code=f"{subject.code}_ch{row.get('chapter_number', index+1)}",
                            chapter_number=row.get('chapter_number', index+1),
                            difficulty_level=row.get('difficulty_level', 1)
                        )
                        session.add(chapter)
                        session.flush()  # 获取chapter.id
                        self.import_stats['chapters_imported'] += 1
                    
                    # 检查知识点是否已存在
                    existing_kp = session.query(KnowledgePoint).filter(
                        KnowledgePoint.chapter_id == chapter.id,
                        KnowledgePoint.name == row['name']
                    ).first()
                    
                    if existing_kp:
                        print(f"⚠️ 知识点已存在: {row['name']}")
                        continue
                    
                    # 创建知识点
                    knowledge_point = KnowledgePoint(
                        chapter_id=chapter.id,
                        name=row['name'],
                        code=f"{chapter.code}_kp{len(chapter.knowledge_points)+1}",
                        description=row.get('description', ''),
                        difficulty_level=int(row.get('difficulty_level', 1)),
                        importance_level=int(row.get('importance_level', 1)),
                        exam_frequency=float(row.get('exam_frequency', 0.0)),
                        learning_objectives=row.get('learning_objectives', ''),
                        common_mistakes=row.get('common_mistakes', ''),
                        learning_tips=row.get('learning_tips', '')
                    )
                    
                    session.add(knowledge_point)
                    session.flush()  # 获取knowledge_point.id
                    
                    # 添加关键词
                    if not pd.isna(row.get('keywords')):
                        keywords = str(row['keywords']).split('|')
                        for keyword in keywords:
                            keyword = keyword.strip()
                            if keyword:
                                keyword_obj = KnowledgePointKeyword(
                                    knowledge_point_id=knowledge_point.id,
                                    keyword=keyword,
                                    weight=1.0
                                )
                                session.add(keyword_obj)
                    
                    self.import_stats['knowledge_points_imported'] += 1
                    
                except Exception as e:
                    print(f"❌ 导入知识点 {row.get('name', 'unknown')} 失败: {str(e)}")
                    self.import_stats['errors'].append(f"知识点导入错误: {str(e)}")
                    continue
            
            session.commit()
            print(f"✅ 知识点导入完成，共导入 {self.import_stats['knowledge_points_imported']} 个知识点")
            
        except Exception as e:
            session.rollback()
            error_msg = f"导入知识点数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
        finally:
            session.close()
    
    def import_questions(self, filename: str, question_type: str):
        """导入题目数据"""
        print(f"📝 导入{question_type}数据...")
        
        csv_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(csv_path):
            print(f"❌ {question_type}数据文件不存在")
            return
        
        session = self.Session()
        try:
            df = pd.read_csv(csv_path)
            questions_imported = 0
            
            for index, row in df.iterrows():
                try:
                    # 查找学科
                    subject = session.query(Subject).filter(
                        Subject.name == row['subject']
                    ).first()
                    
                    if not subject:
                        print(f"⚠️ 未找到学科: {row['subject']}")
                        continue
                    
                    # 检查题目是否已存在
                    existing_question = session.query(Question).filter_by(
                        question_id=row['question_id']
                    ).first()
                    
                    if existing_question:
                        print(f"⚠️ 题目已存在: {row['question_id']}")
                        continue
                    
                    # 创建题目
                    question = Question(
                        question_id=row['question_id'],
                        subject_id=subject.id,
                        number=row.get('number', str(index+1)),
                        stem=row['stem'],
                        answer=row.get('answer', ''),
                        type=QuestionType(row['type']),
                        timestamp=int(datetime.now().timestamp()),
                        correct_answer=row.get('correct_answer', ''),
                        explanation=row.get('explanation', ''),
                        difficulty_level=int(row.get('difficulty_level', 1)),
                        source=row.get('source', ''),
                        source_type='exam' if '中考' in question_type else 'mock'
                    )
                    
                    session.add(question)
                    session.flush()  # 获取question对象
                    
                    # 如果是选择题，添加选项
                    if row['type'] == 'choice' and not pd.isna(row.get('options')):
                        try:
                            # 处理选项数据
                            options_str = str(row['options'])
                            if options_str.startswith('[') and options_str.endswith(']'):
                                options = eval(options_str)
                            else:
                                # 假设是逗号分隔的格式
                                options = options_str.split(',')
                            
                            for i, option_text in enumerate(options):
                                option_text = option_text.strip().strip("'\"")
                                if option_text:
                                    option_key = chr(65 + i)  # A, B, C, D
                                    is_correct = (option_key == row.get('correct_answer', ''))
                                    
                                    option = QuestionOption(
                                        question_id=question.question_id,
                                        option_key=option_key,
                                        option_value=option_text,
                                        is_correct=is_correct
                                    )
                                    session.add(option)
                        except Exception as e:
                            print(f"⚠️ 处理题目选项失败: {str(e)}")
                    
                    questions_imported += 1
                    
                except Exception as e:
                    print(f"❌ 导入题目 {row.get('question_id', 'unknown')} 失败: {str(e)}")
                    self.import_stats['errors'].append(f"题目导入错误: {str(e)}")
                    continue
            
            session.commit()
            self.import_stats['questions_imported'] += questions_imported
            print(f"✅ {question_type}导入完成，共导入 {questions_imported} 道题目")
            
        except Exception as e:
            session.rollback()
            error_msg = f"导入{question_type}数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
        finally:
            session.close()
    
    def create_tags_and_associations(self):
        """创建标签并建立关联"""
        print("🏷️ 创建标签和关联...")
        
        session = self.Session()
        try:
            # 创建基础标签
            basic_tags = [
                {'name': '选择题', 'category': 'question_type'},
                {'name': '填空题', 'category': 'question_type'},
                {'name': '判断题', 'category': 'question_type'},
                {'name': '应用题', 'category': 'question_type'},
                {'name': '基础', 'category': 'difficulty'},
                {'name': '中等', 'category': 'difficulty'},
                {'name': '困难', 'category': 'difficulty'},
                {'name': '中考真题', 'category': 'source'},
                {'name': '模拟题', 'category': 'source'}
            ]
            
            for tag_data in basic_tags:
                existing_tag = session.query(Tag).filter_by(name=tag_data['name']).first()
                if not existing_tag:
                    tag = Tag(**tag_data)
                    session.add(tag)
            
            session.commit()
            print("✅ 标签创建完成")
            
        except Exception as e:
            session.rollback()
            error_msg = f"创建标签失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
        finally:
            session.close()
    
    def generate_import_report(self):
        """生成导入报告"""
        print("📊 生成导入报告...")
        
        report = {
            'import_summary': {
                'import_timestamp': self.import_stats['timestamp'],
                'grades_imported': self.import_stats['grades_imported'],
                'subjects_imported': self.import_stats['subjects_imported'],
                'chapters_imported': self.import_stats['chapters_imported'],
                'knowledge_points_imported': self.import_stats['knowledge_points_imported'],
                'questions_imported': self.import_stats['questions_imported'],
                'total_errors': len(self.import_stats['errors']),
                'import_status': 'completed_with_errors' if self.import_stats['errors'] else 'completed'
            },
            'detailed_stats': self.import_stats,
            'database_status': self.check_database_status(),
            'next_steps': [
                '验证导入数据的完整性',
                '建立知识点之间的关联关系',
                '创建题目与知识点的关联',
                '测试数据查询功能'
            ]
        }
        
        # 保存报告
        report_path = os.path.join(self.data_dir, 'import_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 导入报告已保存: {report_path}")
        return report
    
    def check_database_status(self) -> Dict[str, Any]:
        """检查数据库状态"""
        session = self.Session()
        try:
            status = {
                'grades_count': session.query(Grade).count(),
                'subjects_count': session.query(Subject).count(),
                'chapters_count': session.query(Chapter).count(),
                'knowledge_points_count': session.query(KnowledgePoint).count(),
                'questions_count': session.query(Question).count(),
                'tags_count': session.query(Tag).count()
            }
            return status
        except Exception as e:
            return {'error': str(e)}
        finally:
            session.close()
    
    def run_import(self):
        """执行完整的数据导入流程"""
        print("🚀 开始数据导入流程...")
        print("=" * 60)
        
        try:
            # 1. 创建数据库表
            self.create_tables()
            
            # 2. 设置基础数据
            self.setup_basic_data()
            
            # 3. 导入知识点数据
            self.import_knowledge_points()
            
            # 4. 导入题目数据
            self.import_questions('exam_questions.csv', '中考原题')
            self.import_questions('mock_questions.csv', '模拟题')
            
            # 5. 创建标签和关联
            self.create_tags_and_associations()
            
            # 6. 生成导入报告
            report = self.generate_import_report()
            
            print("\n" + "=" * 60)
            print("🎉 数据导入完成！")
            print(f"📊 导入统计:")
            print(f"  - 年级: {report['import_summary']['grades_imported']}")
            print(f"  - 学科: {report['import_summary']['subjects_imported']}")
            print(f"  - 章节: {report['import_summary']['chapters_imported']}")
            print(f"  - 知识点: {report['import_summary']['knowledge_points_imported']}")
            print(f"  - 题目: {report['import_summary']['questions_imported']}")
            print(f"❗ 错误数量: {report['import_summary']['total_errors']}")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            error_msg = f"数据导入过程中发生严重错误: {str(e)}"
            print(f"❌ {error_msg}")
            self.import_stats['errors'].append(error_msg)
            raise

def main():
    """主函数"""
    # 可以通过环境变量或参数传入数据库连接字符串
    database_url = os.getenv('DATABASE_URL')
    
    try:
        importer = DataImporter(database_url)
        report = importer.run_import()
        
        print("\n📋 导入总结:")
        print("✅ 成功完成:")
        print("  - 数据库表创建")
        print("  - 基础数据设置")
        print("  - 知识点数据导入")
        print("  - 题目数据导入")
        print("  - 标签系统创建")
        
        if report['import_summary']['total_errors'] > 0:
            print(f"\n⚠️ 发现 {report['import_summary']['total_errors']} 个错误，请查看导入报告")
        else:
            print("\n🎉 所有数据导入成功，无错误！")
        
        print("\n🔄 下一步建议:")
        print("  - 验证数据库中的数据完整性")
        print("  - 测试知识点查询功能")
        print("  - 建立题目与知识点的关联")
        print("  - 开始数据服务API开发")
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

