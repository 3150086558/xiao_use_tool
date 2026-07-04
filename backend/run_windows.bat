@echo off
chcp 65001 > nul
echo ========================================
echo   小肖的自用工具 - 后端启动 (Windows)
echo ========================================

cd /d "%~dp0"

if not exist ".venv" (
    echo 正在创建 Python 虚拟环境...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

echo.
echo 启动后端服务...
echo 访问地址: http://127.0.0.1:1112
echo API 文档: http://127.0.0.1:1112/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

uvicorn app.main:app --host 0.0.0.0 --port 1112 --reload

pause
