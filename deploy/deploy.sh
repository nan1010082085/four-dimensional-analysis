#!/bin/bash
set -e

# 四维分析盯盘台 - 部署脚本
# 用法: bash deploy/deploy.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVER="ubuntu@pyflow.icu"
REMOTE_DIR="~/stock-analysis"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "=========================================="
echo "四维分析盯盘台 - 部署"
echo "=========================================="
echo "服务器: ${SERVER}"
echo "远程目录: ${REMOTE_DIR}"
echo ""

# 构建前端
echo "构建前端..."
cd "${ROOT_DIR}/frontend"
npm run build

# 创建临时打包目录
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="deploy-package"

mkdir -p "${TEMP_DIR}/${PACKAGE_NAME}"

# 复制文件
echo "打包文件..."
cp -r "${ROOT_DIR}/app.py" "${TEMP_DIR}/${PACKAGE_NAME}/"
cp -r "${ROOT_DIR}/ai" "${TEMP_DIR}/${PACKAGE_NAME}/"
cp -r "${ROOT_DIR}/datasources" "${TEMP_DIR}/${PACKAGE_NAME}/"
cp -r "${ROOT_DIR}/paper_trading.py" "${TEMP_DIR}/${PACKAGE_NAME}/"
cp -r "${ROOT_DIR}/requirements.txt" "${TEMP_DIR}/${PACKAGE_NAME}/"
cp -r "${ROOT_DIR}/frontend/dist" "${TEMP_DIR}/${PACKAGE_NAME}/frontend-dist"
cp -r "${ROOT_DIR}/.env.example" "${TEMP_DIR}/${PACKAGE_NAME}/"

# 打包
cd "${TEMP_DIR}"
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# 上传
echo "上传到服务器..."
rsync -avz -e ssh "${PACKAGE_NAME}.tar.gz" "${SERVER}:~/stock-analysis/"

# 远程部署
echo "远程部署..."
ssh "${SERVER}" bash -s << REMOTE
set -e
cd ~/stock-analysis
tar -xzf ${PACKAGE_NAME}.tar.gz
rm -f ${PACKAGE_NAME}.tar.gz
mv ${PACKAGE_NAME}/* .
rm -rf ${PACKAGE_NAME}
rm -f ._*

# 安装依赖
source venv/bin/activate
pip install -r requirements.txt -q

# 重启服务
pm2 restart stock-analysis

echo "部署完成"
REMOTE

# 清理
rm -rf "${TEMP_DIR}"

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo "访问地址: http://pyflow.icu/stock-analysis/"
echo ""
