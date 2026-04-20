# 悦读小灯塔 · 部署指南

> 完整的生产环境部署流程，涵盖 Docker、Nginx、HTTPS、数据库、短信、微信小程序等所有配置。

---

## 部署架构

```
用户设备（H5/小程序/App）
    ↓
Nginx（80/443）
    ├── 静态文件（前端 H5）
    ├── /api/* → FastAPI 后端（8000）
    └── /uploads/* → 静态文件服务
    ↓
PostgreSQL（5432）
```

---

## 一、快速部署（Docker Compose）

### 1.1 开发环境（本地测试）

```bash
# 1. 克隆代码
git clone <your-repo-url>
cd dyslexia-support-app

# 2. 准备后端配置
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少修改 SECRET_KEY

# 3. 一键启动（SQLite + 前后端分离）
bash deploy.sh dev

# 访问
# 前端：http://localhost
# 后端：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 1.2 生产环境（PostgreSQL + Nginx）

```bash
# 1. 准备生产配置
cp backend/.env.production backend/.env
# 编辑 backend/.env，填写所有必填项：
#   - SECRET_KEY（随机 64 位十六进制）
#   - ALLOWED_ORIGINS（前端域名）
#   - DATABASE_URL（自动从 docker-compose.prod.yml 注入）
#   - AI_API_KEY（可选）
#   - SMS_PROVIDER / SMS_ACCESS_KEY（可选）

# 2. 设置数据库密码
export DB_PASSWORD="your_secure_password"

# 3. 一键部署
bash deploy.sh prod

# 访问
# 前端：http://your-domain.com
# 后端：http://your-domain.com/api
```

---

## 二、手动部署（无 Docker）

### 2.1 后端部署

```bash
cd backend

# 1. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.production .env
# 编辑 .env，填写所有配置

# 4. 初始化数据库（PostgreSQL）
# 表结构会在首次启动时自动创建

# 5. 启动服务（生产模式）
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

**使用 systemd 管理服务**

```bash
sudo nano /etc/systemd/system/dyslexia-backend.service
```

```ini
[Unit]
Description=Dyslexia Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/dyslexia-app/backend
Environment="PATH=/opt/dyslexia-app/backend/venv/bin"
ExecStart=/opt/dyslexia-app/backend/venv/bin/gunicorn app.main:app \
  -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable dyslexia-backend
sudo systemctl start dyslexia-backend
sudo systemctl status dyslexia-backend
```

### 2.2 前端部署

```bash
cd frontend

# 1. 安装依赖
npm ci --legacy-peer-deps

# 2. 构建 H5
npm run build:h5

# 3. 部署到 Nginx
sudo cp -r dist/build/h5/* /var/www/dyslexia-app/
```

**Nginx 配置示例**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/dyslexia-app;
    index index.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_buffering off;  # SSE 流式响应
    }

    # 上传文件
    location /uploads/ {
        alias /opt/dyslexia-app/backend/uploads/;
        expires 30d;
    }
}
```

---

## 三、数据库配置

### 3.1 PostgreSQL（生产推荐）

```bash
# 1. 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. 创建数据库和用户
sudo -u postgres psql
```

```sql
CREATE DATABASE dyslexia;
CREATE USER dyslexia_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE dyslexia TO dyslexia_user;
\q
```

```bash
# 3. 更新 backend/.env
DATABASE_URL=postgresql://dyslexia_user:your_secure_password@localhost:5432/dyslexia
```

### 3.2 SQLite（开发/小规模）

默认配置，无需额外设置。数据库文件位于 `backend/dyslexia.db`。

**备份**

```bash
cp backend/dyslexia.db backend/dyslexia.db.backup.$(date +%Y%m%d)
```

---

## 四、HTTPS 配置

### 4.1 使用 Let's Encrypt 免费证书

```bash
# 1. 安装 certbot
sudo apt install certbot

# 2. 申请证书（需先停止 Nginx）
sudo systemctl stop nginx
sudo certbot certonly --standalone -d your-domain.com

# 3. 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*.pem

# 4. 取消 nginx/conf.d/app.conf 中 SSL 相关行的注释

