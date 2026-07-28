#!/bin/bash
set -e

# 四维分析盯盘台 - 部署脚本
# 用法: bash deploy/deploy.sh [服务器地址]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVER="${1:-${DEPLOY_SERVER:-ubuntu@pyflow.icu}}"
REMOTE_DIR="${DEPLOY_REMOTE_DIR:-~/four-dimensional-analysis}"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "=========================================="
echo "四维分析盯盘台 - 部署"
echo "=========================================="
echo "服务器: ${SERVER}"
echo "远程目录: ${REMOTE_DIR}"
echo "版本: ${VERSION}"
echo ""

# 检查SSH连接
echo "检查SSH连接..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SERVER}" "echo ok" || { echo "SSH连接失败"; exit 1; }

# 打包前端
echo "构建前端..."
cd "${ROOT_DIR}/frontend"
npm run build

# 创建临时打包目录
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="four-dimensional-analysis-${VERSION}"

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

# 创建远程部署脚本
cat > "${TEMP_DIR}/${PACKAGE_NAME}/setup.sh" << 'SETUP'
#!/bin/bash
set -e

echo "安装Python依赖..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "创建.env文件..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 .env 文件配置API密钥"
fi

echo "部署完成！"
echo "启动命令: source venv/bin/activate && python app.py"
SETUP

chmod +x "${TEMP_DIR}/${PACKAGE_NAME}/setup.sh"

# 打包
cd "${TEMP_DIR}"
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# 上传
echo "上传到服务器..."
scp "${PACKAGE_NAME}.tar.gz" "${SERVER}:~/"

# 远程部署
echo "远程部署..."
ssh "${SERVER}" bash -s << REMOTE
set -e

# 创建目录
mkdir -p "${REMOTE_DIR}"

# 解压
cd ~
tar -xzf "${PACKAGE_NAME}.tar.gz"
rm -f "${PACKAGE_NAME}.tar.gz"

# 复制文件到目标目录
cp -a "${PACKAGE_NAME}/." "${REMOTE_DIR}/"
rm -rf "${PACKAGE_NAME}"

# 进入目录
cd "${REMOTE_DIR}"

# 安装依赖
echo "安装Python依赖..."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt -q

# 创建.env（如果不存在）
if [ ! -f .env ]; then
    cp .env.example .env
fi

echo "部署完成！"
echo "目录: ${REMOTE_DIR}"
REMOTE

# 清理
rm -rf "${TEMP_DIR}"

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "SSH登录服务器后执行："
echo "  cd ${REMOTE_DIR}"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "或者使用nohup后台运行："
echo "  cd ${REMOTE_DIR}"
echo "  source venv/bin/activate"
echo "  nohup python app.py > app.log 2>&1 &"
echo ""
