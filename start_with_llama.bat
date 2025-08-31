@echo off
echo 启动支持 Llama2 的作业批改系统
echo ================================

echo 1. 检查 Ollama 服务状态...
ollama list
if %errorlevel% neq 0 (
    echo 错误：Ollama 服务未启动，请先启动 Ollama
    pause
    exit /b 1
)

echo.
echo 2. 检查 llama2:13b 模型...
ollama list | findstr "llama2:13b" >nul
if %errorlevel% neq 0 (
    echo 警告：未找到 llama2:13b 模型，请运行：ollama pull llama2:13b
    pause
)

echo.
echo 3. 安装 Python 依赖...
cd llmhomework_Backend
pip install -r requirements.txt

echo.
echo 4. 测试 Llama2 连接...
C:\Users\48108\AppData\Local\Programs\Python\Python313\python.exe test_ollama.py

echo.
echo 5. 启动后端服务...
C:\Users\48108\AppData\Local\Programs\Python\Python313\python.exe run.py

pause
