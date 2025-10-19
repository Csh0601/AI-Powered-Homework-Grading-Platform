@echo off
chcp 65001 >nul
echo ========================================
echo     🌐 获取当前电脑IP地址工具
echo ========================================
echo.
echo 正在检测网络配置...
echo.

REM 获取所有IPv4地址
echo 📋 当前电脑的所有IPv4地址：
echo ----------------------------------------
ipconfig | findstr /R /C:"IPv4"
echo ----------------------------------------
echo.

REM 提取校园网IP（172.x.x.x段）
echo 🏫 检测校园网IP（172网段）：
ipconfig | findstr /R /C:"IPv4" | findstr /R /C:"172\."
if %errorlevel% equ 0 (
    echo ✅ 检测到校园网IP
) else (
    echo ⚠️  未检测到校园网IP
)
echo.

REM 提取WiFi IP（192.168.x.x段）
echo 📱 检测WiFi/路由器IP（192.168网段）：
ipconfig | findstr /R /C:"IPv4" | findstr /R /C:"192\.168\."
if %errorlevel% equ 0 (
    echo ✅ 检测到WiFi/路由器IP
) else (
    echo ⚠️  未检测到WiFi/路由器IP
)
echo.

echo ========================================
echo     📝 使用说明
echo ========================================
echo.
echo 1. 查看上方显示的IP地址
echo 2. 系统会自动尝试所有显示的IP地址
echo 3. 无需手动修改配置文件
echo.
echo 💡 如果需要手动指定IP：
echo    - 编辑 llmhomework_Frontend/app/config/api.ts
echo    - 找到 NETWORK_CONFIG.MANUAL_IP
echo    - 设置为: 'http://你的IP:5000'
echo.
echo ⚠️  注意事项：
echo    - 确保后端服务已启动（运行 start_backends.bat）
echo    - 防火墙允许端口5000访问
echo    - 手机和电脑在同一网络环境
echo.
echo ========================================
echo.

REM 检查后端是否运行
echo 🔍 检查后端服务状态...
netstat -ano | findstr ":5000" >nul
if %errorlevel% equ 0 (
    echo ✅ 后端服务正在运行（端口5000已监听）
) else (
    echo ❌ 后端服务未运行
    echo 💡 请运行 start_backends.bat 启动后端服务
)
echo.

echo ========================================
echo.
pause

