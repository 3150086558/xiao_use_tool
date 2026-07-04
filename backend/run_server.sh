#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

echo ""
echo "启动后端服务..."
echo "访问地址: http://127.0.0.1:1112"
echo "API 文档: http://127.0.0.1:1112/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 1112 --reload
