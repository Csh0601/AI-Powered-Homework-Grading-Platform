"""
测试对话API是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """测试模块导入"""
    print("=" * 60)
    print("测试对话API模块导入...")
    print("=" * 60)
    
    try:
        from app import create_app
        print("✅ 成功导入create_app")
        
        from app.services.context_manager import get_context_manager
        print("✅ 成功导入context_manager")
        
        from app.services.chat_service import get_chat_service
        print("✅ 成功导入chat_service")
        
        from app.api.chat_endpoints import chat_bp
        print("✅ 成功导入chat_endpoints")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_app_creation():
    """测试应用创建"""
    print("\n" + "=" * 60)
    print("测试Flask应用创建...")
    print("=" * 60)
    
    try:
        from app import create_app
        app = create_app()
        print(f"✅ Flask应用创建成功")
        
        # 检查蓝图是否注册
        blueprints = list(app.blueprints.keys())
        print(f"\n📋 已注册的蓝图: {blueprints}")
        
        if 'chat' in blueprints:
            print("✅ 对话蓝图已成功注册")
        else:
            print("❌ 对话蓝图未注册")
            return False
            
        # 检查路由
        chat_routes = [str(rule) for rule in app.url_map.iter_rules() if 'chat' in str(rule)]
        print(f"\n🛣️  对话相关路由:")
        for route in chat_routes:
            print(f"  - {route}")
            
        return True
    except Exception as e:
        print(f"❌ 应用创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_context_manager():
    """测试上下文管理器"""
    print("\n" + "=" * 60)
    print("测试上下文管理器...")
    print("=" * 60)
    
    try:
        from app.services.context_manager import get_context_manager
        
        cm = get_context_manager()
        print("✅ 上下文管理器实例化成功")
        
        # 测试保存批改上下文
        test_grading_result = {
            'summary': {
                'total_questions': 5,
                'correct_count': 3,
                'accuracy_rate': 0.6
            },
            'grading_result': []
        }
        
        cm.save_grading_context('test_task_123', test_grading_result)
        print("✅ 保存批改上下文成功")
        
        # 测试创建对话
        conv_id = cm.create_conversation('test_task_123')
        print(f"✅ 创建对话成功: {conv_id}")
        
        # 测试添加消息
        cm.add_message(conv_id, 'user', '测试消息')
        print("✅ 添加消息成功")
        
        # 测试获取完整上下文
        context = cm.get_full_context(conv_id)
        print(f"✅ 获取完整上下文成功，消息数: {len(context['messages'])}")
        
        # 获取统计信息
        stats = cm.get_statistics()
        print(f"\n📊 统计信息: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ 上下文管理器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🧪 开始测试对话API功能")
    print("=" * 60)
    
    results = []
    
    # 测试1: 模块导入
    results.append(("模块导入", test_import()))
    
    # 测试2: 应用创建
    results.append(("应用创建", test_app_creation()))
    
    # 测试3: 上下文管理器
    results.append(("上下文管理器", test_context_manager()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print("\n" + "=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！对话API已准备就绪")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
