#!/bin/bash

# 四维分析盯盘台 - 启动脚本

set -e

echo "🚀 启动四维分析盯盘台..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查并创建 Python 虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "📦 安装 Python 依赖..."
source venv/bin/activate
pip install -q flask flask-cors python-dotenv akshare tushare

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 检查前端是否已构建
if [ ! -d "frontend/dist" ]; then
    echo "🔨 构建前端..."
    cd frontend
    npm run build
    cd ..
fi

# 停止已有的服务
echo "🛑 停止已有服务..."
pkill -f "python app.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 1

# 启动后端
echo "🔧 启动后端服务 (端口 5080)..."
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端开发服务器（可选）
if [ "$1" = "--dev" ]; then
    echo "🎨 启动前端开发服务 (端口 5173)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ 启动完成！"
    echo ""
    echo "📊 前端页面: http://localhost:5173"
    echo "🔌 后端 API: http://localhost:5080"
else
    echo ""
    echo "✅ 启动完成！"
    echo ""
    echo "📊 访问地址: http://localhost:5080"
fi

echo ""
echo "数据源: ${DATA_SOURCE:-legacy}"
echo ""
echo "按 Ctrl+C 停止服务"

# 捕获退出信号
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# 等待进程结束
wait
