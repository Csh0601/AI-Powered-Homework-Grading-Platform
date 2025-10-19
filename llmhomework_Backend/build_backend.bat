@echo off
chcp 65001
echo ========================================
echo AI学习伙伴后端打包工具
echo ========================================
echo.

echo 步骤1: 安装 PyInstaller...
pip install pyinstaller

echo.
echo 步骤2: 开始打包后端...
pyinstaller build_exe.spec --clean

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位置: dist\LLMHomework_Backend\LLMHomework_Backend.exe
echo ========================================
pause


