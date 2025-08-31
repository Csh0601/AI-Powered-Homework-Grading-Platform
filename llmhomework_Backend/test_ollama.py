#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Ollama 服务连接和 Llama2 模型
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.llama_service import LlamaService
from app.config import Config

def test_ollama_connection():
    """测试 Ollama 连接"""
    print("=" * 50)
    print("测试 Ollama 服务连接")
    print("=" * 50)
    
    try:
        # 尝试创建 Llama 服务
        print(f"正在连接到模型: {Config.LLAMA_MODEL_NAME}")
        llama_service = LlamaService(Config.LLAMA_MODEL_NAME)
        print("✅ Ollama 服务连接成功！")
        
        # 测试简单对话
        print("\n测试基本对话功能...")
        test_prompt = "你好，请介绍一下你自己。"
        response = llama_service.generate_response(test_prompt, max_tokens=200)
        print(f"测试提问: {test_prompt}")
        print(f"模型响应: {response}")
        
        # 测试题目类型分析
        print("\n测试题目类型分析...")
        test_question = "下列说法正确的是：A. 地球是方的 B. 太阳从西边升起 C. 水的沸点是100度 D. 1+1=3"
        question_type = llama_service.analyze_question_type(test_question)
        print(f"测试题目: {test_question}")
        print(f"识别类型: {question_type}")
        
        # 测试批改功能
        print("\n测试批改功能...")
        grading_result = llama_service.grade_question(
            test_question, 
            "C", 
            "选择题"
        )
        print(f"学生答案: C")
        print(f"批改结果: {grading_result}")
        
        print("\n✅ 所有功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保 Ollama 服务已启动")
        print("2. 确保已安装 llama2:13b 模型")
        print("3. 运行命令检查: ollama list")
        print("4. 如果模型未安装，运行: ollama pull llama2:13b")
        return False

def test_ai_grading():
    """测试AI批改功能"""
    print("\n" + "=" * 50)
    print("测试完整AI批改流程")
    print("=" * 50)
    
    try:
        from app.services.grading_llama import grade_homework_with_ai
        
        # 模拟题目数据
        test_questions = [
            {
                'stem': '计算：15 + 27 = ?',
                'answer': '42',
                'type': '计算题',
                'question_id': 'test_q1'
            },
            {
                'stem': '地球绕太阳转一圈需要多长时间？',
                'answer': '一年',
                'type': '填空题', 
                'question_id': 'test_q2'
            },
            {
                'stem': '判断：太阳从东边升起。',
                'answer': '对',
                'type': '判断题',
                'question_id': 'test_q3'
            }
        ]
        
        print(f"测试题目数量: {len(test_questions)}")
        
        # 执行AI批改
        result = grade_homework_with_ai(test_questions, "测试OCR文本内容")
        
        print(f"批改结果: {len(result['grading_results'])} 道题")
        print(f"知识点分析: {result.get('knowledge_analysis', {}).get('wrong_knowledge_points', [])}")
        print(f"练习题生成: {len(result.get('practice_questions', []))} 道")
        
        print("\n✅ AI批改功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ AI批改测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试 Llama2 集成...")
    
    # 测试基本连接
    connection_ok = test_ollama_connection()
    
    if connection_ok:
        # 测试AI批改
        test_ai_grading()
    
    print("\n测试完成！")
