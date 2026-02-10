#!/bin/bash
# 简历智能匹配系统启动脚本

echo "========================================"
echo "简历智能匹配系统启动脚本"
echo "Resume Intelligent Matching System"
echo "========================================"
echo

echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3环境，请先安装Python 3.7或更高版本"
    exit 1
fi

echo "正在检查依赖包..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误：依赖包安装失败"
        exit 1
    fi
fi

echo "正在启动系统..."
echo "访问地址：http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo
python3 app.py