@echo off
echo 启动Expo开发服务器（本地模式）...
echo 使用localhost连接
echo.

cd /d "%~dp0"

echo 清理缓存...
npx expo start --clear

echo.
echo 启动本地模式...
npx expo start --localhost

echo.
echo 前端服务已停止，按任意键退出...
pause
