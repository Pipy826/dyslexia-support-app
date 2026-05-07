#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# 悦读小灯�?· 一键部署脚�?# 用法：bash deploy.sh [dev|prod]
# ─────────────────────────────────────────────────────────────────────────────
set -e

MODE=${1:-dev}
echo "🚀 部署模式: $MODE"

# ── 检查依�?──────────────────────────────────────────────────────────────────
check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "�?未找�?$1，请先安�?
    exit 1
  fi
}
check_cmd docker
check_cmd docker-compose 2>/dev/null || check_cmd "docker compose"

# ── 检�?.env 文件 ────────────────────────────────────────────────────────────
if [ ! -f backend/.env ]; then
  echo "⚠️  未找�?backend/.env，正在从模板创建..."
  if [ "$MODE" = "prod" ]; then
    cp backend/.env.production backend/.env
    echo "📝 请编�?backend/.env 填写生产配置后重新运�?
    exit 1
  else
    cp backend/.env.example backend/.env
    echo "�?已创建开发环�?.env"
  fi
fi

# ── 生产模式：构建前�?────────────────────────────────────────────────────────
if [ "$MODE" = "prod" ]; then
  echo "📦 构建前端..."
  cd frontend
  npm ci --legacy-peer-deps
  npm run build:h5
  cd ..
  echo "�?前端构建完成"
fi

# ── 启动服务 ──────────────────────────────────────────────────────────────────
if [ "$MODE" = "prod" ]; then
  COMPOSE_FILE="docker-compose.prod.yml"
else
  COMPOSE_FILE="docker-compose.yml"
fi

echo "🐳 启动 Docker 服务..."
docker compose -f "$COMPOSE_FILE" pull 2>/dev/null || true
docker compose -f "$COMPOSE_FILE" up -d --build

echo ""
echo "�?部署完成�?
if [ "$MODE" = "prod" ]; then
  echo "   前端：http://your-domain.com"
  echo "   后端：http://your-domain.com/api"
else
  echo "   前端：http://localhost"
  echo "   后端：http://localhost:8000"
  echo "   API 文档：http://localhost:8000/docs"
fi
echo ""
echo "📋 查看日志：docker compose -f $COMPOSE_FILE logs -f"
echo "🛑 停止服务：docker compose -f $COMPOSE_FILE down"
