#!/usr/bin/env python3
"""
AI作业批改系统 - 题库初始化脚本
Day 9: 构建大规模题目数据库的初始化工具

主要功能：
1. 创建题库相关的数据库表
2. 导入爬取的题目数据
3. 生成初始化报告
4. 数据质量检查和验证
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import Config
from app.models.knowledge_base import Base
from app.models.question_bank import StandardQuestion, QuestionOption, QuestionBank
from app.services.question_bank_service import QuestionBankService, initialize_question_bank_from_crawled_data
from app.database import get_session

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('question_bank_init.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class QuestionBankInitializer:
    """题库初始化器"""
    
    def __init__(self):
        self.engine = None
        self.session = None
        self.init_report = {
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'success': False,
            'steps_completed': [],
            'errors': [],
            'statistics': {}
        }
    
    def initialize(self):
        """执行完整的初始化流程"""
        try:
            logger.info("开始题库初始化...")
            
            # 1. 连接数据库
            self._connect_database()
            self._add_step("数据库连接成功")
            
            # 2. 创建数据库表
            self._create_tables()
            self._add_step("数据库表创建完成")
            
            # 3. 检查基础数据
            self._check_base_data()
            self._add_step("基础数据检查完成")
            
            # 4. 导入爬取的题目数据
            import_result = self._import_crawled_data()
            self._add_step(f"题目数据导入完成: {import_result}")
            
            # 5. 数据质量检查
            quality_result = self._check_data_quality()
            self._add_step(f"数据质量检查完成: {quality_result}")
            
            # 6. 生成统计报告
            stats = self._generate_statistics()
            self.init_report['statistics'] = stats
            self._add_step("统计报告生成完成")
            
            # 7. 完成初始化
            self.init_report['success'] = True
            self.init_report['end_time'] = datetime.utcnow().isoformat()
            
            logger.info("题库初始化完成!")
            self._save_report()
            
            return self.init_report
            
        except Exception as e:
            error_msg = f"初始化失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.init_report['errors'].append(error_msg)
            self.init_report['end_time'] = datetime.utcnow().isoformat()
            self._save_report()
            raise
        
        finally:
            if self.session:
                self.session.close()
    
    def _connect_database(self):
        """连接数据库"""
        try:
            # 使用SQLite进行测试
            database_url = Config.SQLITE_DATABASE_URL or "sqlite:///knowledge_base.db"
            self.engine = create_engine(database_url, echo=False)
            SessionLocal = sessionmaker(bind=self.engine)
            self.session = SessionLocal()
            
            # 测试连接
            self.session.execute(text("SELECT 1"))
            logger.info(f"数据库连接成功: {database_url}")
            
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    def _create_tables(self):
        """创建数据库表"""
        try:
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建完成")
            
            # 验证表是否存在
            tables = ['standard_questions', 'question_options_extended', 'question_banks']
            for table in tables:
                result = self.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if not result.fetchone():
                    logger.warning(f"表 {table} 可能未正确创建")
            
        except Exception as e:
            raise Exception(f"创建数据库表失败: {str(e)}")
    
    def _check_base_data(self):
        """检查基础数据"""
        try:
            from app.models.knowledge_base import Grade, Subject
            
            # 检查年级数据
            grade_count = self.session.query(Grade).count()
            if grade_count == 0:
                logger.warning("未找到年级数据，尝试插入基础数据...")
                self._insert_base_data()
            
            # 检查学科数据
            subject_count = self.session.query(Subject).count()
            logger.info(f"发现 {grade_count} 个年级，{subject_count} 个学科")
            
        except Exception as e:
            logger.warning(f"检查基础数据时出现错误: {str(e)}，继续执行...")
    
    def _insert_base_data(self):
        """插入基础数据"""
        try:
            from app.models.knowledge_base import Grade, Subject
            
            # 插入年级数据
            grades_data = [
                {'name': 'Grade 7', 'code': 'grade7', 'description': '初一', 'sort_order': 1},
                {'name': 'Grade 8', 'code': 'grade8', 'description': '初二', 'sort_order': 2},
                {'name': 'Grade 9', 'code': 'grade9', 'description': '初三', 'sort_order': 3}
            ]
            
            for grade_data in grades_data:
                existing = self.session.query(Grade).filter(Grade.code == grade_data['code']).first()
                if not existing:
                    grade = Grade(**grade_data)
                    self.session.add(grade)
            
            self.session.commit()
            
            # 插入学科数据
            subjects_data = [
                {'grade_id': 1, 'name': 'Mathematics', 'code': 'math', 'description': '数学', 'difficulty_level': 3},
                {'grade_id': 1, 'name': 'Chinese', 'code': 'chinese', 'description': '语文', 'difficulty_level': 2},
                {'grade_id': 1, 'name': 'English', 'code': 'english', 'description': '英语', 'difficulty_level': 2}
            ]
            
            for subject_data in subjects_data:
                existing = self.session.query(Subject).filter(Subject.code == subject_data['code']).first()
                if not existing:
                    subject = Subject(**subject_data)
                    self.session.add(subject)
            
            self.session.commit()
            logger.info("基础数据插入完成")
            
        except Exception as e:
            self.session.rollback()
            logger.warning(f"插入基础数据失败: {str(e)}")
    
    def _import_crawled_data(self) -> Dict[str, Any]:
        """导入爬取的题目数据"""
        try:
            service = QuestionBankService(self.session)
            
            # 获取爬取数据目录
            data_directory = os.path.join(
                os.path.dirname(__file__),
                '../../data_collection/collectors/crawled_data'
            )
            
            if not os.path.exists(data_directory):
                logger.warning(f"爬取数据目录不存在: {data_directory}")
                return {'total_imported': 0, 'message': '数据目录不存在'}
            
            # 执行导入
            results = service.import_crawled_data(data_directory)
            
            logger.info(f"数据导入结果: {results}")
            return results
            
        except Exception as e:
            error_msg = f"导入爬取数据失败: {str(e)}"
            logger.error(error_msg)
            return {'total_imported': 0, 'error': error_msg}
    
    def _check_data_quality(self) -> Dict[str, Any]:
        """检查数据质量"""
        try:
            # 统计题目数量
            total_questions = self.session.query(StandardQuestion).count()
            
            # 检查必要字段完整性
            incomplete_questions = self.session.query(StandardQuestion).filter(
                (StandardQuestion.stem == None) | 
                (StandardQuestion.stem == '') |
                (StandardQuestion.correct_answer == None) |
                (StandardQuestion.correct_answer == '')
            ).count()
            
            # 检查重复题目
            service = QuestionBankService(self.session)
            duplicates = service.duplicate_detection(threshold=0.9)
            
            quality_result = {
                'total_questions': total_questions,
                'incomplete_questions': incomplete_questions,
                'duplicate_groups': len(duplicates),
                'data_completeness': (total_questions - incomplete_questions) / total_questions if total_questions > 0 else 0
            }
            
            logger.info(f"数据质量检查结果: {quality_result}")
            return quality_result
            
        except Exception as e:
            error_msg = f"数据质量检查失败: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """生成统计信息"""
        try:
            service = QuestionBankService(self.session)
            stats = service.get_question_bank_statistics()
            
            # 添加额外统计信息
            from app.models.knowledge_base import Subject
            subject_stats = {}
            subjects = self.session.query(Subject).all()
            
            for subject in subjects:
                question_count = self.session.query(StandardQuestion).filter(
                    StandardQuestion.subject_id == subject.id
                ).count()
                subject_stats[subject.name] = question_count
            
            stats['subject_distribution'] = subject_stats
            
            logger.info(f"统计信息: {stats}")
            return stats
            
        except Exception as e:
            error_msg = f"生成统计信息失败: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def _add_step(self, step_description: str):
        """添加完成步骤"""
        self.init_report['steps_completed'].append({
            'step': step_description,
            'timestamp': datetime.utcnow().isoformat()
        })
        logger.info(f"✅ {step_description}")
    
    def _save_report(self):
        """保存初始化报告"""
        try:
            report_file = os.path.join(
                os.path.dirname(__file__),
                f"question_bank_init_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.init_report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"初始化报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")


def main():
    """主函数"""
    try:
        print("=" * 60)
        print("AI作业批改系统 - 题库初始化")
        print("=" * 60)
        
        initializer = QuestionBankInitializer()
        report = initializer.initialize()
        
        print("\n" + "=" * 60)
        print("初始化完成!")
        print("=" * 60)
        print(f"开始时间: {report['start_time']}")
        print(f"结束时间: {report['end_time']}")
        print(f"成功状态: {report['success']}")
        print(f"完成步骤: {len(report['steps_completed'])}")
        
        if report.get('statistics'):
            stats = report['statistics']
            print(f"\n题库统计:")
            print(f"  总题目数: {stats.get('total_questions', 0)}")
            print(f"  平均质量分: {stats.get('average_quality_score', 0)}")
            
            if stats.get('subject_distribution'):
                print("  学科分布:")
                for subject, count in stats['subject_distribution'].items():
                    print(f"    {subject}: {count} 题")
        
        if report.get('errors'):
            print(f"\n错误信息:")
            for error in report['errors']:
                print(f"  - {error}")
        
        return 0 if report['success'] else 1
        
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
