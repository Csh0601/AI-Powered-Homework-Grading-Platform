#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批改结果的唯一性
确保每次调用批改函数都会返回不同的结果
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加后端路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'llmhomework_Backend')
sys.path.insert(0, backend_dir)

from app.services.grading import grade_homework

def test_grading_uniqueness():
    """测试批改结果的唯一性"""
    print("开始测试批改结果唯一性...")
    
    # 测试数据
    test_questions = [
        "1. 2+2=?: 4",
        "2. 中国的首都是?: 北京", 
        "3. 1+1=?: 2",
        "4. 对错题: 对",
        "5. 选择题: A",
        "6. 填空题: 答案",
        "7. 没有答案的题目",
        "8. 另一个题目: 答案B"
    ]
    
    results = []
    
    # 进行多次批改测试
    for i in range(5):
        print(f"\n第 {i+1} 次批改测试:")
        print("-" * 50)
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行批改
        grading_result = grade_homework(test_questions)
        
        # 记录结束时间
        end_time = time.time()
        
        # 统计结果
        correct_count = sum(1 for r in grading_result if r['correct'])
        total_score = sum(r['score'] for r in grading_result)
        
        print(f"批改时间: {end_time - start_time:.3f}秒")
        print(f"正确题目数: {correct_count}/{len(grading_result)}")
        print(f"总分: {total_score:.1f}")
        
        # 显示每个题目的结果
        for j, result in enumerate(grading_result):
            status = "✓" if result['correct'] else "✗"
            print(f"  {j+1}. {status} {result['type']} - 得分: {result['score']} - {result['explanation']}")
        
        # 保存结果用于比较
        results.append({
            'test_id': i + 1,
            'timestamp': datetime.now().isoformat(),
            'correct_count': correct_count,
            'total_score': total_score,
            'grading_result': grading_result
        })
    
    # 分析结果唯一性
    print("\n" + "="*60)
    print("唯一性分析结果:")
    print("="*60)
    
    # 检查正确题目数是否不同
    correct_counts = [r['correct_count'] for r in results]
    unique_correct_counts = set(correct_counts)
    
    print(f"正确题目数变化: {correct_counts}")
    print(f"唯一正确题目数: {len(unique_correct_counts)}")
    
    if len(unique_correct_counts) > 1:
        print("✓ 正确题目数在不同测试中有变化")
    else:
        print("✗ 正确题目数在所有测试中相同")
    
    # 检查总分是否不同
    total_scores = [r['total_score'] for r in results]
    unique_total_scores = set(total_scores)
    
    print(f"总分变化: {total_scores}")
    print(f"唯一总分: {len(unique_total_scores)}")
    
    if len(unique_total_scores) > 1:
        print("✓ 总分在不同测试中有变化")
    else:
        print("✗ 总分在所有测试中相同")
    
    # 检查每个题目的正确性是否不同
    question_correctness = {}
    for i, question in enumerate(test_questions):
        correctness_list = []
        for result in results:
            if i < len(result['grading_result']):
                correctness_list.append(result['grading_result'][i]['correct'])
        question_correctness[f"题目{i+1}"] = correctness_list
    
    print("\n各题目正确性变化:")
    for question, correctness in question_correctness.items():
        unique_correctness = set(correctness)
        if len(unique_correctness) > 1:
            print(f"  {question}: ✓ 有变化 {correctness}")
        else:
            print(f"  {question}: ✗ 无变化 {correctness}")
    
    # 保存详细结果到文件
    with open('grading_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: grading_test_results.json")
    
    # 总结
    print("\n" + "="*60)
    print("测试总结:")
    print("="*60)
    
    uniqueness_score = 0
    total_checks = 3  # 正确数、总分、题目正确性
    
    if len(unique_correct_counts) > 1:
        uniqueness_score += 1
    if len(unique_total_scores) > 1:
        uniqueness_score += 1
    
    # 检查题目正确性变化
    question_changes = sum(1 for correctness in question_correctness.values() if len(set(correctness)) > 1)
    if question_changes > 0:
        uniqueness_score += 1
    
    print(f"唯一性评分: {uniqueness_score}/{total_checks}")
    
    if uniqueness_score == total_checks:
        print("🎉 测试通过！批改结果具有良好的唯一性")
    elif uniqueness_score >= 2:
        print("✅ 测试基本通过！批改结果有一定的唯一性")
    else:
        print("❌ 测试失败！批改结果缺乏唯一性")
    
    return uniqueness_score == total_checks

if __name__ == "__main__":
    success = test_grading_uniqueness()
    sys.exit(0 if success else 1) 