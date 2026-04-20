# 儿童读写障碍智能筛查与干预系统（悦读小灯塔）

> 基于游戏化交互与 AI 行为分析的儿童读写障碍智能筛查与家庭干预 App
>
> 版本：v1.0.0 · UniApp + FastAPI · 支持 H5 / 微信小程序 / iOS / Android

---

## 项目简介

本产品面向家庭使用场景，通过游戏化互动采集儿童行为数据，结合 AI 分析生成能力画像与风险报告，帮助家长早发现、可理解、可干预、可追踪儿童读写能力问题。

**产品闭环：** 发现问题 → 理解问题 → 获得建议 → 开展训练 → 跟踪变化

**用户角色：**
- **家长端**：注册登录、创建儿童档案、发起筛查、查看报告、AI 问答、管理训练计划、跟踪成长变化
- **儿童端**：完成筛查游戏、完成训练任务、接收鼓励反馈、查看奖励成就

> ⚠️ 本产品不是医疗诊断工具，不替代医院、康复机构或持证教师的专业判断。

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | UniApp (Vue 3) | 3.0.0 |
| 构建工具 | Vite | 5.2.8 |
| 后端框架 | FastAPI + Uvicorn | 0.115.0 / 0.32.0 |
| ORM | SQLAlchemy | 2.0.36 |
| 数据验证 | Pydantic v2 | 2.9.2 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）| — |
| 认证 | JWT (python-jose) + bcrypt | — |
| AI 集成 | 兼容 OpenAI 格式（OpenAI / DeepSeek / 通义千问）| — |
| HTTP 客户端 | httpx | 0.27.2 |
| 样式 | Sass + Phosphor Icons | — |
| 跨平台 | H5 / 微信小程序 / App（iOS & Android）| — |

---

## 项目结构

```
.
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层
│   │   │   ├── auth.py         # 注册、登录、验证码、微信登录
│   │   │   ├── children.py     # 儿童档案 CRUD
│   │   │   ├── screenings.py   # 筛查流程（题目、提交、历史）
│   │   │   ├── reports.py      # 评估报告查询与维度分析
│   │   │   ├── training.py     # 训练任务、成长记录、奖励
│   │   │   ├── ai_qa.py        # AI 问答（LLM 或规则型降级）
│   │   │   ├── notifications.py# 通知管理
│   │   │   └── upload.py       # 头像上传
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   │   ├── user.py         # 用户（家长）
│   │   │   ├── child.py        # 儿童档案
│   │   │   ├── screening.py    # 筛查记录 + 维度得分 + 报告
│   │   │   ├── training.py     # 训练任务 + 成长记录
│   │   │   ├── reward.py       # 奖励
│   │   │   └── ai_chat.py      # AI 对话历史 + 收藏消息
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── ai_service.py   # AI 服务（含降级处理）
│   │   │   └── screening_service.py  # 评分算法
│   │   ├── games/              # 6 种筛查游戏题库
│   │   │   ├── visual_game.py          # 视觉辨识
│   │   │   ├── spelling_game.py        # 拼字识别
│   │   │   ├── comprehension_game.py   # 文字理解
│   │   │   ├── working_memory_game.py  # 工作记忆
│   │   │   ├── rapid_naming_game.py    # 快速命名
│   │   │   └── motor_coordination_game.py  # 精细动作
│   │   ├── utils/              # 工具函数（安全、加密）
│   │   ├── config.py           # 环境变量配置
│   │   ├── database.py         # 数据库连接
│   │   └── main.py             # FastAPI 应用入口
│   ├── tests/                  # 后端测试
│   ├── requirements.txt
│   ├── run.py
│   ├── Dockerfile
│   └── .env.example
│
└── frontend/                   # UniApp 前端
    └── src/
        ├── pages/
        │   ├── parent/         # 家长端页面
        │   │   ├── auth/       # 登录、注册、引导页、创建档案
        │   │   ├── home/       # 首页
        │   │   ├── screening/  # 能力筛查入口
        │   │   ├── report/     # 评估报告（列表 + 详情 + 对比）
        │   │   ├── training/   # 干预与训练管理
        │   │   ├── ai-chat/    # AI 问答
        │   │   ├── growth/     # 成长分析与趋势图
        │   │   ├── child-profile/      # 儿童档案详情
        │   │   ├── notifications/      # 通知中心
        │   │   ├── professional-guide/ # 专业机构引导
        │   │   ├── reminder/           # 复评提醒
        │   │   ├── profile/            # 个人主页
        │   │   ├── account/            # 账号设置
        │   │   ├── settings/           # 应用设置
        │   │   ├── help/               # 帮助中心
        │   │   ├── about/              # 关于我们
        │   │   └── legal/              # 隐私协议 / 用户协议
        │   └── child/          # 儿童端页面
        │       ├── home/       # 游戏选择首页
        │       ├── prep/       # 游戏前准备
        │       ├── game/       # 游戏主界面
        │       ├── reward/     # 完成奖励页
        │       ├── training/   # 训练任务列表
        │       ├── training-game/   # 训练游戏
        │       └── training-reward/ # 训练奖励
        ├── api/                # 前端 API 封装（含拦截器）
        ├── components/         # 公共组件（TabBar、图表等）
        └── utils/              # 工具函数
```

