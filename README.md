# 悦读小灯塔

> 基于游戏化交互与 AI 行为分析的儿童读写障碍智能筛查与家庭干预系统

版本：v1.0.0 · UniApp (Vue 3) + FastAPI · 支持 H5 / 微信小程序 / iOS / Android

---

## 项目简介

面向家庭使用场景，通过 9 种游戏化互动采集儿童行为数据，结合 AI 分析生成能力画像与风险报告，帮助家长早发现、可理解、可干预、可追踪儿童读写能力问题。

**产品闭环：** 发现问题 → 理解问题 → 获得建议 → 开展训练 → 跟踪变化

**用户角色：**
- **家长端**：注册登录、创建儿童档案、发起筛查、查看报告、AI 问答、管理训练计划、跟踪成长变化、报告对比复评
- **儿童端**：完成筛查游戏、完成训练任务、连续打卡、查看奖励徽章
- **游客端**：免注册体验游戏

> ⚠️ 本产品不是医疗诊断工具，不替代医院、康复机构或持证教师的专业判断。

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | UniApp + Vue 3 | Vue 3.4.21 |
| 构建工具 | Vite | 5.2.8 |
| 状态管理 | Pinia | 2.1.7 |
| 跨端支持 | @dcloudio/uni-mp-weixin | 3.0.0 |
| 后端框架 | FastAPI + Uvicorn | 0.115.0 |
| ORM | SQLAlchemy | 2.0.36 |
| 数据验证 | Pydantic v2 | 2.9.2 |
| 认证 | JWT (python-jose) + bcrypt | 3.3.0 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）| — |
| AI 集成 | 兼容 OpenAI 格式（OpenAI / DeepSeek / 通义千问 / NVIDIA）| — |
| 定时任务 | APScheduler | 3.10.4 |
| 数据库迁移 | Alembic | 1.13.3 |

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

# 2. 一键启动（开发模式）
bash deploy.sh dev
```

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost |
| 后端 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

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
npm run dev:h5                  # H5 开发模式，访问 http://localhost:5173
```

微信小程序：使用 HBuilderX 打开 `frontend` 目录 → 发行 → 微信小程序

---

## 部署

### 生产环境

```bash
# 1. 准备生产配置
cp backend/.env.production backend/.env
# 编辑 backend/.env，填写 SECRET_KEY、DATABASE_URL、ALLOWED_ORIGINS

# 2. 一键部署（自动构建前端 + 启动 Docker）
bash deploy.sh prod
```

脚本会自动执行：前端 `npm run build:h5` → Docker 镜像构建 → Nginx + 后端容器启动

iOS / Android 打包请参阅 [云打包教程.md](./云打包教程.md)

详细部署配置请参阅 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SECRET_KEY` | 开发默认值 | JWT 密钥，**生产必须修改** |
| `DEBUG` | `True` | 生产设为 `False`，关闭 Swagger 并收紧 CORS |
| `DATABASE_URL` | `sqlite:///./dyslexia.db` | 数据库连接串 |
| `ALLOWED_ORIGINS` | 空 | 前端域名，逗号分隔，生产必填 |
| `AI_API_KEY` | 空 | AI 服务密钥，不填则降级为规则型回复 |
| `AI_API_BASE_URL` | OpenAI 官方地址 | 支持 DeepSeek / 通义千问 / NVIDIA，根据 key 前缀自动识别 |
| `AI_MODEL` | `gpt-4o-mini` | 模型名称 |
| `WX_APPID` / `WX_SECRET` | 空 | 微信小程序配置，小程序登录必填 |
| `UPLOAD_DIR` | `uploads` | 文件上传目录 |
| `SMS_PROVIDER` | 空 | 短信服务商（`aliyun` / `tencent`） |
| `CONTACT_PHONE` | `0755-33941800` | AI 跳转专业咨询时显示的联系方式 |

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> AI 自动识别规则：`sk-` 开头 → OpenAI，`ds-` 开头 → DeepSeek，`nvapi-` 开头 → NVIDIA NIM，其他 → 默认 OpenAI 兼容格式

---

## 核心功能

### 筛查游戏（9 种）

每种游戏分 L1 / L2 / L3 三个难度等级，根据儿童年级自动匹配：

| 游戏 | 评估维度 |
|------|----------|
| 视觉辨识（Visual）| 视觉辨识能力、持续注意力 |
| 拼字识别（Spelling）| 音形映射、字序组织、拼写输出 |
| 文字理解（Comprehension）| 阅读理解、语义整合、信息提取 |
| 工作记忆（Working Memory）| 工作记忆容量、短时记忆 |
| 快速命名（Rapid Naming）| 快速命名速度、音韵意识 |
| 精细动作（Motor Coordination）| 精细动作控制、视动整合 |
| 翻牌记忆（Flip Card）| 视觉记忆、空间定位 |
| 连一连（Connect）| 语义关联、逻辑推理 |
| 手写识别（Handwriting）| 笔画顺序、书写流畅度 |

**评分算法：**
```
效率分 = 正确率(60%) + 反应时效率(40%)
注意力维度 = 基于反应时变异系数(CV)独立估算

风险等级：低风险 ≥75 / 中风险 ≥60 / 高风险 <60
```

