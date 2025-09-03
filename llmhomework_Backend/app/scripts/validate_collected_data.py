#!/usr/bin/env python3
"""
数据收集质量验证脚本
验证收集的知识点和题目数据的完整性和质量
"""

import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Any
import re
from datetime import datetime

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data_collection', 'processed')
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_points': {'total': 0, 'valid': 0, 'errors': []},
            'exam_questions': {'total': 0, 'valid': 0, 'errors': []},
            'mock_questions': {'total': 0, 'valid': 0, 'errors': []},
            'overall_quality': 'unknown'
        }
    
    def validate_knowledge_points(self) -> Dict[str, Any]:
        """验证知识点数据"""
        print("🔍 验证知识点数据...")
        
        csv_path = os.path.join(self.data_dir, 'knowledge_points.csv')
        if not os.path.exists(csv_path):
            print("❌ 知识点数据文件不存在")
            return {'error': '文件不存在'}
        
        try:
            df = pd.read_csv(csv_path)
            total_count = len(df)
            valid_count = 0
            errors = []
            
            # 验证必填字段
            required_fields = ['grade', 'subject', 'chapter', 'name', 'description', 
                             'difficulty_level', 'importance_level', 'exam_frequency']
            
            for index, row in df.iterrows():
                row_errors = []
                
                # 检查必填字段
                for field in required_fields:
                    if pd.isna(row[field]) or str(row[field]).strip() == '':
                        row_errors.append(f"字段 {field} 为空")
                
                # 验证数值范围
                if not pd.isna(row['difficulty_level']):
                    if not (1 <= row['difficulty_level'] <= 5):
                        row_errors.append("difficulty_level 应在1-5范围内")
                
                if not pd.isna(row['importance_level']):
                    if not (1 <= row['importance_level'] <= 5):
                        row_errors.append("importance_level 应在1-5范围内")
                
                if not pd.isna(row['exam_frequency']):
                    if not (0.0 <= row['exam_frequency'] <= 1.0):
                        row_errors.append("exam_frequency 应在0.0-1.0范围内")
                
                # 验证文本长度
                if not pd.isna(row['name']) and len(str(row['name'])) > 200:
                    row_errors.append("name 长度超过200字符")
                
                if not pd.isna(row['description']) and len(str(row['description'])) < 10:
                    row_errors.append("description 长度太短，应至少10字符")
                
                # 验证关键词
                if not pd.isna(row['keywords']):
                    keywords = str(row['keywords']).split('|')
                    if len(keywords) < 2:
                        row_errors.append("keywords 应至少包含2个关键词")
                
                if not row_errors:
                    valid_count += 1
                else:
                    errors.append({
                        'row': index + 1,
                        'name': row['name'],
                        'errors': row_errors
                    })
            
            self.validation_results['knowledge_points'] = {
                'total': total_count,
                'valid': valid_count,
                'errors': errors,
                'validation_rate': round(valid_count / total_count * 100, 2) if total_count > 0 else 0
            }
            
            print(f"✅ 知识点验证完成: {valid_count}/{total_count} 条记录有效")
            return self.validation_results['knowledge_points']
            
        except Exception as e:
            error_msg = f"验证知识点数据时出错: {str(e)}"
            print(f"❌ {error_msg}")
            self.validation_results['knowledge_points']['errors'].append(error_msg)
            return {'error': error_msg}
    
    def validate_questions(self, filename: str, question_type: str) -> Dict[str, Any]:
        """验证题目数据"""
        print(f"🔍 验证{question_type}数据...")
        
        csv_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(csv_path):
            print(f"❌ {question_type}数据文件不存在")
            return {'error': '文件不存在'}
        
        try:
            df = pd.read_csv(csv_path)
            total_count = len(df)
            valid_count = 0
            errors = []
            
            # 验证必填字段
            required_fields = ['question_id', 'subject', 'type', 'stem', 'correct_answer', 
                             'difficulty_level', 'source']
            
            for index, row in df.iterrows():
                row_errors = []
                
                # 检查必填字段
                for field in required_fields:
                    if pd.isna(row[field]) or str(row[field]).strip() == '':
                        row_errors.append(f"字段 {field} 为空")
                
                # 验证题目ID唯一性
                if not pd.isna(row['question_id']):
                    if len(str(row['question_id'])) > 100:
                        row_errors.append("question_id 长度超过100字符")
                
                # 验证题目类型
                valid_types = ['choice', 'true_false', 'fill_blank', 'application', 'calculation']
                if not pd.isna(row['type']) and row['type'] not in valid_types:
                    row_errors.append(f"type 应为以下之一: {', '.join(valid_types)}")
                
                # 验证难度等级
                if not pd.isna(row['difficulty_level']):
                    if not (1 <= row['difficulty_level'] <= 5):
                        row_errors.append("difficulty_level 应在1-5范围内")
                
                # 验证选择题选项
                if not pd.isna(row['type']) and row['type'] == 'choice':
                    if pd.isna(row.get('options')):
                        row_errors.append("选择题缺少options字段")
                    else:
                        try:
                            # 假设options是JSON格式存储
                            options = eval(str(row['options'])) if isinstance(row['options'], str) else row['options']
                            if not isinstance(options, list) or len(options) < 2:
                                row_errors.append("选择题应至少有2个选项")
                        except:
                            row_errors.append("options 格式错误")
                
                # 验证题目内容长度
                if not pd.isna(row['stem']) and len(str(row['stem'])) < 5:
                    row_errors.append("stem 内容太短")
                
                if not pd.isna(row['correct_answer']) and len(str(row['correct_answer'])) == 0:
                    row_errors.append("correct_answer 为空")
                
                if not row_errors:
                    valid_count += 1
                else:
                    errors.append({
                        'row': index + 1,
                        'question_id': row.get('question_id', 'unknown'),
                        'errors': row_errors
                    })
            
            result = {
                'total': total_count,
                'valid': valid_count,
                'errors': errors,
                'validation_rate': round(valid_count / total_count * 100, 2) if total_count > 0 else 0
            }
            
            # 保存到验证结果
            if question_type == '中考原题':
                self.validation_results['exam_questions'] = result
            elif question_type == '模拟题':
                self.validation_results['mock_questions'] = result
            
            print(f"✅ {question_type}验证完成: {valid_count}/{total_count} 条记录有效")
            return result
            
        except Exception as e:
            error_msg = f"验证{question_type}数据时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}
    
    def check_data_completeness(self) -> Dict[str, Any]:
        """检查数据完整性"""
        print("📊 检查数据完整性...")
        
        # 目标数量
        targets = {
            '数学': {'knowledge_points': 50, 'exam_questions': 20, 'mock_questions': 15},
            '语文': {'knowledge_points': 50, 'exam_questions': 20, 'mock_questions': 15},
            '英语': {'knowledge_points': 50, 'exam_questions': 20, 'mock_questions': 15},
            '物理': {'knowledge_points': 40, 'exam_questions': 20, 'mock_questions': 15},
            '化学': {'knowledge_points': 40, 'exam_questions': 20, 'mock_questions': 15},
            '生物': {'knowledge_points': 30, 'exam_questions': 20, 'mock_questions': 15},
            '历史': {'knowledge_points': 30, 'exam_questions': 20, 'mock_questions': 15},
            '地理': {'knowledge_points': 30, 'exam_questions': 20, 'mock_questions': 15},
            '政治': {'knowledge_points': 30, 'exam_questions': 20, 'mock_questions': 15}
        }
        
        completeness = {}
        
        # 检查知识点完整性
        try:
            kp_path = os.path.join(self.data_dir, 'knowledge_points.csv')
            if os.path.exists(kp_path):
                df_kp = pd.read_csv(kp_path)
                subject_counts = df_kp['subject'].value_counts()
                
                for subject in targets.keys():
                    current_count = subject_counts.get(subject, 0)
                    target_count = targets[subject]['knowledge_points']
                    completeness[f'{subject}_知识点'] = {
                        'current': current_count,
                        'target': target_count,
                        'progress': f"{current_count}/{target_count}",
                        'completion_rate': round(current_count / target_count * 100, 2)
                    }
        except Exception as e:
            print(f"❌ 检查知识点完整性时出错: {e}")
        
        # 检查题目完整性
        for file_info in [('exam_questions.csv', '中考原题'), ('mock_questions.csv', '模拟题')]:
            filename, question_type = file_info
            try:
                q_path = os.path.join(self.data_dir, filename)
                if os.path.exists(q_path):
                    df_q = pd.read_csv(q_path)
                    subject_counts = df_q['subject'].value_counts()
                    
                    for subject in targets.keys():
                        current_count = subject_counts.get(subject, 0)
                        target_key = 'exam_questions' if '中考' in question_type else 'mock_questions'
                        target_count = targets[subject][target_key]
                        completeness[f'{subject}_{question_type}'] = {
                            'current': current_count,
                            'target': target_count,
                            'progress': f"{current_count}/{target_count}",
                            'completion_rate': round(current_count / target_count * 100, 2)
                        }
            except Exception as e:
                print(f"❌ 检查{question_type}完整性时出错: {e}")
        
        return completeness
    
    def calculate_overall_quality(self) -> str:
        """计算总体数据质量"""
        quality_scores = []
        
        # 知识点质量得分
        if self.validation_results['knowledge_points']['total'] > 0:
            kp_score = self.validation_results['knowledge_points']['valid'] / self.validation_results['knowledge_points']['total']
            quality_scores.append(kp_score)
        
        # 题目质量得分
        for question_type in ['exam_questions', 'mock_questions']:
            if self.validation_results[question_type]['total'] > 0:
                q_score = self.validation_results[question_type]['valid'] / self.validation_results[question_type]['total']
                quality_scores.append(q_score)
        
        if not quality_scores:
            return 'unknown'
        
        avg_score = sum(quality_scores) / len(quality_scores)
        
        if avg_score >= 0.9:
            return 'excellent'
        elif avg_score >= 0.8:
            return 'good'
        elif avg_score >= 0.7:
            return 'fair'
        else:
            return 'poor'
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        print("📋 生成验证报告...")
        
        # 计算总体质量
        self.validation_results['overall_quality'] = self.calculate_overall_quality()
        
        # 检查完整性
        completeness = self.check_data_completeness()
        
        # 生成建议
        suggestions = []
        
        # 基于验证结果的建议
        if self.validation_results['knowledge_points']['errors']:
            suggestions.append("修复知识点数据中的错误字段")
        
        if self.validation_results['exam_questions']['errors']:
            suggestions.append("修复中考原题数据中的错误字段")
        
        if self.validation_results['mock_questions']['errors']:
            suggestions.append("修复模拟题数据中的错误字段")
        
        # 基于完整性的建议
        for key, value in completeness.items():
            if value['completion_rate'] < 50:
                suggestions.append(f"增加{key}的数据收集，当前完成度仅{value['completion_rate']:.1f}%")
        
        if not suggestions:
            suggestions.append("数据质量良好，可以进行下一步处理")
        
        report = {
            'validation_summary': {
                'overall_quality': self.validation_results['overall_quality'],
                'total_records_validated': (
                    self.validation_results['knowledge_points']['total'] +
                    self.validation_results['exam_questions']['total'] +
                    self.validation_results['mock_questions']['total']
                ),
                'validation_timestamp': self.validation_results['timestamp']
            },
            'detailed_results': self.validation_results,
            'completeness_analysis': completeness,
            'recommendations': suggestions,
            'next_actions': [
                "修复发现的数据错误",
                "补充缺失的数据项",
                "进行数据标准化处理",
                "导入数据库进行最终验证"
            ]
        }
        
        # 保存报告（处理numpy类型）
        def convert_numpy_types(obj):
            """转换numpy类型为Python原生类型"""
            if hasattr(obj, 'item'):
                return obj.item()
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            return obj
        
        report_converted = convert_numpy_types(report)
        report_path = os.path.join(self.data_dir, 'validation_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_converted, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 验证报告已保存: {report_path}")
        return report
    
    def run_validation(self) -> Dict[str, Any]:
        """执行完整的数据验证流程"""
        print("🔍 开始数据质量验证...")
        print("=" * 60)
        
        # 验证知识点数据
        self.validate_knowledge_points()
        
        # 验证题目数据
        self.validate_questions('exam_questions.csv', '中考原题')
        self.validate_questions('mock_questions.csv', '模拟题')
        
        # 生成验证报告
        report = self.generate_validation_report()
        
        print("\n" + "=" * 60)
        print("🎉 数据验证完成！")
        print(f"📊 总体质量等级: {report['validation_summary']['overall_quality']}")
        print(f"📈 验证记录总数: {report['validation_summary']['total_records_validated']}")
        print(f"💡 建议数量: {len(report['recommendations'])}")
        print("=" * 60)
        
        return report

def main():
    """主函数"""
    validator = DataValidator()
    report = validator.run_validation()
    
    # 输出验证总结
    print("\n📋 验证总结:")
    
    # 显示各类数据的验证结果
    for data_type in ['knowledge_points', 'exam_questions', 'mock_questions']:
        if data_type in report['detailed_results']:
            result = report['detailed_results'][data_type]
            if result['total'] > 0:
                print(f"  {data_type}: {result['valid']}/{result['total']} 有效 ({result.get('validation_rate', 0):.1f}%)")
    
    # 显示主要建议
    print("\n💡 主要建议:")
    for i, suggestion in enumerate(report['recommendations'][:5], 1):
        print(f"  {i}. {suggestion}")
    
    # 显示数据质量等级
    quality_levels = {
        'excellent': '优秀 🌟',
        'good': '良好 ✅',
        'fair': '一般 ⚠️',
        'poor': '需改进 ❌',
        'unknown': '未知 ❓'
    }
    quality = report['validation_summary']['overall_quality']
    print(f"\n🏆 数据质量: {quality_levels.get(quality, quality)}")

if __name__ == "__main__":
    main()
