#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证所有导入是否正确
"""

try:
    print("🔍 验证导入...")
    
    # 测试配置导入
    from app.config import Config
    print("✅ Config 导入成功")
    
    # 测试服务导入
    from app.services.qwen_service import QwenService
    print("✅ QwenService 导入成功")
    
    from app.services.grading_qwen import QwenGradingEngine, grade_homework_with_ai
    print("✅ QwenGradingEngine 导入成功")
    
    # 测试路由导入
    from app.routes.upload import upload_bp
    print("✅ upload_bp 导入成功")
    
    from app.routes.status import status_bp
    print("✅ status_bp 导入成功")
    
    # 测试应用创建
    from app import create_app
    app = create_app()
    print("✅ Flask 应用创建成功")
    
    print("\n🎉 所有导入验证成功！项目可以正常启动了。")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