---

## 快速启动

### 环境要求

- Python 3.9+
- Node.js 18+
- npm 9+

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，至少修改 SECRET_KEY（见下方说明）

# 启动开发服务器（表结构自动创建）
python run.py
# 或：uvicorn app.main:app --reload --port 8000
```

API 交互文档（开发模式）：http://localhost:8000/docs

### 前端

```bash
cd frontend

# 安装依赖
npm install

# H5 开发模式（默认代理到 http://localhost:8000）
npm run dev:h5

# 构建 H5
npm run build:h5
```

前端默认通过 Vite 代理将 `/api` 请求转发到 `http://localhost:8000`，生产环境可在 `frontend/src/api/index.js` 中修改 `BASE_URL`，或通过环境变量 `VITE_API_BASE_URL` 指定。

> 微信小程序 / App 打包请使用 HBuilderX 导入 `frontend` 目录后编译。

---

## 部署

### 方式一：Docker Compose（推荐）

项目已内置完整的 Docker 部署配置，一条命令即可启动。

**开发环境（SQLite + 前后端分离）**

```bash
# 1. 准备配置
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少修改 SECRET_KEY

# 2. 一键启动
bash deploy.sh dev
# 或手动：docker compose up -d --build
```

访问：前端 http://localhost · 后端 http://localhost:8000 · API 文档 http://localhost:8000/docs

**生产环境（PostgreSQL + Nginx）**

```bash
# 1. 准备生产配置
cp backend/.env.production backend/.env
# 编辑 backend/.env，填写所有必填项（SECRET_KEY、ALLOWED_ORIGINS 等）

# 2. 构建前端并启动
bash deploy.sh prod
```

**常用命令**

```bash
# 查看日志
docker compose logs -f backend

# 重启单个服务
docker compose restart backend

# 停止所有服务
docker compose down

# 备份数据库（SQLite）
docker compose exec backend cp /app/data/dyslexia.db /app/uploads/backup.db
```

### 方式二：手动部署（无 Docker）

**后端**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 编辑 .env

# 开发
python run.py

# 生产（4 worker）
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**前端**

```bash
cd frontend
npm ci --legacy-peer-deps
npm run build:h5
# 将 dist/build/h5/ 目录部署到 Nginx / CDN
```

### 方式三：GitHub Actions 自动部署

项目已内置 `.github/workflows/deploy.yml`，推送到 `main` 分支时自动构建并部署到服务器。

需要在 GitHub 仓库 Settings → Secrets 中配置：

