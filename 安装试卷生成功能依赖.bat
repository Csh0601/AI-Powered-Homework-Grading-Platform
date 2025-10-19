@echo off
chcp 65001 >nul
echo ========================================
echo 📦 安装试卷生成功能依赖
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo 📦 正在安装ReportLab（PDF生成库）...
echo 这可能需要几分钟时间，请耐心等待...
echo.

cd llmhomework_Backend
pip install reportlab

if errorlevel 1 (
    echo.
    echo ❌ 安装失败！尝试使用国内镜像...
    echo.
    pip install reportlab -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if errorlevel 1 (
        echo.
        echo ❌ 安装仍然失败，请尝试以下方法：
        echo 1. 检查网络连接
        echo 2. 升级pip: python -m pip install --upgrade pip
        echo 3. 手动安装: pip install reportlab
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo ✅ ReportLab安装成功！
echo ========================================
echo.

echo 🔍 验证安装...
python -c "import reportlab; print('✅ ReportLab版本:', reportlab.Version)"

if errorlevel 1 (
    echo ❌ 验证失败，请检查安装
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 安装完成！
echo ========================================
echo.
echo 现在可以启动后端服务了：
echo   cd llmhomework_Backend
echo   python run.py
echo.

pause

