@echo off
chcp 65001 > nul
echo ========================================
echo   小肖的自用工具 - 前端启动 (Windows)
echo ========================================

cd /d "%~dp0"

if not exist "node_modules" (
    echo 正在安装前端依赖...
    npm install
)

echo.
echo 启动前端开发服务器...
echo 访问地址: http://127.0.0.1:1111
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev

pause
