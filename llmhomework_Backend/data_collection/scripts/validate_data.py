#!/usr/bin/env python3
"""
统一数据质量验证脚本
验证收集的数据是否符合质量标准
"""

import os
import sys
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data_quality():
    """验证数据质量"""
    logger.info("🔍 开始数据质量验证...")

    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        processed_dir = os.path.join(base_dir, "processed")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_summary": {
                "total_files_checked": 0,
                "total_records": 0,
                "data_quality_issues": 0,
                "overall_quality": "unknown"
            },
            "file_details": {},
            "quality_metrics": {},
            "recommendations": []
        }

        # 检查处理后的统一数据文件
        files_to_check = [
            ("knowledge_points_unified.csv", "知识点"),
            ("questions_unified.csv", "题目")
        ]

        total_records = 0
        total_issues = 0

        for filename, data_type in files_to_check:
            file_path = os.path.join(processed_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    record_count = len(df)
                    total_records += record_count
                    
                    # 检查数据质量
                    quality_issues = check_data_quality(df, data_type)
                    total_issues += len(quality_issues)
                    
                    validation_results["file_details"][filename] = {
                        "exists": True,
                        "record_count": record_count,
                        "columns": list(df.columns),
                        "quality_issues": quality_issues,
                        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
                    }
                    
                    validation_results["validation_summary"]["total_files_checked"] += 1
                    logger.info(f"✅ {data_type}数据: {record_count} 条记录, {len(quality_issues)} 个质量问题")
                    
                except Exception as e:
                    validation_results["file_details"][filename] = {
                        "exists": True,
                        "error": str(e)
                    }
                    logger.error(f"❌ 读取 {filename} 失败: {e}")
            else:
                validation_results["file_details"][filename] = {"exists": False}
                logger.warning(f"⚠️ 文件不存在: {filename}")

        # 更新汇总信息
        validation_results["validation_summary"]["total_records"] = total_records
        validation_results["validation_summary"]["data_quality_issues"] = total_issues
        
        # 计算质量等级
        if total_records == 0:
            quality_grade = "no_data"
        elif total_issues == 0:
            quality_grade = "excellent"
        elif total_issues / total_records < 0.05:
            quality_grade = "good"
        elif total_issues / total_records < 0.15:
            quality_grade = "fair"
        else:
            quality_grade = "poor"
            
        validation_results["validation_summary"]["overall_quality"] = quality_grade

        # 生成质量指标
        validation_results["quality_metrics"] = generate_quality_metrics(validation_results)

        # 生成建议
        validation_results["recommendations"] = generate_recommendations(validation_results)

        # 保存验证报告
        report_file = os.path.join(
            processed_dir,
            f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 验证报告已保存: {report_file}")
        logger.info(f"📊 质量等级: {quality_grade}")
        logger.info(f"📈 总记录数: {total_records}, 质量问题: {total_issues}")

        return True

    except Exception as e:
        logger.error(f"❌ 数据验证失败: {e}")
        return False

def check_data_quality(df, data_type):
    """检查数据框的质量问题"""
    issues = []
    
    # 检查空值
    null_counts = df.isnull().sum()
    for col, null_count in null_counts.items():
        if null_count > 0:
            issues.append(f"{col}列有{null_count}个空值")
    
    # 检查重复记录
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"发现{duplicates}条重复记录")
    
    # 根据数据类型进行特定检查
    if data_type == "知识点":
        # 检查必需字段
        required_fields = ['subject', 'knowledge_point', 'description']
        for field in required_fields:
            if field not in df.columns:
                issues.append(f"缺少必需字段: {field}")
            elif df[field].isnull().any():
                issues.append(f"必需字段{field}包含空值")
    
    elif data_type == "题目":
        # 检查必需字段
        required_fields = ['subject', 'question', 'answer']
        for field in required_fields:
            if field not in df.columns:
                issues.append(f"缺少必需字段: {field}")
            elif df[field].isnull().any():
                issues.append(f"必需字段{field}包含空值")
    
    # 检查文本长度
    for col in df.select_dtypes(include=['object']).columns:
        avg_length = df[col].dropna().str.len().mean()
        if avg_length < 10:  # 文本太短可能是质量问题
            issues.append(f"{col}列平均长度过短({avg_length:.1f}字符)")
    
    return issues

def generate_quality_metrics(validation_results):
    """生成质量指标"""
    metrics = {}
    
    total_files = validation_results["validation_summary"]["total_files_checked"]
    total_records = validation_results["validation_summary"]["total_records"]
    total_issues = validation_results["validation_summary"]["data_quality_issues"]
    
    if total_records > 0:
        metrics["data_completeness"] = (total_records - total_issues) / total_records * 100
        metrics["error_rate"] = total_issues / total_records * 100
    else:
        metrics["data_completeness"] = 0
        metrics["error_rate"] = 100
    
    metrics["file_coverage"] = total_files / 2 * 100  # 期望2个文件
    
    return metrics

def generate_recommendations(validation_results):
    """生成改进建议"""
    recommendations = []
    
    quality = validation_results["validation_summary"]["overall_quality"]
    total_records = validation_results["validation_summary"]["total_records"]
    total_issues = validation_results["validation_summary"]["data_quality_issues"]
    
    if quality == "no_data":
        recommendations.append("没有找到数据文件，请先运行数据收集和统一处理")
    elif quality == "poor":
        recommendations.append("数据质量较差，建议重新收集数据")
        recommendations.append("检查数据生成和处理流程")
    elif quality == "fair":
        recommendations.append("数据质量一般，建议增强数据质量")
        recommendations.append("清理重复和无效数据")
    elif quality == "good":
        recommendations.append("数据质量良好，可以进行下一步处理")
    elif quality == "excellent":
        recommendations.append("数据质量优秀，可以直接用于训练")
    
    if total_records < 500:
        recommendations.append("数据量不足，建议增加更多数据")
    
    if total_issues > 0:
        recommendations.append(f"发现{total_issues}个质量问题，建议进行数据清理")
    
    return recommendations

def main():
    """主函数"""
    logger.info("🔍 启动数据质量验证...")
    
    success = validate_data_quality()
    
    if success:
        logger.info("✅ 数据质量验证完成")
    else:
        logger.error("❌ 数据质量验证失败")
    
    return success

if __name__ == "__main__":
    main()