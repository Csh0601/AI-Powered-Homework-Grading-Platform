@echo off
chcp 65001 >nul
echo 🚀 启动LoRA服务...
echo ================================================

cd /d "%~dp0"

echo 📍 当前目录: %CD%
echo 🔧 启动LoRA服务脚本...

python start_lora_service.py

echo.
echo ================================================
echo 💡 如果LoRA服务启动成功，现在可以启动后端服务:
echo    python run.py
echo ================================================
pause