# 5. 重启 Nginx
docker compose -f docker-compose.prod.yml restart nginx
# 或手动：sudo systemctl restart nginx
```

### 4.2 自动续期

```bash
# 添加 cron 任务（每月 1 号凌晨 2 点）
sudo crontab -e
```

```cron
0 2 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /opt/dyslexia-app/nginx/ssl/ && docker compose -f /opt/dyslexia-app/docker-compose.prod.yml restart nginx
```

---

## 五、短信服务配置

### 5.1 阿里云 SMS

```bash
# 1. 安装 SDK
pip install alibabacloud-dysmsapi20170525

# 2. 在阿里云控制台申请短信签名和模板
# 短信模板示例：您的验证码是${code}，5分钟内有效。

# 3. 配置 backend/.env
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY=your_access_key_id
SMS_SECRET_KEY=your_access_key_secret
SMS_SIGN_NAME=悦读小灯塔
SMS_TEMPLATE_CODE=SMS_xxxxxxxxx
```

### 5.2 腾讯云 SMS

```bash
# 1. 安装 SDK
pip install tencentcloud-sdk-python-sms

# 2. 在腾讯云控制台申请短信签名和模板

# 3. 配置 backend/.env
SMS_PROVIDER=tencent
SMS_ACCESS_KEY=your_secret_id
SMS_SECRET_KEY=your_secret_key
SMS_APP_ID=your_sms_app_id
SMS_SIGN_NAME=悦读小灯塔
SMS_TEMPLATE_CODE=your_template_id
```

---

## 六、微信小程序配置

### 6.1 申请小程序

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册小程序账号
3. 获取 AppID 和 AppSecret

### 6.2 配置后端

```bash
# backend/.env
WX_APPID=wx1234567890abcdef
WX_SECRET=your_wx_secret
```

### 6.3 配置前端

```javascript
// frontend/src/manifest.json
{
  "mp-weixin": {
    "appid": "wx1234567890abcdef",
    ...
  }
}
```

### 6.4 申请订阅消息模板

在微信公众平台 → 功能 → 订阅消息 中申请以下模板：

| 模板用途 | 关键词 |
|---------|--------|
| 训练提醒 | 任务名称、提醒时间、温馨提示 |
| 复评提醒 | 孩子姓名、训练天数、建议内容 |
| 报告生成 | 报告类型、生成时间、查看入口 |

获取模板 ID 后，在 `frontend/src/pages/parent/reminder/index.vue` 中替换占位符 `training_reminder_template_id`。

### 6.5 编译上传

使用 HBuilderX：

1. 导入 `frontend` 目录
2. 运行 → 运行到小程序模拟器 → 微信开发者工具
3. 在微信开发者工具中点击"上传"
4. 在微信公众平台提交审核

---

## 七、AI 服务配置

### 7.1 OpenAI

```bash
# backend/.env
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

### 7.2 DeepSeek（国内推荐）

```bash
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
AI_API_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

### 7.3 通义千问

```bash
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-turbo
```

### 7.4 无 AI Key（降级模式）

不配置 `AI_API_KEY` 时，系统自动使用规则型回复模板，所有 AI 功能仍可正常演示。

---

## 八、监控与日志

### 8.1 查看日志

```bash
# Docker 方式
docker compose logs -f backend
docker compose logs -f frontend

# systemd 方式
sudo journalctl -u dyslexia-backend -f
```

### 8.2 健康检查

```bash
# 后端
curl http://localhost:8000/health

# 前端
curl http://localhost/health
```

### 8.3 性能监控（可选）

推荐使用 Prometheus + Grafana 监控：

```bash
# 安装 prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator

# 在 backend/app/main.py 中添加
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

---

## 九、数据备份

### 9.1 SQLite 备份

```bash
# 手动备份
cp backend/dyslexia.db backend/backup/dyslexia.db.$(date +%Y%m%d_%H%M%S)

# 定时备份（cron）
0 2 * * * cp /opt/dyslexia-app/backend/dyslexia.db /opt/backups/dyslexia.db.$(date +\%Y\%m\%d)
```

### 9.2 PostgreSQL 备份

