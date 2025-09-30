@echo off
echo =====================================
echo React Native (Expo) 前端启动脚本
echo =====================================
echo.
echo 🎯 当前项目: AI作业批改助手
echo 🌐 后端地址: http://192.168.116.198:5000
echo 📱 支持平台: Web + Android + iOS
echo.

echo 📦 检查依赖...
if not exist node_modules (
    echo 📥 安装依赖包...
    npm install
)

echo.
echo 🚀 启动Expo开发服务器...
echo.
echo 📱 访问方式:
echo   [w] 网页版 - 在浏览器中打开
echo   [a] Android模拟器 - 需要Android Studio
echo   [i] iOS模拟器 - 需要Xcode (仅Mac)
echo   扫码 - 使用Expo Go APP扫描二维码
echo.
echo 🎮 功能特性:
echo   ✅ 拍照和相册选择
echo   ✅ 图片编辑和裁剪  
echo   ✅ OCR文字识别
echo   ✅ AI智能批改
echo   ✅ 知识点分析
echo   ✅ 历史记录
echo.

npx expo start

echo.
echo 前端服务已停止。
pause
