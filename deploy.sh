#!/bin/bash
# ============================================================
# 悦读灯塔 - 服务器首次部署脚本
# 在服务器 64.83.16.195 上执行：
#   bash deploy.sh
# ============================================================
set -e

SERVER_IP="64.83.16.195"
APP_DIR="/opt/dyslexia-app"

echo "======================================"
echo "  悦读灯塔 - 服务器部署"
echo "  服务器：$SERVER_IP"
echo "======================================"

# ── 1. 安装 Docker ──────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    echo "▶ 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
fi
echo "✓ Docker: $(docker --version)"

# ── 2. 创建目录结构 ─────────────────────────────────────────
mkdir -p $APP_DIR/backend
mkdir -p $APP_DIR/frontend/dist/build/h5
cd $APP_DIR

# ── 3. 下载配置文件（如果没有）──────────────────────────────
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "▶ 请先上传项目文件到 $APP_DIR"
    echo "  在本地电脑执行："
    echo "  scp docker-compose.prod.yml nginx.conf root@$SERVER_IP:$APP_DIR/"
    echo "  scp -r backend/.env.example root@$SERVER_IP:$APP_DIR/backend/"
    exit 1
fi

# ── 4. 创建 .env 文件 ───────────────────────────────────────
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "▶ 创建后端配置文件..."
    cp backend/.env.example backend/.env

    # 自动生成随机 SECRET_KEY
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/CHANGE_ME_TO_A_RANDOM_SECRET_KEY/$SECRET/" backend/.env

    echo ""
    echo "⚠️  请设置数据库密码："
    read -p "   输入数据库密码（直接回车使用默认 Dyslexia2024）: " DB_PASS
    DB_PASS=${DB_PASS:-Dyslexia2024}

    sed -i "s/CHANGE_DB_PASSWORD/$DB_PASS/" backend/.env
    export DB_PASSWORD=$DB_PASS
    echo "DB_PASSWORD=$DB_PASS" >> /etc/environment
    echo "✓ 配置文件已生成"
else
    DB_PASSWORD=$(grep "^DATABASE_URL" backend/.env | sed 's/.*:\(.*\)@.*/\1/')
    export DB_PASSWORD
fi

# ── 5. 启动服务 ─────────────────────────────────────────────
echo ""
echo "▶ 启动所有服务..."
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

echo "⏳ 等待服务启动（30秒）..."
sleep 30

# ── 6. 数据库迁移 ───────────────────────────────────────────
echo "▶ 执行数据库迁移..."
docker exec dyslexia-backend alembic upgrade head || echo "⚠ 迁移失败，稍后手动执行"

# ── 7. 验证 ─────────────────────────────────────────────────
echo ""
if curl -sf "http://localhost:8000/health" | grep -q "healthy"; then
    echo "======================================"
    echo "  ✅ 部署成功！"
    echo ""
    echo "  🌐 访问地址：http://$SERVER_IP"
    echo "  📱 扫码地址：http://$SERVER_IP"
    echo "  � 后端健康：http://$SERVER_IP/health"
    echo "======================================"
else
    echo "❌ 后端未就绪，查看日志："
    docker logs dyslexia-backend --tail 30
fi