| Secret | 说明 |
|--------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码 |
| `SERVER_HOST` | 服务器 IP |
| `SERVER_USER` | SSH 用户名 |
| `SERVER_SSH_KEY` | SSH 私钥 |

### HTTPS 配置

将 SSL 证书文件放入 `nginx/ssl/` 目录，然后取消 `nginx/conf.d/app.conf` 中 SSL 相关行的注释：

```bash
# 使用 Let's Encrypt 免费证书（需安装 certbot）
certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

---

## 环境变量说明（backend/.env）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `True` | 生产环境改为 `False`，关闭 Swagger 文档并收紧 CORS |
| `DATABASE_URL` | `sqlite:///./dyslexia.db` | 数据库连接串 |
| `SECRET_KEY` | ⚠️ 默认值 | **生产必须修改** |
| `ALLOWED_ORIGINS` | 空 | 生产环境填前端域名，逗号分隔 |
| `AI_API_KEY` | 空 | 不填则使用规则型回复（无需 LLM）|
| `AI_API_BASE_URL` | OpenAI 官方 | 兼容 DeepSeek / 通义千问 |
| `AI_MODEL` | `gpt-4o-mini` | 模型名称 |
| `UPLOAD_DIR` | `uploads` | 文件上传目录 |
| `WX_APPID` | 空 | 微信小程序 AppID |
| `WX_SECRET` | 空 | 微信小程序 Secret |
| `SMS_PROVIDER` | 空 | 短信服务商：`aliyun` / `tencent` |
| `SMS_ACCESS_KEY` | 空 | 短信服务 AccessKey |
| `SMS_SECRET_KEY` | 空 | 短信服务 SecretKey |
| `SMS_SIGN_NAME` | `悦读小灯塔` | 短信签名 |
| `SMS_TEMPLATE_CODE` | 空 | 短信模板 Code |

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**支持的 AI 服务商配置示例：**

```dotenv
# OpenAI
AI_API_KEY=sk-xxxx
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini

# DeepSeek
AI_API_KEY=sk-xxxx
AI_API_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 通义千问
AI_API_KEY=sk-xxxx
AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-turbo
```

---

## 核心功能模块

### 筛查游戏（6 种）

每种游戏分 3 个难度等级（L1 学龄前/1-2 年级、L2 3-4 年级、L3 5-6 年级），每级 10 题，根据儿童年级自动匹配，并支持动态难度调整。

| 游戏类型 | 评估维度 | 可识别问题 | 时限 |
|----------|----------|------------|------|
| `visual` 视觉辨识 | 视觉辨识能力、持续注意力 | 形近字混淆、视觉扫描不完整 | 6–10 秒/题 |
| `spelling` 拼字识别 | 音形映射、字序组织、拼写输出 | 拼写困难、字序混乱、音形映射弱 | 6–10 秒/题 |
| `comprehension` 文字理解 | 阅读理解、语义整合、信息提取 | 阅读理解困难、语序处理弱 | 6–10 秒/题 |
| `working_memory` 工作记忆 | 工作记忆容量、短时记忆 | 记忆容量不足、序列信息遗忘 | 10–15 秒/题 |
| `rapid_naming` 快速命名 | 快速命名速度、音韵意识 | 命名速度偏慢、音韵意识薄弱 | 5–8 秒/题 |
| `motor_coordination` 精细动作 | 精细动作控制、视动整合 | 手部协调性不足、眼手配合弱 | 8–12 秒/题 |

**行为数据采集**（每题记录）：答案选择、花费时间、反应时间、修改次数、是否超时、是否正确。

### 评分机制

```
效率分 = 正确率(60%) + 反应时效率(40%)
注意力维度 = 基于反应时变异系数(CV)独立估算

风险等级：
  低风险  ≥ 75 分
  中风险  ≥ 60 分
  高风险  < 60 分
```

### AI 功能（10 项）

