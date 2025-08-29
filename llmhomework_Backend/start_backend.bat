@echo off
echo 启动OCR作业批改后端服务...
echo 使用Python 3.13版本
echo.

cd /d "%~dp0"
"C:\Users\48108\AppData\Local\Programs\Python\Python313\python.exe" run.py

echo.
echo 服务已停止，按任意键退出...
pause
