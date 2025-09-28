#!/usr/bin/env python3
"""
Day10 相似度搜索功能演示脚本
展示完整的相似度计算和搜索流程
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.similarity_search import SimilaritySearchEngine
import json
from datetime import datetime

def demo_similarity_search():
    """演示相似度搜索功能"""
    print("🎯 Day10 相似度搜索功能演示")
    print("=" * 60)
    
    # 1. 创建搜索引擎
    print("1️⃣ 初始化相似度搜索引擎...")
    engine = SimilaritySearchEngine()
    print("✅ 搜索引擎初始化完成")
    
    # 2. 准备测试数据
    print("\n2️⃣ 准备测试题目数据...")
    test_questions = [
        {
            'question_id': 'Q001',
            'stem': '解一元一次方程：2x + 3 = 7，求x的值',
            'correct_answer': 'x = 2',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q002',
            'stem': '解方程：3x - 5 = 10，求x的值',
            'correct_answer': 'x = 5',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q003',
            'stem': '计算三角形的面积，已知底边为6米，高为4米',
            'correct_answer': '12平方米',
            'question_type': 'calculation',
            'difficulty_level': 2,
            'subject': 'math'
        },
        {
            'question_id': 'Q004',
            'stem': '选择正确答案：下列哪个是质数？A.4 B.6 C.7 D.8',
            'correct_answer': 'C',
            'question_type': 'single_choice',
            'difficulty_level': 1,
            'subject': 'math'
        },
        {
            'question_id': 'Q005',
            'stem': '解一元二次方程：x² - 5x + 6 = 0',
            'correct_answer': 'x = 2 或 x = 3',
            'question_type': 'calculation',
            'difficulty_level': 4,
            'subject': 'math'
        },
        {
            'question_id': 'Q006',
            'stem': '分析《春晓》这首古诗中诗人表达的情感和运用的意象',
            'correct_answer': '表达了诗人对春天的喜爱和对美好时光的珍惜',
            'question_type': 'analysis',
            'difficulty_level': 3,
            'subject': 'chinese'
        }
    ]
    
    print(f"✅ 准备了 {len(test_questions)} 个测试题目")
    
    # 3. 构建索引
    print("\n3️⃣ 构建题目索引...")
    start_time = datetime.now()
    index_result = engine.build_question_index(test_questions)
    build_time = (datetime.now() - start_time).total_seconds()
    
    if index_result['success']:
        print(f"✅ 索引构建成功！")
        print(f"   - 索引题目数: {index_result['indexed_questions']}")
        print(f"   - 构建时间: {build_time:.3f} 秒")
        print(f"   - 向量维度: {index_result['vector_dimensions']}")
    else:
        print(f"❌ 索引构建失败: {index_result.get('error')}")
        return
    
    # 4. 执行相似度搜索
    print("\n4️⃣ 执行相似度搜索...")
    
    # 测试查询1: 数学方程题
    query1 = {
        'stem': '求解方程：4x + 1 = 9，x等于多少？',
        'correct_answer': 'x = 2',
        'question_type': 'calculation',
        'difficulty_level': 2,
        'subject': 'math'
    }
    
    print(f"🔍 查询1: {query1['stem']}")
    results1 = engine.find_similar_questions(query1, top_k=3, similarity_threshold=0.2)
    
    print(f"📊 找到 {len(results1)} 个相似题目:")
    for i, result in enumerate(results1, 1):
        print(f"   {i}. 相似度: {result['similarity_score']:.3f}")
        print(f"      题目: {result['question']['stem']}")
        print(f"      匹配原因: {', '.join(result['match_reasons'])}")
    
    # 测试查询2: 语文分析题
    query2 = {
        'stem': '分析《静夜思》这首诗的主题思想',
        'correct_answer': '表达了诗人对故乡的思念之情',
        'question_type': 'analysis',
        'difficulty_level': 3,
        'subject': 'chinese'
    }
    
    print(f"\n🔍 查询2: {query2['stem']}")
    results2 = engine.find_similar_questions(query2, top_k=2, similarity_threshold=0.1)
    
    print(f"📊 找到 {len(results2)} 个相似题目:")
    for i, result in enumerate(results2, 1):
        print(f"   {i}. 相似度: {result['similarity_score']:.3f}")
        print(f"      题目: {result['question']['stem']}")
        print(f"      匹配原因: {', '.join(result['match_reasons'])}")
    
    # 5. 性能统计
    print("\n5️⃣ 性能统计信息:")
    stats = engine.get_search_statistics()
    print(f"   - 总搜索次数: {stats['total_searches']}")
    print(f"   - 平均搜索时间: {stats['avg_search_time_ms']:.2f} ms")
    print(f"   - 缓存命中率: {stats['cache_hit_rate_percent']:.1f}%")
    print(f"   - 索引题目数: {stats['indexed_questions']}")
    print(f"   - 缓存大小: {stats['cache_size']}")
    
    # 6. 缓存测试
    print("\n6️⃣ 缓存机制测试...")
    print("   重复执行相同查询以测试缓存...")
    
    # 重复查询
    start_time = datetime.now()
    results3 = engine.find_similar_questions(query1, top_k=3, similarity_threshold=0.2)
    cache_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   缓存查询时间: {cache_time*1000:.2f} ms")
    
    # 更新统计
    stats_after = engine.get_search_statistics()
    print(f"   缓存命中率: {stats_after['cache_hit_rate_percent']:.1f}%")
    
    print("\n🎉 Day10 相似度搜索功能演示完成！")
    print("=" * 60)
    
    return engine

def demo_api_usage():
    """演示API使用方式"""
    print("\n📡 API使用示例:")
    print("-" * 40)
    
    api_example = {
        "endpoint": "POST /api/question_bank/find_similar",
        "request": {
            "query_question": {
                "stem": "解一元一次方程：2x + 3 = 7，求x的值",
                "correct_answer": "x = 2",
                "question_type": "calculation",
                "difficulty_level": 2,
                "subject": "math"
            },
            "top_k": 5,
            "similarity_threshold": 0.3
        },
        "response": {
            "success": True,
            "data": {
                "similar_questions": [
                    {
                        "rank": 1,
                        "question": {...},
                        "similarity_score": 0.954,
                        "similarity_breakdown": {...},
                        "match_reasons": ["题目内容高度相似", "题型完全一致"]
                    }
                ],
                "total_found": 3,
                "search_statistics": {...}
            }
        }
    }
    
    print(json.dumps(api_example, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        # 运行演示
        engine = demo_similarity_search()
        
        # 显示API使用示例
        demo_api_usage()
        
        print("\n✅ 演示完成！Day10功能运行正常。")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
