@echo off
chcp 65001 >nul
echo 🚀 启动统一数据收集系统...
echo 📚 支持AI生成、网站爬虫、PDF处理等多种方式
echo ⚖️ 严格遵守网站使用条款和robots.txt
echo.

cd /d "%~dp0"

echo 🎯 可用收集方式:
echo   1. ai     - AI数据生成
echo   2. crawl  - 网站爬虫
echo   3. pdf    - PDF处理
echo   4. all    - 全部方式
echo   5. full   - 完整流程（收集+处理+导入）
echo   6. interactive - 交互模式
echo.

set /p choice="请选择收集方式 (1-6) 或直接按回车进入交互模式: "

if "%choice%"=="1" (
    echo 🤖 启动AI数据生成...
    python run_data_collection.py ai
) else if "%choice%"=="2" (
    echo 🌐 启动网站爬虫...
    python run_data_collection.py crawl
) else if "%choice%"=="3" (
    echo 📄 启动PDF处理...
    python run_data_collection.py pdf
) else if "%choice%"=="4" (
    echo 🔄 启动全部收集方式...
    python run_data_collection.py all
) else if "%choice%"=="5" (
    echo 🎯 启动完整流程...
    python run_data_collection.py full
) else if "%choice%"=="6" (
    echo 🎮 进入交互模式...
    python run_data_collection.py interactive
) else (
    echo 🎮 进入交互模式...
    python run_data_collection.py
)

echo.
echo ✅ 数据收集系统执行完成！
echo 📁 请检查 processed 目录下的文件
echo.
pause