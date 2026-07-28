# 四维分析盯盘台 - 部署文档

## 服务器信息

| 项目 | 值 |
|------|------|
| 服务器 | ubuntu@pyflow.icu |
| 域名 | pyflow.icu |
| 项目路径 | ~/stock-analysis/ |
| 访问地址 | http://pyflow.icu/stock-analysis/ |
| 后端端口 | 5080 |
| 进程管理 | PM2 (stock-analysis) |

## 目录结构

```
~/
├── schema-platform/           # 其他项目
├── stock-analysis/            # 本项目（与schema-platform同级）
│   ├── app.py                 # Flask后端
│   ├── ai/                    # AI分析模块
│   │   └── __init__.py        # DeepSeek AI分析器
│   ├── datasources/           # 数据源抽象层
│   │   ├── __init__.py        # DataSource基类
│   │   ├── akshare_source.py  # AkShare数据源
│   │   └── tushare_source.py  # Tushare数据源
│   ├── paper_trading.py       # 模拟盘交易系统
│   ├── frontend-dist/         # 前端构建产物
│   │   ├── index.html
│   │   └── assets/
│   ├── venv/                  # Python虚拟环境
│   ├── .env                   # 环境变量
│   ├── ecosystem.config.cjs   # PM2配置
│   └── logs/                  # 日志目录
```

## Nginx配置

配置文件：`/etc/nginx/sites-available/schema-platform`

```nginx
# ==================== 四维分析盯盘台 ====================
# 前端静态文件
location /stock-analysis/ {
    alias /home/ubuntu/stock-analysis/frontend-dist/;
    try_files $uri $uri/ /stock-analysis/index.html;
}

# 后端API代理
location /stock-analysis/api/ {
    rewrite ^/stock-analysis/(.*) /$1 break;
    proxy_pass http://127.0.0.1:5080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection '';
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

## 常用命令

```bash
# 查看PM2状态
pm2 status

# 查看日志
pm2 logs stock-analysis

# 重启服务
pm2 restart stock-analysis

# 测试nginx配置
sudo nginx -t

# 重载nginx
sudo systemctl reload nginx
```

## 部署流程

```bash
# 本地执行
bash deploy/deploy.sh
```

## 环境变量

```bash
# .env 文件
DATA_SOURCE=legacy          # 数据源：legacy/tushare/akshare
DEEPSEEK_MODEL=deepseek-chat # AI模型
# DEEPSEEK_API_KEY=         # DeepSeek API密钥（可选）
# TUSHARE_TOKEN=            # Tushare Token（可选）
```

## 访问方式

| 路径 | 说明 |
|------|------|
| http://pyflow.icu/stock-analysis/ | 前端页面 |
| http://pyflow.icu/stock-analysis/api/config | 配置接口 |
| http://pyflow.icu/stock-analysis/api/quote?code=sh600519 | 行情接口 |
| http://pyflow.icu/stock-analysis/api/analysis?code=sh600519 | 分析接口 |
