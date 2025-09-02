@echo off
echo 启动支持远程 Qwen3:30B 的作业批改系统
echo ==========================================

echo 1. 测试远程服务器连接...
echo 服务器地址: 172.31.179.77:11434
ping -n 1 172.31.179.77 >nul
if %errorlevel% neq 0 (
    echo 警告：无法ping通服务器，请检查网络连接
    echo 继续尝试连接...
)

echo.
echo 2. 测试远程qwen3:30B模型...

echo.
echo 3. 安装 Python 依赖...
cd llmhomework_Backend
pip install -r requirements.txt

echo.
echo 4. 测试远程 Qwen3:30B 连接...
C:\Users\48108\AppData\Local\Programs\Python\Python313\python.exe test_qwen.py
if %errorlevel% neq 0 (
    echo 警告：远程模型连接失败，请检查服务器状态
    echo 按任意键继续启动（将使用降级模式）...
    pause
)

echo.
echo 5. 启动后端服务...
C:\Users\48108\AppData\Local\Programs\Python\Python313\python.exe run.py

pause
