@echo off
echo 🧹 清理缓存并重启前端服务...
echo.

echo 📦 停止现有服务...
taskkill /f /im node.exe 2>nul

echo 🗑️ 清理Metro缓存...
npx expo start --clear

echo.
echo ✅ 前端服务已重启，缓存已清理
echo 📱 请在手机上重新加载应用
pause
