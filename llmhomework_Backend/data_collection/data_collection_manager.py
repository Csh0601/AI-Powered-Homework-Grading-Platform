#!/usr/bin/env python3
"""
统一数据收集管理器
整合所有数据收集、处理、增强、导入功能
提供一站式数据管理解决方案
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 设置路径
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectionManager:
    """数据收集管理平台"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.collectors_dir = os.path.join(self.base_dir, 'collectors')
        self.scripts_dir = os.path.join(self.base_dir, 'scripts')
        self.processed_dir = os.path.join(self.base_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)

        self.collection_stats = {
            'timestamp': datetime.now().isoformat(),
            'total_knowledge_points': 0,
            'total_questions': 0,
            'total_subjects': 0,
            'data_quality_score': 0.0,
            'processing_steps': []
        }

        # 可用收集器列表
        self.available_collectors = {
            'smart_generator': {
                'name': '智能数据生成器',
                'description': '基于AI生成高质量的教育数据',
                'module': 'collectors.smart_data_generator',
                'function': 'generate_full_dataset'
            },
            'data_enhancer': {
                'name': '数据增强器',
                'description': '提升现有数据的质量和多样性',
                'module': 'collectors.data_enhancer',
                'function': 'run_full_enhancement'
            },
            'education_crawler': {
                'name': '教育网站爬虫',
                'description': '从合法教育网站收集数据',
                'module': 'collectors.legal_education_crawler',
                'function': 'run_full_crawl'
            }
        }

        # 数据处理流程
        self.processing_pipeline = [
            {'name': '数据收集', 'function': self.run_data_collection, 'required': True},
            {'name': '数据统一', 'function': self.run_data_unification, 'required': True},
            {'name': '数据增强', 'function': self.run_data_enhancement, 'required': True},
            {'name': '数据验证', 'function': self.run_data_validation, 'required': True},
            {'name': '质量报告', 'function': self.generate_quality_report, 'required': False}
        ]

    def run_data_collection(self) -> bool:
        """运行数据收集"""
        logger.info("📊 开始数据收集...")

        try:
            # 1. 运行智能数据生成器
            logger.info("🤖 运行智能数据生成器...")
            from collectors.smart_data_generator import SmartDataGenerator

            generator = SmartDataGenerator()
            generator.generate_full_dataset(
                subjects=['math', 'chinese', 'english', 'physics', 'chemistry', 'biology'],
                kp_per_subject=50,
                q_per_subject=80
            )

            step_result = {
                'step': '数据收集',
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'details': '智能数据生成完成'
            }

            self.collection_stats['processing_steps'].append(step_result)
            return True

        except Exception as e:
            logger.error(f"❌ 数据收集失败: {e}")
            step_result = {
                'step': '数据收集',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def run_data_unification(self) -> bool:
        """运行数据统一处理"""
        logger.info("🔄 开始数据统一处理...")

        try:
            # 调用统一处理脚本
            from scripts.unify_data import unify_all_data
            result = unify_all_data()

            step_result = {
                'step': '数据统一',
                'status': 'success' if result else 'failed',
                'timestamp': datetime.now().isoformat(),
                'details': '数据统一处理完成' if result else '数据统一处理失败'
            }

            self.collection_stats['processing_steps'].append(step_result)
            return result

        except Exception as e:
            logger.error(f"❌ 数据统一处理失败: {e}")
            step_result = {
                'step': '数据统一',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def run_data_enhancement(self) -> bool:
        """运行数据增强"""
        logger.info("🚀 开始数据增强...")

        try:
            # 调用数据增强器
            from collectors.data_enhancer import DataEnhancer

            enhancer = DataEnhancer()
            kp_file, q_file = enhancer.run_full_enhancement()

            step_result = {
                'step': '数据增强',
                'status': 'success' if kp_file and q_file else 'failed',
                'timestamp': datetime.now().isoformat(),
                'details': f'知识点增强: {kp_file}, 题目增强: {q_file}' if kp_file and q_file else '数据增强失败'
            }

            self.collection_stats['processing_steps'].append(step_result)
            return kp_file and q_file

        except Exception as e:
            logger.error(f"❌ 数据增强失败: {e}")
            step_result = {
                'step': '数据增强',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def run_data_validation(self) -> bool:
        """运行数据验证"""
        logger.info("🔍 开始数据验证...")

        try:
            # 调用数据验证脚本
            from scripts.validate_data import validate_data_quality
            result = validate_data_quality()

            step_result = {
                'step': '数据验证',
                'status': 'success' if result else 'failed',
                'timestamp': datetime.now().isoformat(),
                'details': '数据验证完成' if result else '数据验证失败'
            }

            self.collection_stats['processing_steps'].append(step_result)
            return result

        except Exception as e:
            logger.error(f"❌ 数据验证失败: {e}")
            step_result = {
                'step': '数据验证',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def generate_quality_report(self) -> bool:
        """生成质量报告"""
        logger.info("📊 生成质量报告...")

        try:
            # 统计数据
            self._collect_statistics()

            # 生成综合报告
            report = self._generate_comprehensive_report()

            # 保存报告
            report_file = os.path.join(
                self.processed_dir,
                f'data_collection_comprehensive_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 质量报告已生成: {report_file}")

            step_result = {
                'step': '质量报告',
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'details': f'报告已保存: {report_file}'
            }

            self.collection_stats['processing_steps'].append(step_result)
            return True

        except Exception as e:
            logger.error(f"❌ 质量报告生成失败: {e}")
            step_result = {
                'step': '质量报告',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def _collect_statistics(self):
        """收集数据统计信息"""
        try:
            # 统计知识点数量
            kp_files = list(Path(self.processed_dir).glob('knowledge_points_*.csv'))
            total_kp = 0

            for file_path in kp_files:
                try:
                    df = pd.read_csv(file_path)
                    total_kp += len(df)
                except:
                    continue

            # 统计题目数量
            q_files = list(Path(self.processed_dir).glob('questions_*.csv'))
            total_q = 0

            for file_path in q_files:
                try:
                    df = pd.read_csv(file_path)
                    total_q += len(df)
                except:
                    continue

            # 统计学科数量
            subjects = set()
            for file_path in kp_files + q_files:
                try:
                    df = pd.read_csv(file_path)
                    if 'subject' in df.columns:
                        subjects.update(df['subject'].unique())
                except:
                    continue

            # 计算质量分数
            quality_score = self._calculate_overall_quality()

            self.collection_stats.update({
                'total_knowledge_points': total_kp,
                'total_questions': total_q,
                'total_subjects': len(subjects),
                'data_quality_score': quality_score
            })

        except Exception as e:
            logger.error(f"❌ 统计收集失败: {e}")

    def _calculate_overall_quality(self) -> float:
        """计算整体数据质量分数"""
        try:
            # 基于各种指标计算质量分数
            quality_score = 0.0
            score_factors = 0

            # 检查数据完整性
            required_files = [
                'knowledge_points_unified_*.csv',
                'questions_unified_*.csv',
                'validation_report.json'
            ]

            for pattern in required_files:
                files = list(Path(self.processed_dir).glob(pattern))
                if files:
                    quality_score += 20.0  # 每个必需文件20分
                    score_factors += 1

            # 检查数据量
            if self.collection_stats.get('total_knowledge_points', 0) > 200:
                quality_score += 15.0
            elif self.collection_stats.get('total_knowledge_points', 0) > 100:
                quality_score += 10.0

            if self.collection_stats.get('total_questions', 0) > 500:
                quality_score += 15.0
            elif self.collection_stats.get('total_questions', 0) > 200:
                quality_score += 10.0

            # 检查学科覆盖
            if self.collection_stats.get('total_subjects', 0) >= 6:
                quality_score += 15.0
            elif self.collection_stats.get('total_subjects', 0) >= 3:
                quality_score += 10.0

            # 验证报告质量
            validation_report = os.path.join(self.processed_dir, 'validation_report.json')
            if os.path.exists(validation_report):
                try:
                    with open(validation_report, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        overall_quality = report.get('validation_summary', {}).get('overall_quality', 'unknown')
                        if overall_quality == 'excellent':
                            quality_score += 15.0
                        elif overall_quality == 'good':
                            quality_score += 10.0
                        elif overall_quality == 'fair':
                            quality_score += 5.0
                except:
                    pass

            # 标准化为0-100分
            max_score = 100.0
            return min(max_score, quality_score)

        except Exception as e:
            logger.error(f"❌ 质量计算失败: {e}")
            return 0.0

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        return {
            'report_type': 'comprehensive_data_collection_report',
            'generation_time': datetime.now().isoformat(),
            'summary': {
                'total_knowledge_points': self.collection_stats['total_knowledge_points'],
                'total_questions': self.collection_stats['total_questions'],
                'total_subjects': self.collection_stats['total_subjects'],
                'data_quality_score': self.collection_stats['data_quality_score'],
                'overall_grade': self._get_quality_grade(self.collection_stats['data_quality_score'])
            },
            'detailed_statistics': self.collection_stats,
            'processing_history': self.collection_stats['processing_steps'],
            'file_inventory': self._generate_file_inventory(),
            'recommendations': self._generate_recommendations(),
            'next_steps': [
                '检查数据质量报告',
                '根据建议优化数据收集策略',
                '准备数据导入数据库',
                '进行AI模型训练测试',
                '监控数据使用效果'
            ]
        }

    def _get_quality_grade(self, score: float) -> str:
        """根据分数获取质量等级"""
        if score >= 90:
            return '优秀 (A级)'
        elif score >= 80:
            return '良好 (B级)'
        elif score >= 70:
            return '一般 (C级)'
        elif score >= 60:
            return '需改进 (D级)'
        else:
            return '不合格 (F级)'

    def _generate_file_inventory(self) -> Dict[str, List[str]]:
        """生成文件清单"""
        inventory = {}

        # 知识点文件
        kp_files = list(Path(self.processed_dir).glob('knowledge_points_*.csv'))
        inventory['knowledge_points'] = [str(f.name) for f in sorted(kp_files)]

        # 题目文件
        q_files = list(Path(self.processed_dir).glob('questions_*.csv'))
        inventory['questions'] = [str(f.name) for f in sorted(q_files)]

        # 报告文件
        report_files = list(Path(self.processed_dir).glob('*report*.json'))
        inventory['reports'] = [str(f.name) for f in sorted(report_files)]

        return inventory

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        quality_score = self.collection_stats['data_quality_score']

        if quality_score < 60:
            recommendations.append('数据质量不合格，建议重新收集数据')
        elif quality_score < 80:
            recommendations.append('数据质量一般，建议增加更多高质量数据源')

        if self.collection_stats['total_knowledge_points'] < 300:
            recommendations.append('知识点数量不足，建议增加知识点收集量')

        if self.collection_stats['total_questions'] < 800:
            recommendations.append('题目数量不足，建议增加题目收集量')

        if self.collection_stats['total_subjects'] < 6:
            recommendations.append('学科覆盖不够全面，建议增加更多学科数据')

        # 检查处理步骤是否都成功
        failed_steps = [step for step in self.collection_stats['processing_steps'] if step['status'] == 'failed']
        if failed_steps:
            recommendations.append(f'发现 {len(failed_steps)} 个处理步骤失败，需要重新执行')

        if not recommendations:
            recommendations.append('数据质量良好，可以进行下一步处理')

        return recommendations

    def import_data_to_database(self) -> bool:
        """导入数据到数据库"""
        logger.info("💾 开始数据导入...")
        
        try:
            from scripts.import_to_db import import_to_database
            result = import_to_database()
            
            step_result = {
                'step': '数据导入',
                'status': 'success' if result else 'failed',
                'timestamp': datetime.now().isoformat(),
                'details': '数据导入完成' if result else '数据导入失败'
            }
            
            self.collection_stats['processing_steps'].append(step_result)
            return result
            
        except Exception as e:
            logger.error(f"❌ 数据导入失败: {e}")
            step_result = {
                'step': '数据导入',
                'status': 'failed',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self.collection_stats['processing_steps'].append(step_result)
            return False

    def collect_data_by_method(self, method="all") -> bool:
        """按指定方法收集数据"""
        logger.info(f"🚀 开始数据收集: {method}")
        
        try:
            if method in ["all", "ai"]:
                logger.info("🤖 运行AI数据生成器...")
                from collectors.smart_data_generator import SmartDataGenerator
                generator = SmartDataGenerator()
                generator.generate_full_dataset(
                    subjects=['math', 'chinese', 'english', 'physics', 'chemistry', 'biology'],
                    kp_per_subject=50,
                    q_per_subject=80
                )
            
            if method in ["all", "crawl"]:
                logger.info("🌐 运行网站爬虫...")
                from collectors.legal_education_crawler import main as crawler_main
                crawler_main()
            
            if method in ["all", "pdf"]:
                logger.info("📄 运行PDF处理器...")
                from collectors.pdf_document_processor import main as pdf_main
                pdf_main()
            
            logger.info("✅ 数据收集完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据收集失败: {e}")
            return False

    def run_full_collection_pipeline(self, include_import: bool = True) -> bool:
        """运行完整的数据收集流程"""
        logger.info("🚀 开始完整数据收集流程...")

        # 添加数据导入步骤
        pipeline = self.processing_pipeline.copy()
        if include_import:
            pipeline.append({'name': '数据导入', 'function': self.import_data_to_database, 'required': False})

        success_count = 0
        total_steps = len(pipeline)

        for step in pipeline:
            logger.info(f"\n{'='*50}")
            logger.info(f"📋 执行步骤: {step['name']}")
            logger.info(f"{'='*50}")

            if step['function']():
                success_count += 1
                logger.info(f"✅ {step['name']} 完成")
            else:
                if step['required']:
                    logger.error(f"❌ 必需步骤 {step['name']} 失败，终止流程")
                    break
                else:
                    logger.warning(f"⚠️ 可选步骤 {step['name']} 失败，继续执行")

        success_rate = success_count / total_steps * 100
        logger.info(f"\n{'='*50}")
        logger.info("🎉 数据收集流程完成！")
        logger.info(f"📊 成功率: {success_count}/{total_steps} ({success_rate:.1f}%)")
        logger.info(f"{'='*50}")

        return success_rate >= 80.0  # 80%成功率视为成功

    def get_collection_status(self) -> Dict[str, Any]:
        """获取收集状态"""
        return {
            'status': 'running' if any(s['status'] == 'success' for s in self.collection_stats['processing_steps']) else 'not_started',
            'progress': len([s for s in self.collection_stats['processing_steps'] if s['status'] == 'success']) / len(self.processing_pipeline) * 100,
            'current_step': self.collection_stats['processing_steps'][-1]['step'] if self.collection_stats['processing_steps'] else '未开始',
            'statistics': self.collection_stats
        }

    def get_data_status(self) -> Dict[str, Any]:
        """获取数据状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "raw_data": {},
            "processed_data": {},
            "database_status": "unknown"
        }
        
        # 检查原始数据
        raw_dir = os.path.join(self.base_dir, "..", "raw", "subjects")
        if os.path.exists(raw_dir):
            for subject in os.listdir(raw_dir):
                subject_dir = os.path.join(raw_dir, subject)
                if os.path.isdir(subject_dir):
                    file_count = sum([len(files) for r, d, files in os.walk(subject_dir)])
                    status["raw_data"][subject] = file_count
        
        # 检查处理后数据
        kp_file = os.path.join(self.processed_dir, "knowledge_points_unified.csv")
        q_file = os.path.join(self.processed_dir, "questions_unified.csv")
        
        status["processed_data"]["knowledge_points_exists"] = os.path.exists(kp_file)
        status["processed_data"]["questions_exists"] = os.path.exists(q_file)
        
        if status["processed_data"]["knowledge_points_exists"]:
            df = pd.read_csv(kp_file)
            status["processed_data"]["knowledge_points_count"] = len(df)
        
        if status["processed_data"]["questions_exists"]:
            df = pd.read_csv(q_file)
            status["processed_data"]["questions_count"] = len(df)
        
        return status

    def show_interactive_menu(self):
        """显示交互式菜单"""
        print("\n" + "="*60)
        print("📚 AI作业批改系统 - 统一数据管理工具")
        print("="*60)
        print("1. 🤖 收集数据 (AI生成)")
        print("2. 🌐 收集数据 (网站爬虫)")
        print("3. 📄 收集数据 (PDF处理)")
        print("4. 🔄 收集数据 (全部方式)")
        print("5. ⚙️  处理数据")
        print("6. 🔍 验证数据")
        print("7. 🚀 增强数据")
        print("8. 💾 导入数据库")
        print("9. 🎯 运行完整管道")
        print("10. 📊 查看数据状态")
        print("11. 📋 查看收集状态")
        print("12. ❌ 退出")
        print("="*60)

    def run_interactive_mode(self):
        """运行交互模式"""
        while True:
            self.show_interactive_menu()
            choice = input("请选择操作 (1-12): ").strip()
            
            if choice == "1":
                self.collect_data_by_method("ai")
            elif choice == "2":
                self.collect_data_by_method("crawl")
            elif choice == "3":
                self.collect_data_by_method("pdf")
            elif choice == "4":
                self.collect_data_by_method("all")
            elif choice == "5":
                self.run_data_unification()
            elif choice == "6":
                self.run_data_validation()
            elif choice == "7":
                self.run_data_enhancement()
            elif choice == "8":
                self.import_data_to_database()
            elif choice == "9":
                collect_method = input("选择收集方式 (ai/crawl/pdf/all) [all]: ").strip() or "all"
                self.collect_data_by_method(collect_method)
                self.run_full_collection_pipeline(include_import=True)
            elif choice == "10":
                status = self.get_data_status()
                print("\n📊 数据状态:")
                print(f"📅 检查时间: {status['timestamp']}")
                print(f"📁 原始数据: {status['raw_data']}")
                print(f"⚙️  处理后数据: {status['processed_data']}")
            elif choice == "11":
                status = self.get_collection_status()
                print("\n📋 收集状态:")
                print(json.dumps(status, ensure_ascii=False, indent=2))
            elif choice == "12":
                print("👋 退出数据管理工具")
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    logger.info("🧠 启动数据收集管理平台...")

    try:
        manager = DataCollectionManager()

        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == 'status':
                status = manager.get_collection_status()
                logger.info("📊 当前状态:")
                logger.info(json.dumps(status, ensure_ascii=False, indent=2))

            elif command == 'data-status':
                status = manager.get_data_status()
                logger.info("📊 数据状态:")
                logger.info(json.dumps(status, ensure_ascii=False, indent=2))

            elif command == 'interactive' or command == 'menu':
                manager.run_interactive_mode()

            elif command == 'full':
                success = manager.run_full_collection_pipeline()
                if success:
                    logger.info("🎉 完整数据收集流程成功完成！")
                else:
                    logger.error("❌ 完整数据收集流程失败")

            elif command == 'collect':
                method = sys.argv[2] if len(sys.argv) > 2 else "all"
                success = manager.collect_data_by_method(method)
                if success:
                    logger.info(f"✅ 数据收集 ({method}) 完成")
                else:
                    logger.error(f"❌ 数据收集 ({method}) 失败")

            elif command == 'step':
                if len(sys.argv) > 2:
                    step_name = sys.argv[2]
                    step_functions = {
                        'collection': manager.run_data_collection,
                        'unification': manager.run_data_unification,
                        'enhancement': manager.run_data_enhancement,
                        'validation': manager.run_data_validation,
                        'report': manager.generate_quality_report,
                        'import': manager.import_data_to_database
                    }

                    if step_name in step_functions:
                        success = step_functions[step_name]()
                        if success:
                            logger.info(f"✅ {step_name} 步骤完成")
                        else:
                            logger.error(f"❌ {step_name} 步骤失败")
                    else:
                        logger.error(f"❌ 未知步骤: {step_name}")
                        logger.info("可用步骤: collection, unification, enhancement, validation, report, import")
                else:
                    logger.error("❌ 请指定步骤名称: collection, unification, enhancement, validation, report, import")

            elif command == 'help':
                print("\n📖 可用命令:")
                print("  status          - 查看收集状态")
                print("  data-status     - 查看数据状态")
                print("  interactive     - 进入交互模式")
                print("  full            - 运行完整流程")
                print("  collect [method] - 收集数据 (ai/crawl/pdf/all)")
                print("  step [name]     - 运行单个步骤")
                print("  help            - 显示帮助信息")

            else:
                logger.error(f"❌ 未知命令: {command}")
                logger.info("使用 'help' 查看可用命令")

        else:
            # 默认进入交互模式
            manager.run_interactive_mode()

    except Exception as e:
        logger.error(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

