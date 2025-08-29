@echo off
echo 启动作业批改系统服务...
echo.

echo 1. 启动LLaVA控制器服务...
cd /d C:\Users\48108\LLaVA
call venv\Scripts\activate
start "LLaVA Controller" cmd /k "python -m llava.serve.controller --host 0.0.0.0 --port 10000"
timeout /t 5

echo 2. 启动LLaVA模型工作器...
start "LLaVA Model Worker" cmd /k "python -m llava.serve.model_worker --host 0.0.0.0 --controller http://localhost:10000 --port 40000 --worker http://localhost:40000 --model-path ./checkpoints/llava-1.5-7b-hf"
timeout /t 10

echo 3. 启动LLaVA Gradio Web服务...
start "LLaVA Gradio" cmd /k "python -m llava.serve.gradio_web_server --host 0.0.0.0 --port 8000 --controller http://localhost:10000"
timeout /t 5

echo 4. 启动后端API服务...
cd /d C:\Users\48108\Desktop\projectone\llmhomework_Backend
start "Backend API" cmd /k "python test_server.py"
timeout /t 3

echo 5. 启动前端开发服务器...
cd /d C:\Users\48108\Desktop\projectone\llmhomework_Frontend
start "Frontend" cmd /k "npm start"
timeout /t 5

echo.
echo 所有服务启动完成！
echo.
echo 服务访问地址：
echo - LLaVA控制器: http://localhost:10000
echo - LLaVA Web界面: http://localhost:8000
echo - 后端API: http://localhost:5000
echo - 前端应用: http://localhost:3000
echo.
pause 