### 训练系统

- 基于筛查结果自动生成个性化训练任务
- 连续打卡机制，3 / 7 / 30 天设有奖励节点
- 徽章系统（首次游戏、全类型完成、完美得分、速度达标等）
- 星星积分奖励
- 成长里程碑记录与趋势图表

### AI 功能

- 报告个性化解读
- 训练计划生成
- 儿童鼓励话语
- 成长趋势分析
- 每日学习贴士
- 家长情绪支持
- 自适应难度评估建议
- 专业支持引导（含联系方式）
- 知识库语义搜索

> 不配置 `AI_API_KEY` 时，系统自动降级为规则型回复，所有接口仍可正常响应。

---

## 项目结构

```
.
├── backend/
│   ├── app/
│   │   ├── api/                # 路由层
│   │   │   ├── auth.py         # 注册、登录、验证码、微信登录
│   │   │   ├── children.py     # 儿童档案 CRUD
│   │   │   ├── screenings.py   # 筛查流程（题目、提交、历史）
│   │   │   ├── reports.py      # 评估报告与维度分析
│   │   │   ├── training.py     # 训练任务、打卡、奖励
│   │   │   ├── ai_qa.py        # AI 问答（9 项功能）
│   │   │   ├── notifications.py# 通知管理
│   │   │   ├── articles.py     # 知识文章
│   │   │   └── upload.py       # 文件上传
│   │   ├── games/              # 9 种游戏题库生成逻辑
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑（AI、筛查评分、知识库）
│   │   ├── utils/              # 工具函数（安全、加密）
│   │   ├── scheduler.py        # 定时任务（通知、打卡提醒）
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # 应用入口
│   ├── migrations/             # Alembic 数据库迁移脚本
│   ├── tests/                  # 单元测试 & 属性测试
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── parent/         # 家长端（登录、首页、筛查、报告、训练、AI 问答等）
│       │   ├── child/          # 儿童端（首页、游戏大厅、关卡、训练任务）
│       │   └── guest/          # 游客端（免注册体验游戏）
│       ├── components/         # 公共组件（游戏题型、图表等）
│       ├── api/                # API 请求封装
│       ├── stores/             # Pinia 状态管理
│       └── utils/              # 工具函数与常量
│
├── docker-compose.yml          # 开发环境 Docker 配置
├── docker-compose.prod.yml     # 生产环境 Docker 配置
├── deploy.sh                   # 一键部署脚本
├── DEPLOYMENT_GUIDE.md         # 详细部署文档
└── 云打包教程.md                # iOS / Android 云打包指南
```

---

## API 端点

| 前缀 | 功能 |
|------|------|
| `/api/auth` | 注册、登录、验证码、微信登录 |
| `/api/children` | 儿童档案 CRUD |
| `/api/screenings` | 筛查流程（题目、提交、历史）|
| `/api/reports` | 评估报告查询与维度分析 |
| `/api/training` | 训练任务、打卡、奖励、徽章 |
| `/api/ai` | AI 问答（9 项功能）|
| `/api/notifications` | 通知管理 |
| `/api/articles` | 知识文章 |
| `/api/upload` | 文件上传（头像，最大 5MB）|

完整交互文档：开发模式下访问 http://localhost:8000/docs

---

## 功能完成度

| 模块 | 状态 |
|------|------|
| 用户认证（注册 / 登录 / JWT / 微信登录）| ✅ |
| 儿童档案管理 | ✅ |
| 9 种筛查游戏（含自适应难度）| ✅ |
| 评分算法与评估报告 | ✅ |
| AI 问答（9 项功能）| ✅ |
| 训练任务系统 | ✅ |
| 连续打卡与徽章奖励 | ✅ |
| 成长记录与趋势分析 | ✅ |
| 报告对比（复评）| ✅ |
| 通知中心 | ✅ |
| 知识文章 | ✅ |
| 文件上传（头像）| ✅ |
| 游客体验模式 | ✅ |
| 短信验证码 | ⚠️ 需配置服务商 SDK |
| 报告导出（PDF）| ❌ 规划中 |

---

## 开发说明

### 运行测试

```bash
cd backend
pytest tests/
```

### 短信验证码

`DEBUG=True` 时验证码打印到后端日志，无需接入真实 SMS。生产环境在 `app/api/auth.py` 中配置 `SMS_PROVIDER`（支持 `aliyun` / `tencent`）。

### 数据库迁移

开发环境 SQLite 表结构在启动时自动创建。生产环境切换 PostgreSQL 后使用 Alembic：

```bash
cd backend
alembic upgrade head
```

### 安全中间件

`main.py` 内置以下中间件：
- 请求体大小限制（10MB，防 DoS）
- 安全响应头（防 MIME 嗅探、XSS、点击劫持）
- CORS 控制（`DEBUG=False` 时仅允许 `ALLOWED_ORIGINS` 中的域名）

---

## 免责声明

本系统仅作为家庭初步风险筛查工具，筛查结果**不构成医学诊断**。如筛查结果显示中高风险，请及时咨询专业医疗机构或持证评估师进行正式评估。

---

## License

MIT
