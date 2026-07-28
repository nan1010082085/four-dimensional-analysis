#!/bin/bash

# 四维分析盯盘台 - 一键启动脚本

set -e

echo "🚀 启动四维分析盯盘台..."

# 检查并创建 Python 虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "📦 安装 Python 依赖..."
source venv/bin/activate
pip install -q flask flask-cors

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 启动后端
echo "🔧 启动后端服务 (端口 5080)..."
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
echo "🎨 启动前端服务 (端口 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 启动完成！"
echo ""
echo "📊 前端页面: http://localhost:3000"
echo "🔌 后端 API: http://localhost:5080"
echo ""
echo "按 Ctrl+C 停止服务"

# 捕获退出信号
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# 等待进程结束
wait