| 功能 | 接口 | 说明 |
|------|------|------|
| 普通对话 | `POST /api/ai/chat` | 家长自由问答 |
| 流式对话 | `POST /api/ai/chat/stream` | SSE 实时流式输出 |
| 报告解读 | `POST /api/ai/report-interpretation` | 个性化报告解读 |
| 训练计划 | `POST /api/ai/training-plan` | 生成定制训练方案 |
| 儿童鼓励 | `POST /api/ai/encouragement` | 游戏结束后鼓励话语 |
| 成长分析 | `GET /api/ai/growth-analysis/{child_id}` | 多次筛查趋势分析 |
| 每日贴士 | `GET /api/ai/daily-tip/{child_id}` | 个性化学习建议 |
| 情绪支持 | `POST /api/ai/emotional-support` | 高风险时家长情绪支持 |
| 自适应难度 | `POST /api/ai/adaptive-difficulty` | 动态调整游戏难度 |
| 对话历史 | `GET/DELETE /api/ai/history` | 查询/清空对话记录 |

> 不配置 `AI_API_KEY` 时，系统自动降级为规则型回复模板，所有 AI 功能仍可正常演示。

---

## 数据模型关系

```
User（家长）
├── Child（儿童档案）
│   ├── Screening（筛查记录）
│   │   ├── DimensionScore（维度得分）
│   │   └── Report（评估报告）
│   ├── TrainingTask（训练任务）
│   ├── GrowthRecord（成长记录）
│   └── Reward（奖励）
└── AIConversation（AI 对话）
    └── SavedMessage（收藏消息）
```

---

## API 端点总览

### 认证 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 注册（用户名/手机号）|
| POST | `/login` | 用户名/密码登录 |
| POST | `/login-by-code` | 手机验证码登录（自动注册）|
| POST | `/send-code` | 发送验证码 |
| GET | `/me` | 获取当前用户信息 |
| PUT | `/profile` | 修改用户名/手机号 |
| POST | `/change-password` | 修改密码 |
| POST | `/wx-login` | 微信小程序登录 |

### 儿童档案 `/api/children`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 获取儿童列表 |
| POST | `/` | 创建儿童档案 |
| GET | `/{id}` | 获取档案详情 |
| PUT | `/{id}` | 更新档案 |
| DELETE | `/{id}` | 删除档案 |

### 筛查 `/api/screenings`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/questions/{type}` | 获取题目（支持自适应难度）|
| POST | `/start` | 开始筛查 |
| POST | `/submit` | 提交答案并生成报告 |
| GET | `/history` | 历史记录 |

### 报告 `/api/reports`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 报告列表 |
| GET | `/{id}` | 报告详情 |
| GET | `/by-screening/{id}` | 按筛查查询报告 |
| GET | `/{id}/dimensions` | 维度详情 |
| GET | `/child/{id}/merged-dimensions` | 合并所有筛查维度（能力图谱）|

### 训练 `/api/training`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tasks` | 训练任务列表 |
| POST | `/tasks` | 创建任务 |
| PUT | `/tasks/{id}/progress` | 更新进度 |
| POST | `/tasks/{id}/complete` | 完成任务 |
| GET/POST | `/growth` | 成长记录 |
| GET | `/rewards` | 奖励列表 |
| GET | `/stars` | 星星总数 |

### AI 问答 `/api/ai`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/chat` | 普通对话 |
| POST | `/chat/stream` | 流式对话（SSE）|
| POST | `/report-interpretation` | 报告解读 |
| POST | `/training-plan` | 训练计划生成 |
| POST | `/encouragement` | 儿童鼓励话语 |
| GET | `/growth-analysis/{child_id}` | 成长趋势分析 |
| GET | `/daily-tip/{child_id}` | 每日学习贴士 |
| POST | `/emotional-support` | 情绪支持 |
| POST | `/adaptive-difficulty` | 自适应难度 |
| GET | `/history` | 对话历史 |
| DELETE | `/history` | 清空对话历史 |

