# 儿童读写障碍智能筛查与干预系统

一款面向家长和儿童的读写障碍早期筛查与 AI 干预应用。通过游戏化测评识别风险，接入大语言模型提供个性化报告解读、训练计划生成、成长趋势分析等 AI 功能。

---

## 功能特性

### 核心业务
- **游戏化筛查**：视觉辨识、拼字识别、文字理解三类测评游戏，三档难度（L1/L2/L3）
- **智能评估**：自动计算 7 个能力维度得分，输出低 / 中 / 高风险等级
- **评估报告**：生成详细报告，包含维度雷达图、摘要与干预建议
- **训练系统**：个性化训练任务 + 星星奖励激励机制
- **儿童 & 家长双端界面**：UniApp 跨平台前端，支持 H5 与微信小程序

### AI 功能（由 NVIDIA NIM / OpenAI 兼容接口驱动）

| 功能 | 说明 |
|------|------|
| 💬 流式 AI 问答 | 家长与 AI 实时对话，结合孩子报告数据作为上下文，支持 SSE 流式输出 |
| 📋 个性化报告解读 | 筛查完成后 AI 自动生成专属解读，替代固定模板文字 |
| 🗓️ AI 训练计划生成 | 根据弱项维度一键生成 4 周家庭训练方案，可直接应用到任务列表 |
| 📈 成长趋势分析 | 对比多次筛查数据，AI 生成纵向进步/退步分析报告 |
| 💡 每日学习贴士 | 首页每日推送一条 AI 个性化建议，根据孩子当日状态生成 |
| ❤️ 家长情绪支持 | 高风险结果时自动弹出 AI 安慰与专业引导，消除家长焦虑 |
| 🎮 自适应难度 | 游戏中每 5 题 AI 评估答题表现，自动调整题目难度 |
| 🌟 儿童鼓励话语 | 游戏结束后 AI 根据本次表现生成个性化鼓励，替代固定"太棒了" |

所有 AI 功能均有降级处理，API 不可用时自动回退到模板内容，不影响正常使用。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+、FastAPI、SQLAlchemy、SQLite、JWT |
| 前端 | Vue 3、UniApp、Vite、SCSS |
| AI | NVIDIA NIM（`meta/llama-3.3-70b-instruct`），兼容 OpenAI 格式，可替换为 DeepSeek、通义千问等 |

---

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── ai_qa.py        # AI 全部接口（问答、报告解读、训练计划、趋势分析等）
│   │   │   ├── auth.py         # 注册、登录、验证码
│   │   │   ├── children.py     # 儿童档案管理
│   │   │   ├── screenings.py   # 筛查流程
│   │   │   ├── reports.py      # 报告查询
│   │   │   └── training.py     # 训练任务、成长记录、奖励
│   │   ├── models/             # SQLAlchemy 数据库模型
│   │   ├── schemas/            # Pydantic 数据校验
│   │   ├── services/
│   │   │   ├── ai_service.py   # LLM 调用封装（普通/流式/各业务功能）
│   │   │   └── screening_service.py  # 评分算法与报告生成
│   │   ├── games/              # 题库（visual、spelling、comprehension，各三档难度）
│   │   ├── utils/              # JWT、密码加密
│   │   ├── config.py           # 配置管理（读取 .env）
│   │   └── main.py             # FastAPI 应用入口
│   ├── .env                    # 环境变量（含 AI API Key）
│   ├── requirements.txt
│   └── run.py
└── frontend/
    └── src/
        ├── pages/
        │   ├── parent/
        │   │   ├── home/       # 首页（每日贴士、报告摘要）
        │   │   ├── screening/  # 筛查发起与历史
        │   │   ├── report/     # 报告列表与详情（含 AI 解读、情绪支持弹窗）
        │   │   ├── training/   # 训练计划（含 AI 生成入口）
        │   │   ├── growth/     # 成长趋势分析（新页面）
        │   │   ├── ai-chat/    # 流式 AI 问答
        │   │   └── profile/    # 个人中心
        │   └── child/
        │       ├── home/       # 儿童首页（游戏类型选择）
        │       ├── game/       # 游戏主体（含自适应难度）
        │       ├── reward/     # 奖励页（含 AI 鼓励话语）
        │       └── training/   # 儿童训练乐园
        ├── api/                # 接口封装（含流式 chatStream）
        └── styles/             # 全局样式
```

---

## 快速开始

### 1. 后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（.env 已预置 NVIDIA NIM 配置，开箱即用）
python run.py
```

服务启动后：
- API 文档（Swagger）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 2. 前端

```bash
cd frontend
npm install

# H5 开发模式（推荐）
npm run dev:h5

# 微信小程序开发模式
npm run dev
```

前端启动后访问：http://localhost:8080

### 3. 创建账号

首次运行数据库为空，需先注册账号。可通过前端注册页面，或直接调用接口快速创建：

```bash
# 快速创建测试账号（PowerShell）
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" `
  -ContentType "application/json" `
  -Body '{"username":"test","password":"test123"}'
```

| 账号 | 密码 |
|------|------|
| `test` | `test123` |

---

## 环境变量

`backend/.env` 已预置 NVIDIA NIM 配置，无需额外修改即可使用 AI 功能。如需替换为其他服务：

```env
# NVIDIA NIM（默认）
AI_API_KEY=nvapi-xxxx
AI_API_BASE_URL=https://integrate.api.nvidia.com/v1
AI_MODEL=meta/llama-3.3-70b-instruct

# DeepSeek
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://api.deepseek.com/v1
# AI_MODEL=deepseek-chat

# OpenAI
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://api.openai.com/v1
# AI_MODEL=gpt-4o-mini

# 通义千问
# AI_API_KEY=sk-xxxx
# AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# AI_MODEL=qwen-turbo
```

---

## API 概览

### 业务接口

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/auth` | 注册、登录、验证码、获取当前用户 |
| 儿童档案 | `/api/children` | 增删改查儿童信息 |
| 筛查 | `/api/screenings` | 获取题目、开始/提交筛查、历史记录 |
| 报告 | `/api/reports` | 报告列表、详情、维度分数 |
| 训练 | `/api/training` | 训练任务、成长记录、奖励与星星 |

### AI 接口（`/api/ai`）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | 普通对话 |
| `/chat/stream` | POST | 流式对话（SSE） |
| `/history` | GET | 对话历史 |
| `/report-interpretation` | POST | AI 报告解读 |
| `/training-plan` | POST | AI 生成训练计划 |
| `/encouragement` | POST | 儿童鼓励话语 |
| `/growth-analysis/{child_id}` | GET | 成长趋势分析 |
| `/daily-tip/{child_id}` | GET | 每日学习贴士 |
| `/emotional-support` | POST | 家长情绪支持 |
| `/adaptive-difficulty` | POST | 自适应难度评估 |

---

## 游戏类型与能力维度

| 游戏 | 测评维度 |
|------|----------|
| `visual` 视觉辨识 | 视觉辨识、注意力 |
| `spelling` 拼字识别 | 拼写、音形映射、字序组织 |
| `comprehension` 文字理解 | 阅读理解、语义整合、信息提取 |

难度级别：`L1`（初级）/ `L2`（中级）/ `L3`（高级）  
风险等级：`low`（低风险）/ `medium`（中风险）/ `high`（高风险）

---

## License

MIT
