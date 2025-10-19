@echo off
chcp 65001 >nul
echo ========================================
echo     ⚡ 快速提交更新到GitHub
echo ========================================
echo.

REM 使用默认提交信息（带时间戳）
set commit_msg=更新: 网络配置优化 - 自动IP检测 (%date% %time:~0,5%)

echo 📝 提交信息: %commit_msg%
echo.

echo 🔄 正在提交...
git add .
git commit -m "%commit_msg%"
git pull origin main --rebase
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ✅ 更新成功！
    echo 🔗 查看: https://github.com/Csh0601/AI-Powered-Homework-Grading-Platform
) else (
    echo.
    echo ❌ 更新失败，请检查错误信息
)

echo.
pause

