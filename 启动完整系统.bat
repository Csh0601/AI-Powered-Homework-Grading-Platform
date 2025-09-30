@echo off
echo =====================================
echo    AI作业批改系统 - 完整启动脚本
echo =====================================
echo.
echo 🎯 系统架构：
echo   前端: React Native (Expo) - llmhomework_Frontend
echo   后端: Flask + AI大模型 - llmhomework_Backend  
echo   OCR: 腾讯云OCR (优先) + PaddleOCR (备用)
echo   AI: Qwen3-30B大模型 + 知识点分析
echo.

set FRONTEND_DIR=C:\Users\48108\Desktop\projectone\llmhomework_Frontend
set BACKEND_DIR=C:\Users\48108\Desktop\projectone\llmhomework_Backend

echo =====================================
echo 第一步：启动后端服务
echo =====================================
echo.
echo 📍 切换到后端目录...
cd /d "%BACKEND_DIR%"

echo 🚀 启动Flask后端服务...
echo   地址: http://192.168.116.198:5000
echo   功能: OCR识别 + AI批改 + 知识点分析
echo.
start "后端服务" cmd /k "python run.py"

echo ⏳ 等待后端服务启动完成...
timeout /t 10

echo.
echo =====================================
echo 第二步：启动前端应用
echo =====================================
echo.
echo 📍 切换到前端目录...
cd /d "%FRONTEND_DIR%"

echo 📱 启动Expo前端应用...
echo   支持: 网页版 + 手机版 + 拍照功能
echo   网络: 已配置连接到 192.168.116.198:5000
echo.
start "前端应用" cmd /k "npx expo start"

echo.
echo =====================================
echo 🎉 系统启动完成！
echo =====================================
echo.
echo 📱 前端访问方式:
echo   1. 网页版: 在Expo界面按 'w' 键
echo   2. 手机版: 扫描二维码 (需要Expo Go APP)
echo   3. 模拟器: 在Expo界面按 'a' 键 (Android)
echo.
echo 🔧 后端服务:
echo   - 主地址: http://192.168.116.198:5000
echo   - 健康检查: http://192.168.116.198:5000/
echo   - API文档: http://192.168.116.198:5000/docs (如果支持)
echo.
echo 🤖 AI功能:
echo   - 腾讯云OCR: ✅ 已配置
echo   - Qwen3大模型: ✅ 已集成
echo   - 知识点分析: ✅ 可用
echo   - 错题练习: ✅ 支持
echo.
echo 💡 使用提示:
echo   1. 确保手机和电脑在同一WiFi网络
echo   2. 前端支持拍照和相册选择
echo   3. 支持图片编辑和裁剪
echo   4. 具备完整的批改和分析功能
echo.
echo 按任意键继续...
pause > nul
