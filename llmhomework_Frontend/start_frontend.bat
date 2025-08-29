@echo off
echo 启动作业批改前端应用...
echo.

cd /d "%~dp0"
npm start

echo.
echo 前端服务已停止，按任意键退出...
pause
