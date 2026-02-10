@echo off
echo ========================================
echo 简历智能匹配系统启动脚本
echo Resume Intelligent Matching System
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo 正在检查依赖包...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
)

echo 正在启动系统...
echo 访问地址：http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.
python app.py

pause