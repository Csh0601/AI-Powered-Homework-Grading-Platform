@echo off
chcp 65001 >nul
echo [START] 启动所有后端服务...
echo =====================================

cd /d "C:\Users\48108\Desktop\projectone"

echo [INFO] 当前目录: %cd%
echo.

echo [MANAGER] 运行全后端启动管理器...
python start_all_backends.py

echo.
echo [DONE] 后端服务管理器已退出
pause
