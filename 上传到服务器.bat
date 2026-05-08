@echo off
chcp 65001 >nul
title 上传到服务器 121.43.250.191

echo.
echo ╔══════════════════════════════════════════╗
echo ║   悦读灯塔 - 上传文件到新服务器          ║
echo ║   服务器：121.43.250.191                 ║
echo ╚══════════════════════════════════════════╝
echo.

set SERVER=root@121.43.250.191
set APP_DIR=/opt/dyslexia-app

echo [1/4] 在服务器上创建目录...
ssh %SERVER% "mkdir -p %APP_DIR%/backend/app %APP_DIR%/backend/migrations %APP_DIR%/frontend/dist/build"

echo.
echo [2/4] 上传配置文件...
scp docker-compose.prod.yml %SERVER%:%APP_DIR%/
scp nginx.conf %SERVER%:%APP_DIR%/
scp backend\.env.example %SERVER%:%APP_DIR%/backend/
scp backend\alembic.ini %SERVER%:%APP_DIR%/backend/
scp backend\requirements.txt %SERVER%:%APP_DIR%/backend/
scp backend\Dockerfile %SERVER%:%APP_DIR%/backend/
scp backend\run.py %SERVER%:%APP_DIR%/backend/
scp backend\seed_articles.py %SERVER%:%APP_DIR%/backend/

echo.
echo [3/4] 上传后端代码...
scp -r backend\app %SERVER%:%APP_DIR%/backend/
scp -r backend\migrations %SERVER%:%APP_DIR%/backend/

echo.
echo [4/4] 上传前端构建产物...
scp -r frontend\dist\build\h5 %SERVER%:%APP_DIR%/frontend/dist/build/

echo.
echo ✅ 上传完成！
echo.
echo 下一步：SSH 登录服务器执行部署命令
echo   ssh root@121.43.250.191
echo.
pause
