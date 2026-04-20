# 悦读小灯塔

> 基于游戏化交互与 AI 行为分析的儿童读写障碍智能筛查与家庭干预系统

版本：v1.0.0 · UniApp + FastAPI · 支持 H5 / 微信小程序 / iOS / Android

---

## 项目简介

面向家庭使用场景，通过游戏化互动采集儿童行为数据，结合 AI 分析生成能力画像与风险报告，帮助家长早发现、可理解、可干预、可追踪儿童读写能力问题。

**产品闭环：** 发现问题 → 理解问题 → 获得建议 → 开展训练 → 跟踪变化

**用户角色：**
- **家长端**：注册登录、创建儿童档案、发起筛查、查看报告、AI 问答、管理训练计划、跟踪成长变化
- **儿童端**：完成筛查游戏、完成训练任务、接收鼓励反馈、查看奖励成就

> ⚠️ 本产品不是医疗诊断工具，不替代医院、康复机构或持证教师的专业判断。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | UniApp (Vue 3) + Vite 5 |
| 后端框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| 数据验证 | Pydantic v2 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）|
| 认证 | JWT + bcrypt |
| AI 集成 | 兼容 OpenAI 格式（OpenAI / DeepSeek / 通义千问）|

---

## 快速启动

### 环境要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose（推荐）

### 方式一：Docker Compose（推荐）

```bash
# 1. 准备配置
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少修改 SECRET_KEY

# 2. 一键启动
bash deploy.sh dev
```

访问：前端 http://localhost · 后端 http://localhost:8000 · API 文档 http://localhost:8000/docs

### 方式二：手动启动

**后端**

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # 编辑 .env，修改 SECRET_KEY
python run.py
```

**前端**

```bash
cd frontend
npm install
npm run dev:h5
```

---

## 部署

### 生产环境（PostgreSQL + Nginx）

```bash
# 1. 准备生产配置
cp backend/.env.production backend/.env
# 编辑 backend/.env，填写 SECRET_KEY、ALLOWED_ORIGINS 等

# 2. 一键部署
bash deploy.sh prod
```

详细部署指南请参阅 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 环境变量说明

| 变量 | 说明 | 必填 |
|------|------|------|
| `SECRET_KEY` | JWT 密钥（生产必须修改）| ✅ |
| `DEBUG` | 调试模式（生产设为 False）| |
| `DATABASE_URL` | 数据库连接串 | |
| `ALLOWED_ORIGINS` | 前端域名（逗号分隔）| ✅ 生产必填 |
| `AI_API_KEY` | AI 服务密钥 | |
| `AI_API_BASE_URL` | AI 服务地址 | |
| `AI_MODEL` | 模型名称 | |
| `WX_APPID` / `WX_SECRET` | 微信小程序配置 | 小程序必填 |
| `SMS_*` | 短信服务配置 | |

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 核心功能

### 筛查游戏（6 种）

每种游戏分 3 个难度等级，根据儿童年级自动匹配：

| 游戏类型 | 评估维度 | 时限 |
|----------|----------|------|
| 视觉辨识 | 视觉辨识能力、持续注意力 | 6–10 秒/题 |
| 拼字识别 | 音形映射、字序组织 | 6–10 秒/题 |
| 文字理解 | 阅读理解、语义整合 | 6–10 秒/题 |
| 工作记忆 | 工作记忆容量、短时记忆 | 10–15 秒/题 |
| 快速命名 | 快速命名速度、音韵意识 | 5–8 秒/题 |
| 精细动作 | 精细动作控制、视动整合 | 8–12 秒/题 |

### 评分机制

```
效率分 = 正确率(60%) + 反应时效率(40%)
风险等级：低风险 ≥75 / 中风险 ≥60 / 高风险 <60
```

### AI 功能

- 普通对话 / 流式对话
- 报告解读 / 训练计划生成
- 成长趋势分析 / 每日学习贴士
- 自适应难度调整

> 不配置 `AI_API_KEY` 时，系统自动降级为规则型回复，所有功能仍可正常演示。

---

## 项目结构

```
.
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层（auth、children、screenings 等）
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── services/           # 业务逻辑
│   │   ├── games/              # 6 种筛查游戏题库
│   │   └── main.py             # 应用入口
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                   # UniApp 前端
│   └── src/
│       ├── pages/
│       │   ├── parent/         # 家长端页面
│       │   └── child/          # 儿童端页面
│       ├── api/                # API 封装
│       └── components/         # 公共组件
│
├── docker-compose.yml          # 开发环境 Docker 配置
├── docker-compose.prod.yml     # 生产环境 Docker 配置
└── deploy.sh                   # 一键部署脚本
```

---

## API 端点

| 前缀 | 功能 |
|------|------|
| `/api/auth` | 注册、登录、验证码、微信登录 |
| `/api/children` | 儿童档案 CRUD |
| `/api/screenings` | 筛查流程（题目、提交、历史）|
| `/api/reports` | 评估报告查询与维度分析 |
| `/api/training` | 训练任务、成长记录、奖励 |
| `/api/ai` | AI 问答（10 项功能）|
| `/api/notifications` | 通知管理 |
| `/api/upload` | 文件上传 |

完整 API 文档：开发模式下访问 http://localhost:8000/docs

---

## 功能完成度

| 模块 | 状态 |
|------|------|
| 用户认证（注册/登录/JWT/微信登录）| ✅ |
| 儿童档案管理 | ✅ |
| 6 种筛查游戏（含自适应难度）| ✅ |
| 评分算法与评估报告 | ✅ |
| AI 问答（10 项功能）| ✅ |
| 训练任务系统 | ✅ |
| 成长记录与趋势分析 | ✅ |
| 报告对比（复评）| ✅ |
| 通知中心 | ✅ |
| 文件上传（头像）| ✅ |
| 短信服务 | ⚠️ 需配置 |
| 报告导出（PDF）| ❌ 规划中 |

---

## 免责声明

本系统仅作为家庭初步风险筛查工具，筛查结果**不构成医学诊断**。如筛查结果显示中高风险，请及时咨询专业医疗机构或持证评估师进行正式评估。

---

## License

MIT