```bash
# 手动备份
docker compose exec postgres pg_dump -U dyslexia_user dyslexia > backup.sql

# 定时备份（cron）
0 2 * * * docker compose -f /opt/dyslexia-app/docker-compose.prod.yml exec -T postgres pg_dump -U dyslexia_user dyslexia | gzip > /opt/backups/dyslexia_$(date +\%Y\%m\%d).sql.gz
```

### 9.3 上传文件备份

```bash
# 同步到对象存储（如阿里云 OSS）
ossutil cp -r backend/uploads/ oss://your-bucket/uploads/ --update
```

---

## 十、常见问题

### 10.1 前端无法连接后端

**症状**：前端显示"网络错误"或"401 未授权"

**排查**：

```bash
# 1. 检查后端是否启动
curl http://localhost:8000/health

# 2. 检查 CORS 配置
# backend/.env 中 ALLOWED_ORIGINS 是否包含前端域名

# 3. 检查前端 API 地址
# frontend/src/api/index.js 中 BASE_URL 是否正确
```

### 10.2 数据库连接失败

**症状**：后端启动报错 `could not connect to server`

**排查**：

```bash
# 1. 检查 PostgreSQL 是否启动
docker compose ps postgres
# 或：sudo systemctl status postgresql

# 2. 检查 DATABASE_URL 格式
# postgresql://user:password@host:port/database

# 3. 检查防火墙
sudo ufw allow 5432/tcp
```

### 10.3 上传文件 404

**症状**：头像上传后显示不出来

**排查**：

```bash
# 1. 检查上传目录权限
ls -la backend/uploads/

# 2. 检查 Nginx 配置
# nginx/conf.d/app.conf 中 /uploads/ 路径是否正确

# 3. 检查 Docker 挂载
docker compose exec backend ls -la /app/uploads/
```

### 10.4 AI 功能不可用

**症状**：AI 问答返回"服务暂时不可用"

**排查**：

```bash
# 1. 检查 AI_API_KEY 是否配置
grep AI_API_KEY backend/.env

# 2. 测试 API 连通性
curl -H "Authorization: Bearer $AI_API_KEY" \
  https://api.openai.com/v1/models

# 3. 查看后端日志
docker compose logs backend | grep -i "ai\|openai"
```

**降级方案**：不配置 `AI_API_KEY` 时，系统自动使用规则型回复，不影响功能演示。

### 10.5 短信验证码收不到

**症状**：点击"发送验证码"后手机未收到

**排查**：

```bash
# 1. 检查 DEBUG 模式
# DEBUG=True 时验证码只打印到日志，不发送短信
docker compose logs backend | grep "验证码"

# 2. 检查 SMS 配置
grep SMS_ backend/.env

# 3. 测试短信服务商 API
# 阿里云：登录控制台查看发送记录
# 腾讯云：登录控制台查看发送记录
```

---

## 十一、性能优化

### 11.1 后端优化

```bash
# 1. 增加 worker 数量（CPU 核心数 × 2 + 1）
gunicorn app.main:app -w 8 -k uvicorn.workers.UvicornWorker

# 2. 启用 Redis 缓存（可选）
# 安装：pip install redis
# 配置：REDIS_URL=redis://localhost:6379/0

# 3. 数据库连接池
# backend/app/database.py 中调整 pool_size 和 max_overflow
```

### 11.2 前端优化

```bash
# 1. 启用 CDN 加速
# 将 dist/build/h5/ 上传到阿里云 OSS / 腾讯云 COS

# 2. 图片压缩
# 使用 TinyPNG / ImageOptim 压缩图片资源

# 3. 代码分割
# UniApp 已自动分包，无需额外配置
```

### 11.3 Nginx 优化

