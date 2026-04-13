# 儿童读写障碍智能筛查与干预系统

一款面向家长和儿童的读写障碍早期筛查与训练应用，通过游戏化测评识别风险，结合 AI 顾问提供个性化干预建议。

---

## 功能特性

- 游戏化筛查：视觉辨识、拼字识别、文字理解三类测评游戏
- 智能评估：自动计算各能力维度得分，输出低 / 中 / 高风险等级
- 评估报告：生成详细报告，包含摘要与干预建议
- 训练系统：个性化训练任务 + 星星奖励激励机制
- AI 问答：接入 OpenAI / DeepSeek / 通义千问等兼容接口，无 Key 时自动降级为规则回复
- 儿童 & 家长双端界面：UniApp 跨平台前端，支持 H5 与微信小程序

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+、FastAPI、SQLAlchemy、SQLite、JWT |
| 前端 | Vue 3、UniApp、Vite、SCSS |
| AI   | OpenAI 兼容 API（可替换为 DeepSeek、通义千问等） |

---

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/          # 路由层（auth、children、screenings、reports、training、ai_qa、upload）
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 数据校验
│   │   ├── services/     # 业务逻辑（筛查评分、AI 服务）
│   │   ├── games/        # 游戏题目生成（visual、spelling、comprehension）
│   │   ├── utils/        # 工具函数（JWT、密码加密）
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库初始化
│   │   └── main.py       # FastAPI 应用入口
│   ├── requirements.txt
│   └── run.py
└── frontend/
    └── src/
        ├── pages/
        │   ├── parent/   # 家长端（登录、注册、报告、AI 问答、成长记录）
        │   └── child/    # 儿童端（首页、游戏、训练、奖励）
        ├── api/          # 接口封装
        └── styles/       # 全局样式
```

---

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，用于启用 AI 功能）
cp .env.example .env
# 编辑 .env，填写 AI_API_KEY、AI_API_BASE_URL、AI_MODEL

# 启动服务
python run.py
```

服务启动后访问：
- API 文档（Swagger）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 前端

```bash
cd frontend
npm install

# H5 开发模式
npm run dev:h5

# 微信小程序开发模式
npm run dev
```

---



## 环境变量

在 `backend/.env` 中配置（参考 `.env.example`）：

```env
# AI 接口（兼容 OpenAI 格式，留空则使用规则型回复）
AI_API_KEY=sk-xxxx
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini

# 也可接入 DeepSeek
# AI_API_BASE_URL=https://api.deepseek.com/v1
# AI_MODEL=deepseek-chat
```

---

## API 概览

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/auth` | 注册、登录、获取当前用户 |
| 儿童档案 | `/api/children` | 增删改查儿童信息 |
| 筛查 | `/api/screenings` | 获取题目、开始/提交筛查、历史记录 |
| 报告 | `/api/reports` | 报告列表与详情 |
| 训练 | `/api/training` | 训练任务、成长记录、奖励与星星 |
| AI 问答 | `/api/ai` | 发送消息、获取对话历史 |
| 文件上传 | `/api/upload` | 上传文件（最大 5MB） |

---

## 游戏类型与能力维度

| 游戏 | 测评维度 |
|------|----------|
| `visual` 视觉辨识 | 视觉辨识、注意力 |
| `spelling` 拼字识别 | 拼写、音形映射、字序组织 |
| `comprehension` 文字理解 | 阅读理解、语义整合、信息提取 |

风险等级：`low`（低风险）/ `medium`（中风险）/ `high`（高风险）

---

## 测试账号

运行以下脚本可自动创建测试数据（需先启动后端服务）：

```bash
cd backend
python create_test_data.py
```

脚本会注册以下两个账号并为账号1创建儿童档案：

| 账号 | 密码 | 说明 |
|------|------|------|
| `test` | `test123456` | 已预置儿童档案：小明（男，2017-03-15，二年级） |
| `demo` | `demo123456` | 空账号，可自行创建档案 |

---

## License

MIT
