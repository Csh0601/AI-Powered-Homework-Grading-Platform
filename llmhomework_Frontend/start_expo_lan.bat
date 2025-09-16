@echo off
echo 启动Expo开发服务器（LAN模式）...
echo 确保手机和电脑在同一WiFi网络
echo.

cd /d "%~dp0"

echo 清理缓存...
npx expo start --clear

echo.
echo 启动LAN模式...
npx expo start --lan

echo.
echo 前端服务已停止，按任意键退出...
pause