### 通知 `/api/notifications`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 通知列表 |
| PUT | `/{id}/read` | 标记已读 |
| PUT | `/read-all` | 全部已读 |

### 文件上传 `/api/upload`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/avatar` | 上传头像（最大 5MB）|

---

## 开发说明

### 短信验证码

开发模式（`DEBUG=True`）下，验证码直接打印到后端日志，无需接入真实 SMS 服务。生产环境在 `.env` 中配置 `SMS_PROVIDER`（支持 `aliyun` / `tencent`）及对应密钥即可自动启用。

### 数据库迁移

开发环境使用 SQLite，表结构在应用启动时自动创建（`create_all`）。生产环境建议切换 PostgreSQL 并使用 Alembic 管理迁移：

```bash
# 切换数据库（backend/.env）
DATABASE_URL=postgresql://user:password@localhost:5432/dyslexia
```

### 跨平台部署

| 平台 | 方式 |
|------|------|
| H5 | `npm run build:h5` → 部署静态文件 |
| 微信小程序 | HBuilderX 编译 → 微信开发者工具上传 |
| App（iOS/Android）| HBuilderX 云打包 |

### 前端 API 地址配置

| 场景 | 配置方式 |
|------|---------|
| 本地开发（localhost）| Vite 代理自动转发，无需配置 |
| 局域网 IP 访问 | 自动检测非 localhost 主机，使用同主机 8000 端口 |
| 生产环境 | 设置环境变量 `VITE_API_BASE_URL=https://your-api.com` |

---

## 功能完成度

| 模块 | 状态 | 说明 |
|------|------|------|
| 用户认证 | ✅ 完成 | 注册/登录/验证码/JWT/微信登录 |
| 儿童档案管理 | ✅ 完成 | CRUD + 多孩子支持 + 扩展字段 |
| 6 种筛查游戏（后端题库）| ✅ 完成 | 含自适应难度 |
| 游戏前端交互 | ✅ 完成 | 选择题 + 行为数据采集 |
| 评分算法 | ✅ 完成 | 效率分 + 注意力维度 |
| 评估报告生成 | ✅ 完成 | 多维度 + 风险等级 |
| 综合能力图谱 | ✅ 完成 | 合并多次筛查维度 |
| AI 问答（10 项功能）| ✅ 完成 | 含降级处理 |
| 训练任务系统 | ✅ 完成 | 自动推荐 + 奖励 |
| 成长记录与趋势分析 | ✅ 完成 | 折线图 + AI 分析 |
| 高风险专业引导 | ✅ 完成 | 弹窗 + 情绪支持 |
| 首次登录引导页 | ✅ 完成 | 新手流程 + 隐私协议 |
| 阶段性复评提醒 | ✅ 完成 | 训练次数/天数触发 |
| 报告对比（复评）| ✅ 完成 | 与上次结果对比 |
| 通知中心 | ✅ 完成 | 系统通知 + 已读管理 |
| 文件上传（头像）| ✅ 完成 | 最大 5MB |
| 短信服务 | ⚠️ 开发模式 | 生产需配置 SMS_PROVIDER |
| 报告导出（PDF）| ❌ 规划中 | — |
| 推送通知 | ❌ 规划中 | — |

---

## 版本规划

| 阶段 | 目标 |
|------|------|
| **MVP（当前 v1.0）** | 完整筛查闭环：注册 → 筛查 → 报告 → 训练 → 成长跟踪 |
| **v2 干预增强** | 完善训练游戏内容、阶段复评、用户留存机制 |
| **v3 智能化升级** | 引入 ML 模型、优化推荐策略、专业支持对接 |

---

## 免责声明

本系统仅作为家庭初步风险筛查工具，筛查结果**不构成医学诊断**。如筛查结果显示中高风险，请及时咨询专业医疗机构、特殊教育机构或持证评估师进行正式评估。

---

## License

MIT
