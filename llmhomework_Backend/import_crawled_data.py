#!/usr/bin/env python3
"""
导入爬取的数据到数据库
直接使用SQLAlchemy模型进行导入
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
import time

# 添加路径
sys.path.append(os.path.dirname(__file__))

# 导入数据库模型和数据库连接
from app.models.knowledge_base import (
    Base, Grade, Subject, Chapter, KnowledgePoint, Question,
    QuestionOption, QuestionType
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_crawled_data():
    """导入爬取的数据"""
    logger.info("🔄 开始导入爬取的数据...")

    # 创建数据库连接
    db_path = os.path.join(os.path.dirname(__file__), "database", "knowledge_base.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 读取统一后的数据
        knowledge_file = os.path.join(os.path.dirname(__file__), "data_collection", "processed", "knowledge_points_unified.csv")
        questions_file = os.path.join(os.path.dirname(__file__), "data_collection", "processed", "questions_unified.csv")

        imported_kp_count = 0
        imported_q_count = 0

        # 导入知识点
        if os.path.exists(knowledge_file):
            logger.info(f"📚 导入知识点数据: {knowledge_file}")
            df_kp = pd.read_csv(knowledge_file)

            for _, row in df_kp.iterrows():
                try:
                    # 查找或创建年级
                    grade = session.query(Grade).filter_by(code=row.get('grade', 'Grade 7')).first()
                    if not grade:
                        grade = Grade(
                            name=row.get('grade', 'Grade 7'),
                            code=row.get('grade', 'Grade 7'),
                            description=f"年级 {row.get('grade', 'Grade 7')}"
                        )
                        session.add(grade)
                        session.flush()

                    # 查找或创建学科
                    subject = session.query(Subject).filter_by(
                        grade_id=grade.id,
                        code=row.get('subject', 'math').lower()
                    ).first()
                    if not subject:
                        subject = Subject(
                            grade_id=grade.id,
                            name=row.get('subject', '数学'),
                            code=row.get('subject', 'math').lower(),
                            difficulty_level=int(row.get('difficulty_level', 3))
                        )
                        session.add(subject)
                        session.flush()

                    # 查找或创建章节
                    chapter = session.query(Chapter).filter_by(
                        subject_id=subject.id,
                        name=row.get('chapter', '未分类')
                    ).first()
                    if not chapter:
                        chapter = Chapter(
                            subject_id=subject.id,
                            name=row.get('chapter', '未分类'),
                            code=f"ch_{subject.code}_{len(session.query(Chapter).filter_by(subject_id=subject.id).all()) + 1}",
                            difficulty_level=int(row.get('difficulty_level', 3))
                        )
                        session.add(chapter)
                        session.flush()

                    # 创建知识点
                    keywords = []
                    if pd.notna(row.get('keywords')):
                        keywords = str(row.get('keywords')).split('|')[:5]

                    knowledge_point = KnowledgePoint(
                        chapter_id=chapter.id,
                        name=str(row.get('name', '')),
                        code=f"kp_{chapter.code}_{len(session.query(KnowledgePoint).filter_by(chapter_id=chapter.id).all()) + 1}",
                        description=str(row.get('description', '')),
                        difficulty_level=int(row.get('difficulty_level', 3)),
                        importance_level=int(row.get('importance_level', 3)),
                        exam_frequency=float(row.get('exam_frequency', 0.5))
                    )
                    session.add(knowledge_point)
                    session.flush()

                    # 添加关键词
                    for keyword in keywords:
                        if keyword.strip():
                            from app.models.knowledge_base import KnowledgePointKeyword
                            kp_keyword = KnowledgePointKeyword(
                                knowledge_point_id=knowledge_point.id,
                                keyword=keyword.strip(),
                                weight=1.0
                            )
                            session.add(kp_keyword)

                    imported_kp_count += 1

                except Exception as e:
                    logger.warning(f"跳过知识点 {row.get('name', '未知')}: {e}")

            session.commit()
            logger.info(f"✅ 知识点导入完成: {imported_kp_count} 条")

        # 导入题目
        if os.path.exists(questions_file):
            logger.info(f"📝 导入题目数据: {questions_file}")
            df_q = pd.read_csv(questions_file)

            for _, row in df_q.iterrows():
                try:
                    # 查找学科
                    subject = session.query(Subject).filter_by(
                        code=str(row.get('subject', 'math')).lower()
                    ).first()
                    if not subject:
                        logger.warning(f"找不到学科 {row.get('subject')}")
                        continue

                    # 创建题目
                    question = Question(
                        question_id=str(row.get('question_id', f'q_{int(time.time())}_{imported_q_count}')),
                        subject_id=subject.id,
                        number=str(row.get('number', imported_q_count + 1)),
                        stem=str(row.get('stem', '')),
                        answer=str(row.get('answer', '')),
                        type=QuestionType(str(row.get('question_type', 'choice'))),
                        timestamp=int(time.time()),
                        correct_answer=str(row.get('correct_answer', '')),
                        explanation=str(row.get('explanation', '')),
                        difficulty_level=int(row.get('difficulty_level', 3)),
                        source=str(row.get('source', '导入数据'))
                    )
                    session.add(question)
                    session.flush()

                    # 处理选项
                    options_data = row.get('options', '')
                    if pd.notna(options_data) and options_data:
                        try:
                            import json
                            options_list = json.loads(options_data)
                            if isinstance(options_list, list):
                                for i, option in enumerate(options_list):
                                    if option:
                                        q_option = QuestionOption(
                                            question_id=question.question_id,
                                            option_key=chr(65 + i),  # A, B, C, D...
                                            option_value=str(option),
                                            is_correct=(str(row.get('correct_answer', '')) == chr(65 + i))
                                        )
                                        db_session.add(q_option)
                        except:
                            # 如果JSON解析失败，尝试其他格式
                            pass

                    imported_q_count += 1

                except Exception as e:
                    logger.warning(f"跳过题目 {row.get('question_id', '未知')}: {e}")

            session.commit()
            logger.info(f"✅ 题目导入完成: {imported_q_count} 条")

        # 统计信息
        logger.info("📊 数据库统计:")
        logger.info(f"  - 知识点已导入: {imported_kp_count} 条")
        logger.info(f"  - 题目已导入: {imported_q_count} 条")

        # 显示实际数据库中的数据
        kp_count = session.query(KnowledgePoint).count()
        q_count = session.query(Question).count()
        logger.info(f"📊 数据库实际数据:")
        logger.info(f"  - 知识点总数: {kp_count} 条")
        logger.info(f"  - 题目总数: {q_count} 条")

        logger.info("🎉 数据导入完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 数据导入失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🔄 开始导入爬取的数据到数据库...")
    success = import_crawled_data()
    
    if success:
        print("✅ 数据导入成功！")
        print("\n📋 后续操作建议:")
        print("1. 运行 python test_day7_complete.py 测试系统")
        print("2. 启动后端服务 python run.py")
        print("3. 测试知识匹配功能")
    else:
        print("❌ 数据导入失败")
