@echo off
chcp 65001 >nul
echo ==========================================
echo           项目修复和测试脚本
echo ==========================================
echo.

cd /d "%~dp0"
echo [INFO] 当前目录: %cd%

echo.
echo [STEP 1] 安装/更新依赖库...
echo.
python -m pip install --upgrade scikit-learn
python -m pip install tencentcloud-sdk-python
python -m pip install requests

echo.
echo [STEP 2] 测试服务器连接...
echo.
python test_server_connection.py

echo.
echo [STEP 3] 运行完整系统测试...
echo.
python test_complete_system.py

echo.
echo [DONE] 修复和测试完成！
echo.
echo 下一步：
echo 1. 检查上面的测试结果
echo 2. 如果一切正常，运行: start_backends.bat
echo 3. 然后启动Flutter前端
echo.
pause
