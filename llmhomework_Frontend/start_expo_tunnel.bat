@echo off
echo 启动Expo开发服务器（隧道模式）...
echo 这将解决网络连接问题
echo.

cd /d "%~dp0"

echo 清理缓存...
npx expo start --clear

echo.
echo 启动隧道模式...
npx expo start --tunnel

echo.
echo 前端服务已停止，按任意键退出...
pause
