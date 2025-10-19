@echo off
chcp 65001 >nul
echo ========================================
echo     📤 上传项目到GitHub仓库
echo ========================================
echo.
echo 仓库地址: https://github.com/Csh0601/AI-Powered-Homework-Grading-Platform
echo.

REM 检查是否已初始化Git
if not exist ".git" (
    echo ⚠️  未检测到Git仓库，正在初始化...
    git init
    git remote add origin https://github.com/Csh0601/AI-Powered-Homework-Grading-Platform.git
    echo ✅ Git仓库初始化完成
    echo.
)

echo 📋 正在检查当前状态...
git status
echo.

echo ========================================
echo     📝 请输入提交信息
echo ========================================
echo.
echo 💡 提示：请输入本次更新的描述信息
echo 例如：更新网络配置，支持自动IP检测
echo.
set /p commit_msg="请输入提交信息: "

if "%commit_msg%"=="" (
    set commit_msg=更新项目代码
    echo 使用默认提交信息: %commit_msg%
)
echo.

echo ========================================
echo     🔄 开始上传流程
echo ========================================
echo.

echo [1/5] 添加所有文件到暂存区...
git add .
if %errorlevel% neq 0 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo ✅ 文件添加完成
echo.

echo [2/5] 提交更改...
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo ⚠️  没有新的更改需要提交，或提交失败
    echo.
    echo 💡 提示：
    echo - 如果没有更改，无需重复提交
    echo - 如果是首次提交，请确保有文件需要提交
    echo.
)
echo.

echo [3/5] 检查远程仓库连接...
git remote -v
echo.

echo [4/5] 拉取远程更新（如有冲突会提示）...
git pull origin main --allow-unrelated-histories
if %errorlevel% neq 0 (
    echo ⚠️  拉取失败，可能需要手动解决冲突
    echo.
    echo 💡 如果是首次推送，这是正常的，继续执行...
)
echo.

echo [5/5] 推送到GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 推送失败
    echo.
    echo 💡 可能的原因：
    echo 1. 网络连接问题
    echo 2. 需要配置GitHub认证
    echo 3. 分支名称不匹配
    echo.
    echo 📖 解决方法：
    echo - 确保已登录GitHub账号
    echo - 检查网络连接
    echo - 或手动运行: git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo     ✅ 上传成功！
echo ========================================
echo.
echo 🎉 项目已成功上传到GitHub
echo 🔗 查看仓库: https://github.com/Csh0601/AI-Powered-Homework-Grading-Platform
echo.
echo 📊 提交信息: %commit_msg%
echo ⏰ 提交时间: %date% %time%
echo.

pause

