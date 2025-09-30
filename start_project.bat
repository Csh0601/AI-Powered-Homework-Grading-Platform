@echo off
chcp 65001 >nul
title AI作业批改系统 - 启动管理器

echo ========================================================
echo              AI作业批改系统 - 启动管理器
echo ========================================================
echo.

cd /d "%~dp0"
echo [INFO] 项目根目录: %cd%
echo.

echo [MENU] 请选择启动选项:
echo.
echo   1. 启动完整系统 (后端 + 前端)
echo   2. 仅启动后端服务
echo   3. 仅启动前端Flutter
echo   4. 运行系统测试
echo   5. 退出
echo.

set /p choice=[INPUT] 请输入选项 (1-5): 

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto exit
goto invalid_choice

:start_all
echo.
echo [FULL] 启动完整系统...
echo ========================================================
echo.
echo [STEP 1] 启动后端服务...
start "AI后端服务" /min cmd /c "cd /d %~dp0 && start_backends.bat"
timeout /t 10 >nul
echo.
echo [STEP 2] 启动前端Flutter...
start "Flutter前端" cmd /c "cd /d %~dp0\My Part && flutter run -d web-server --web-port 3000"
echo.
echo [SUCCESS] 系统启动完成！
echo [INFO] 前端地址: http://localhost:3000
echo [INFO] AI后端: http://127.0.0.1:5000
echo [INFO] OCR后端: http://127.0.0.1:8002
goto end

:start_backend
echo.
echo [BACKEND] 启动后端服务...
echo ========================================================
call start_backends.bat
goto end

:start_frontend
echo.
echo [FRONTEND] 启动Flutter前端...
echo ========================================================
cd /d "%~dp0\My Part"
echo [INFO] 切换到Flutter目录: %cd%
echo [START] 启动Flutter Web服务器...
flutter run -d web-server --web-port 3000
goto end

:run_tests
echo.
echo [TEST] 运行系统测试...
echo ========================================================
cd /d "%~dp0\llmhomework_Backend"
call install_and_test.bat
goto end

:invalid_choice
echo.
echo [ERROR] 无效选项，请重新选择...
timeout /t 2 >nul
cls
goto start

:exit
echo.
echo [BYE] 退出系统启动器
timeout /t 1 >nul
exit /b 0

:end
echo.
echo [DONE] 操作完成，按任意键返回主菜单...
pause >nul
cls
goto start

:start
goto :eof
