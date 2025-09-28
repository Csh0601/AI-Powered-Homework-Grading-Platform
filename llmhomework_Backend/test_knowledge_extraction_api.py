#!/usr/bin/env python3
"""
知识点提取API测试脚本
测试Day 8完成的高精度知识点提取系统
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:5000/api/knowledge"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康检查通过")
            print(f"   服务状态: {data['data']['status']}")
            print(f"   知识点提取器: {'可用' if data['data']['services']['knowledge_extractor'] else '不可用'}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_knowledge_extraction():
    """测试知识点提取"""
    print("\n🔍 测试知识点提取...")
    
    test_cases = [
        {
            "question_text": "解一元一次方程：2x + 3 = 7，求x的值",
            "subject_hint": "math",
            "expected_kp": "equations"
        },
        {
            "question_text": "已知三角形ABC的三边长分别为3、4、5，求该三角形的面积",
            "subject_hint": "math",
            "expected_kp": "geometry_triangle"
        },
        {
            "question_text": "分析《春晓》这首古诗中诗人表达的情感和运用的意象",
            "subject_hint": "chinese",
            "expected_kp": "poetry_analysis"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  测试用例 {i}: {test_case['question_text'][:30]}...")
        
        payload = {
            "question_text": test_case["question_text"],
            "subject_hint": test_case["subject_hint"],
            "top_k": 3,
            "extraction_method": "ensemble"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/extract", json=payload)
            if response.status_code == 200:
                data = response.json()
                extractions = data['data']['extractions']
                
                if extractions:
                    print(f"   ✅ 提取成功: {len(extractions)}个知识点")
                    for j, extraction in enumerate(extractions[:2], 1):
                        print(f"      {j}. {extraction['knowledge_point']} ({extraction['subject']}) - 置信度: {extraction['confidence']:.3f}")
                    
                    # 检查是否包含期望的知识点
                    found_expected = any(ext['knowledge_point'] == test_case['expected_kp'] for ext in extractions)
                    if found_expected:
                        print(f"   ✅ 找到期望知识点: {test_case['expected_kp']}")
                    else:
                        print(f"   ⚠️ 未找到期望知识点: {test_case['expected_kp']}")
                else:
                    print("   ❌ 未提取到知识点")
            else:
                print(f"   ❌ 提取失败: {response.status_code}")
                print(f"      错误信息: {response.text}")
        except Exception as e:
            print(f"   ❌ 提取异常: {e}")

def test_batch_extraction():
    """测试批量提取"""
    print("\n🔍 测试批量知识点提取...")
    
    payload = {
        "questions": [
            "解一元一次方程：2x + 3 = 7",
            "计算三角形的面积",
            "分析古诗的情感表达"
        ],
        "subject_hints": ["math", "math", "chinese"],
        "top_k": 2,
        "extraction_method": "ensemble"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/extract/batch", json=payload)
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            
            print(f"✅ 批量提取成功: {len(results)}个问题")
            for i, result in enumerate(results, 1):
                print(f"   问题{i}: {result['question'][:20]}...")
                print(f"     提取到 {result['extraction_count']} 个知识点")
                for extraction in result['extractions'][:2]:
                    print(f"       - {extraction['knowledge_point']} ({extraction['subject']})")
        else:
            print(f"❌ 批量提取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 批量提取异常: {e}")

def test_extraction_statistics():
    """测试提取统计"""
    print("\n🔍 测试提取统计...")
    
    try:
        response = requests.get(f"{BASE_URL}/extract/statistics")
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            
            print("✅ 统计信息获取成功:")
            print(f"   总提取次数: {stats.get('total_extractions', 0)}")
            print(f"   成功提取次数: {stats.get('successful_extractions', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0):.2%}")
            
            if stats.get('top_knowledge_points'):
                print("   热门知识点:")
                for kp, count in list(stats['top_knowledge_points'].items())[:3]:
                    print(f"     - {kp}: {count}次")
        else:
            print(f"❌ 统计信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息获取异常: {e}")

def main():
    """主测试函数"""
    print("🧪 知识点提取API测试开始")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health_check():
        print("\n❌ 服务不可用，请先启动后端服务")
        return
    
    # 测试知识点提取
    test_knowledge_extraction()
    
    # 测试批量提取
    test_batch_extraction()
    
    # 测试统计信息
    test_extraction_statistics()
    
    print("\n" + "=" * 50)
    print("✅ 知识点提取API测试完成")

if __name__ == "__main__":
    main()
