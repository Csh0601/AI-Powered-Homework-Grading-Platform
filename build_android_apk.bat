@echo off
chcp 65001 >nul
echo ================================
echo   AI学习伙伴 Android APK打包
echo ================================
echo.

cd llmhomework_Frontend

echo [检查] 验证EAS CLI安装状态...
call eas whoami >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到EAS CLI或未登录
    echo.
    echo 请按照以下步骤操作:
    echo 1. 安装EAS CLI: npm install -g eas-cli
    echo 2. 登录账号: eas login
    echo.
    pause
    exit /b 1
)

echo [成功] EAS CLI已就绪
echo.
echo [提示] 打包配置选项:
echo   1. preview  - 生成APK文件(推荐,可直接安装)
echo   2. production - 生成AAB文件(用于上架应用商店)
echo.
set /p choice="请选择配置 (1/2,默认1): "

if "%choice%"=="2" (
    set profile=production
    echo [选择] 使用 production 配置
) else (
    set profile=preview
    echo [选择] 使用 preview 配置
)

echo.
echo [开始] 构建Android应用...
echo [提示] 首次构建可能需要10-30分钟,请耐心等待
echo [提示] 构建过程在Expo云端进行,可以关闭窗口
echo.

call eas build --platform android --profile %profile%

echo.
echo ================================
echo   构建完成!
echo ================================
echo.
echo 下一步操作:
echo 1. 点击上方提供的下载链接获取APK/AAB文件
echo 2. 或访问 https://expo.dev/ 查看所有构建
echo 3. 将APK传输到Android手机并安装
echo.
pause


