#!/usr/bin/env python3
"""
测试相似度搜索API功能
Day10任务验证脚本
"""

import requests
import json
import time

def test_similarity_search_api():
    """测试相似度搜索API"""
    print("🧪 测试相似度搜索API...")
    
    # API端点
    base_url = "http://localhost:5000"
    api_url = f"{base_url}/api/question_bank/find_similar"
    
    # 测试数据
    test_query = {
        "query_question": {
            "stem": "解一元一次方程：2x + 3 = 7，求x的值",
            "correct_answer": "x = 2",
            "question_type": "calculation",
            "difficulty_level": 2,
            "subject": "math"
        },
        "top_k": 5,
        "similarity_threshold": 0.3
    }
    
    try:
        print(f"📡 发送请求到: {api_url}")
        print(f"📝 查询题目: {test_query['query_question']['stem']}")
        
        # 发送POST请求
        response = requests.post(
            api_url,
            json=test_query,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result['data']
                similar_questions = data.get('similar_questions', [])
                
                print(f"✅ 找到 {len(similar_questions)} 个相似题目:")
                
                for i, item in enumerate(similar_questions, 1):
                    print(f"\n{i}. 相似度: {item['similarity_score']:.3f}")
                    print(f"   题目: {item['question']['stem']}")
                    print(f"   答案: {item['question']['correct_answer']}")
                    print(f"   匹配原因: {', '.join(item['match_reasons'])}")
                
                # 显示统计信息
                search_stats = data.get('search_statistics', {})
                index_stats = data.get('index_statistics', {})
                
                print(f"\n📈 搜索统计:")
                print(f"   平均搜索时间: {search_stats.get('avg_search_time_ms', 0):.2f} ms")
                print(f"   索引题目数: {index_stats.get('indexed_questions', 0)}")
                print(f"   向量维度: {index_stats.get('vector_dimensions', 0)}")
                print(f"   构建时间: {index_stats.get('build_time_seconds', 0):.3f} 秒")
                
                return True
            else:
                print(f"❌ API返回错误: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行 (python run.py)")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_multiple_queries():
    """测试多个查询"""
    print("\n🔄 测试多个查询...")
    
    base_url = "http://localhost:5000"
    api_url = f"{base_url}/api/question_bank/find_similar"
    
    test_queries = [
        {
            "query_question": {
                "stem": "计算三角形的面积，已知底边为6米，高为4米",
                "correct_answer": "12平方米",
                "question_type": "calculation",
                "difficulty_level": 2,
                "subject": "math"
            },
            "top_k": 3
        },
        {
            "query_question": {
                "stem": "选择正确答案：下列哪个是质数？A.4 B.6 C.7 D.8",
                "correct_answer": "C",
                "question_type": "single_choice",
                "difficulty_level": 1,
                "subject": "math"
            },
            "top_k": 3
        }
    ]
    
    success_count = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试查询 {i} ---")
        print(f"题目: {query['query_question']['stem']}")
        
        try:
            response = requests.post(
                api_url,
                json=query,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    similar_count = len(result['data'].get('similar_questions', []))
                    print(f"✅ 找到 {similar_count} 个相似题目")
                    success_count += 1
                else:
                    print(f"❌ 查询失败: {result.get('message')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 查询异常: {str(e)}")
    
    print(f"\n📊 多查询测试结果: {success_count}/{len(test_queries)} 成功")
    return success_count == len(test_queries)

def main():
    """主测试函数"""
    print("🚀 开始测试Day10相似度搜索功能...")
    print("=" * 50)
    
    # 测试1: 基本相似度搜索
    test1_success = test_similarity_search_api()
    
    # 测试2: 多个查询
    test2_success = test_multiple_queries()
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"   基本相似度搜索: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"   多查询测试: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n🎉 所有测试通过！Day10相似度搜索功能工作正常")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查后端服务")
        return False

if __name__ == "__main__":
    main()