```nginx
# 启用 HTTP/2
listen 443 ssl http2;

# 启用 Brotli 压缩（需安装模块）
brotli on;
brotli_types text/plain text/css application/json application/javascript;

# 静态文件缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 十二、安全加固

### 12.1 必做项

- [x] 修改 `SECRET_KEY` 为随机 64 位十六进制
- [x] 设置 `DEBUG=False`
- [x] 配置 `ALLOWED_ORIGINS` 为前端域名
- [x] 使用 HTTPS（Let's Encrypt 免费证书）
- [x] 数据库密码强度 ≥ 16 位
- [x] 定期备份数据库和上传文件

### 12.2 推荐项

- [ ] 启用 Nginx 限流（`limit_req_zone`）
- [ ] 配置防火墙（只开放 80/443/22 端口）
- [ ] 使用 Fail2Ban 防止暴力破解
- [ ] 定期更新依赖包（`pip list --outdated`）
- [ ] 配置日志轮转（logrotate）

---

## 十三、扩展部署

### 13.1 微信小程序云托管

微信小程序可使用云托管服务，无需自建服务器：

1. 在微信公众平台开通云托管
2. 上传 `backend/Dockerfile`
3. 配置环境变量（通过云托管控制台）
4. 绑定域名并配置 HTTPS

### 13.2 阿里云 / 腾讯云部署

**使用云服务器（ECS / CVM）**

```bash
# 1. 购买服务器（2核4G起步）
# 2. 安装 Docker 和 Docker Compose
# 3. 克隆代码到 /opt/dyslexia-app
# 4. 按本文档"一、快速部署"章节操作
```

**使用容器服务（ACK / TKE）**

```bash
# 1. 推送镜像到容器镜像服务
docker tag dyslexia-backend:latest registry.cn-hangzhou.aliyuncs.com/your-namespace/dyslexia-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/dyslexia-backend:latest

# 2. 在 Kubernetes 中创建 Deployment 和 Service
kubectl apply -f k8s/
```

---

## 十四、部署检查清单

部署前请逐项确认：

**后端**
- [ ] `SECRET_KEY` 已修改为随机值
- [ ] `DEBUG=False`
- [ ] `ALLOWED_ORIGINS` 已配置前端域名
- [ ] 数据库连接正常（PostgreSQL 推荐）
- [ ] `uploads/` 目录权限正确（755）
- [ ] AI_API_KEY 已配置（可选）
- [ ] SMS 服务已配置（可选）

**前端**
- [ ] `npm run build:h5` 构建成功
- [ ] `dist/build/h5/` 目录存在
- [ ] API 地址指向生产后端
- [ ] 微信小程序 AppID 已配置（如需上线小程序）

**Nginx**
- [ ] 反向代理配置正确（`/api/` → 后端）
- [ ] 静态文件路径正确
- [ ] HTTPS 证书已配置（生产必须）
- [ ] 上传文件路径已挂载

**数据库**
- [ ] PostgreSQL 已创建数据库和用户
- [ ] 数据库密码强度足够
- [ ] 定时备份任务已配置

**安全**
- [ ] 防火墙已配置（只开放必要端口）
- [ ] SSH 密钥登录（禁用密码登录）
- [ ] 定期更新系统和依赖包

---

## 十五、快速命令参考

```bash
# ── 启动 ──────────────────────────────────────────────────────────────────
bash deploy.sh dev                          # 开发环境
bash deploy.sh prod                         # 生产环境
docker compose up -d --build                # 手动启动（开发）
docker compose -f docker-compose.prod.yml up -d --build  # 手动启动（生产）

# ── 日志 ──────────────────────────────────────────────────────────────────
docker compose logs -f backend              # 后端日志
docker compose logs -f frontend             # 前端日志
docker compose logs -f postgres             # 数据库日志

# ── 重启 ──────────────────────────────────────────────────────────────────
docker compose restart backend              # 重启后端
docker compose restart nginx                # 重启 Nginx

# ── 停止 ──────────────────────────────────────────────────────────────────
docker compose down                         # 停止所有服务
docker compose down -v                      # 停止并删除数据卷（危险！）

# ── 备份 ──────────────────────────────────────────────────────────────────
docker compose exec postgres pg_dump -U dyslexia_user dyslexia > backup.sql
docker compose exec backend tar czf /app/uploads.tar.gz /app/uploads

# ── 更新 ──────────────────────────────────────────────────────────────────
git pull origin main                        # 拉取最新代码
docker compose up -d --build                # 重新构建并启动
```

---

## 支持

如有部署问题，请查看：
- 项目 README.md
- IMPLEMENTATION_STATUS.md（功能完成度）
- 后端日志：`docker compose logs backend`
- 前端控制台：浏览器 F12 → Console

---

**祝部署顺利！🚀**
