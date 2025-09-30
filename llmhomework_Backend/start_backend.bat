@echo off
chcp 65001 >nul
echo [AI] 启动OCR作业批改后端服务...
echo [INFO] 使用Python 3.10版本
echo.

cd /d "%~dp0"

REM ✅ 确保禁用 Flash Attention / Triton，避免 wrap_triton 报错
SET PYTORCH_ENABLE_TRITON=0
SET TORCHINDUCTOR_DISABLE_TRITON=1
SET FLASH_ATTENTION_FORCE_DISABLED=1
SET ATTN_IMPLEMENTATION=eager

python run.py

echo.
echo [STOP] 服务已停止，按任意键退出...
pause
