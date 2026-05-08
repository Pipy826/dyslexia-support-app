@echo off
chcp 65001 >nul
title 悦读灯塔 - 开发环境

echo.
echo ╔══════════════════════════════════════╗
echo ║     悦读灯塔 - 一键启动开发环境      ║
echo ╚══════════════════════════════════════╝
echo.

:: ── 启动后端 ──────────────────────────────────────────────
echo [1/3] 启动后端服务...
start "悦读灯塔-后端" cmd /k "cd /d %~dp0backend && python run.py"
timeout /t 3 /nobreak >nul

:: ── 启动 ngrok（如果已安装）──────────────────────────────
where ngrok >nul 2>&1
if %errorlevel% == 0 (
    echo [2/3] 启动 ngrok 内网穿透...
    start "悦读灯塔-ngrok" cmd /k "ngrok http 5173"
    timeout /t 3 /nobreak >nul
    set TUNNEL=--tunnel
) else (
    echo [2/3] 未检测到 ngrok，跳过内网穿透（仅局域网可用）
    echo       安装 ngrok 后可让任何人访问：https://ngrok.com/download
    set TUNNEL=
)

:: ── 启动前端（带二维码）──────────────────────────────────
echo [3/3] 启动前端并生成二维码...
cd /d %~dp0frontend
node dev-qr.js %TUNNEL%
