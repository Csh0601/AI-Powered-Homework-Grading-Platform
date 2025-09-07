#!/usr/bin/env python3
"""
爬虫管理器
统一管理所有合法的数据获取工具
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.output_dir = os.path.join(self.base_dir, 'all_crawled_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 爬虫配置
        self.crawlers = {
            'smart_generator': {
                'name': '智能数据生成器',
                'module': 'smart_data_generator',
                'description': '基于课程标准生成高质量数据',
                'enabled': True,
                'priority': 1
            },
            'legal_crawler': {
                'name': '合法教育爬虫',
                'module': 'legal_education_crawler',
                'description': '爬取官方教育网站',
                'enabled': True,
                'priority': 2
            },
            'pdf_processor': {
                'name': 'PDF文档处理器',
                'module': 'pdf_document_processor',
                'description': '处理官方教育文档',
                'enabled': True,
                'priority': 3
            }
        }
        
        self.results = {
            'start_time': datetime.now().isoformat(),
            'crawlers_run': [],
            'total_knowledge_points': 0,
            'total_questions': 0,
            'errors': [],
            'files_generated': []
        }
    
    def run_crawler(self, crawler_key: str) -> Dict[str, Any]:
        """运行单个爬虫"""
        crawler_config = self.crawlers.get(crawler_key)
        if not crawler_config or not crawler_config['enabled']:
            logger.warning(f"⚠️ 爬虫 {crawler_key} 未启用或不存在")
            return {'success': False, 'error': '爬虫未启用'}
        
        logger.info(f"🚀 启动 {crawler_config['name']}...")
        
        try:
            start_time = time.time()
            
            if crawler_key == 'smart_generator':
                result = self._run_smart_generator()
            elif crawler_key == 'legal_crawler':
                result = self._run_legal_crawler()
            elif crawler_key == 'pdf_processor':
                result = self._run_pdf_processor()
            else:
                return {'success': False, 'error': f'未知爬虫: {crawler_key}'}
            
            end_time = time.time()
            duration = end_time - start_time
            
            result.update({
                'crawler': crawler_key,
                'duration': duration,
                'success': True
            })
            
            logger.info(f"✅ {crawler_config['name']} 完成，耗时 {duration:.2f}秒")
            return result
            
        except Exception as e:
            error_msg = f"{crawler_config['name']} 运行失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'crawler': crawler_key
            }
    
    def _run_smart_generator(self) -> Dict[str, Any]:
        """运行智能数据生成器"""
        try:
            from smart_data_generator import SmartDataGenerator
            
            generator = SmartDataGenerator()
            generator.generate_full_dataset(
                subjects=['math', 'chinese', 'english'],
                kp_per_subject=40,
                q_per_subject=60
            )
            
            return {
                'knowledge_points': 120,  # 3科 * 40个
                'questions': 180,         # 3科 * 60道
                'source': 'generated'
            }
            
        except ImportError:
            return {'knowledge_points': 0, 'questions': 0, 'error': '生成器模块未找到'}
    
    def _run_legal_crawler(self) -> Dict[str, Any]:
        """运行合法教育爬虫"""
        try:
            from legal_education_crawler import LegalEducationCrawler
            
            crawler = LegalEducationCrawler()
            kp_count, q_count = crawler.run_full_crawl()
            
            return {
                'knowledge_points': kp_count,
                'questions': q_count,
                'source': 'crawled'
            }
            
        except ImportError:
            return {'knowledge_points': 0, 'questions': 0, 'error': '爬虫模块未找到'}
    
    def _run_pdf_processor(self) -> Dict[str, Any]:
        """运行PDF文档处理器"""
        try:
            from pdf_document_processor import PDFDocumentProcessor
            
            processor = PDFDocumentProcessor()
            kp_count = processor.run_processing()
            
            return {
                'knowledge_points': kp_count,
                'questions': 0,  # PDF处理器主要提取知识点
                'source': 'pdf_extracted'
            }
            
        except ImportError:
            return {'knowledge_points': 0, 'questions': 0, 'error': 'PDF处理器模块未找到'}
    
    def run_all_crawlers(self):
        """运行所有启用的爬虫"""
        logger.info("🌐 开始运行所有合法爬虫...")
        
        # 按优先级排序
        sorted_crawlers = sorted(
            self.crawlers.items(),
            key=lambda x: x[1]['priority']
        )
        
        for crawler_key, config in sorted_crawlers:
            if not config['enabled']:
                continue
            
            logger.info(f"📋 {config['name']}: {config['description']}")
            
            result = self.run_crawler(crawler_key)
            self.results['crawlers_run'].append(result)
            
            if result['success']:
                self.results['total_knowledge_points'] += result.get('knowledge_points', 0)
                self.results['total_questions'] += result.get('questions', 0)
            
            # 爬虫间休息，避免过载
            time.sleep(2)
        
        self.results['end_time'] = datetime.now().isoformat()
        
        # 统一处理数据
        self._unify_all_data()
        
        # 生成报告
        self._generate_final_report()
    
    def _unify_all_data(self):
        """统一处理所有爬取的数据"""
        logger.info("🔄 开始统一处理数据...")
        
        try:
            from unify_generated_data import unify_data
            stats = unify_data()
            
            self.results['unified_stats'] = stats
            logger.info("✅ 数据统一处理完成")
            
        except Exception as e:
            error_msg = f"数据统一处理失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
    
    def _generate_final_report(self):
        """生成最终报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'crawler_session': {
                'session_id': f"crawl_session_{timestamp}",
                'start_time': self.results['start_time'],
                'end_time': self.results.get('end_time'),
                'total_duration': self._calculate_total_duration()
            },
            'crawler_results': self.results['crawlers_run'],
            'summary': {
                'total_knowledge_points': self.results['total_knowledge_points'],
                'total_questions': self.results['total_questions'],
                'successful_crawlers': len([r for r in self.results['crawlers_run'] if r['success']]),
                'failed_crawlers': len([r for r in self.results['crawlers_run'] if not r['success']]),
                'errors_count': len(self.results['errors'])
            },
            'errors': self.results['errors'],
            'unified_stats': self.results.get('unified_stats', {}),
            'next_steps': [
                '检查unified_data.csv文件质量',
                '运行数据验证脚本',
                '导入数据库',
                '测试AI批改系统'
            ]
        }
        
        # 保存报告
        report_file = os.path.join(self.output_dir, f'crawler_session_report_{timestamp}.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 最终报告已保存: {report_file}")
        
        # 控制台输出摘要
        self._print_summary(report)
        
        return report
    
    def _calculate_total_duration(self) -> float:
        """计算总运行时间"""
        if 'end_time' in self.results:
            start = datetime.fromisoformat(self.results['start_time'])
            end = datetime.fromisoformat(self.results['end_time'])
            return (end - start).total_seconds()
        return 0
    
    def _print_summary(self, report: Dict):
        """打印摘要"""
        print("\n" + "="*60)
        print("🎉 合法爬虫运行完成!")
        print("="*60)
        
        summary = report['summary']
        print(f"📊 数据统计:")
        print(f"  - 知识点总数: {summary['total_knowledge_points']}")
        print(f"  - 题目总数: {summary['total_questions']}")
        print(f"  - 成功爬虫: {summary['successful_crawlers']}")
        print(f"  - 失败爬虫: {summary['failed_crawlers']}")
        
        if summary['errors_count'] > 0:
            print(f"⚠️  错误数量: {summary['errors_count']}")
        
        print(f"\n📁 数据位置:")
        print(f"  - 统一数据: processed/knowledge_points_unified.csv")
        print(f"  - 统一题目: processed/questions_unified.csv")
        print(f"  - 详细报告: {self.output_dir}/")
        
        print(f"\n🔄 下一步操作:")
        for step in report['next_steps']:
            print(f"  - {step}")
    
    def run_quick_test(self):
        """快速测试所有爬虫"""
        logger.info("⚡ 运行快速测试...")
        
        # 只运行智能生成器（最快）
        result = self.run_crawler('smart_generator')
        
        if result['success']:
            print("✅ 快速测试成功!")
            print(f"📊 生成数据: {result.get('knowledge_points', 0)}个知识点, {result.get('questions', 0)}道题目")
        else:
            print("❌ 快速测试失败!")
            print(f"错误: {result.get('error', '未知错误')}")

def main():
    """主函数"""
    print("🎛️ 爬虫管理器")
    print("==============")
    print("1. 运行所有爬虫")
    print("2. 快速测试")
    print("3. 运行单个爬虫")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    manager = CrawlerManager()
    
    if choice == '1':
        manager.run_all_crawlers()
    elif choice == '2':
        manager.run_quick_test()
    elif choice == '3':
        print("\n可用爬虫:")
        for key, config in manager.crawlers.items():
            status = "✅" if config['enabled'] else "❌"
            print(f"  {key}: {config['name']} {status}")
        
        crawler_key = input("\n请输入爬虫key: ").strip()
        result = manager.run_crawler(crawler_key)
        
        if result['success']:
            print("✅ 爬虫运行成功!")
        else:
            print(f"❌ 爬虫运行失败: {result.get('error')}")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
