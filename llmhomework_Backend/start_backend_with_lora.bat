@echo off
chcp 65001 >nul
echo 🚀 一键启动后端服务（包含LoRA服务）
echo ================================================

cd /d "%~dp0"

echo 📍 当前目录: %CD%
echo 🔧 启动后端服务（自动启动LoRA服务）...

python start_backend_with_lora.py

echo.
echo ================================================
echo 🛑 后端服务已停止
echo ================================================
pause
