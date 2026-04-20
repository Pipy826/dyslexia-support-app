# 儿童读写障碍智能筛查与干预系统 — 后端

> FastAPI 后端服务，提供筛查游戏题库、评分算法、AI 问答、训练管理等全部 API。

---

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI + Uvicorn | 0.115.0 |
| ORM | SQLAlchemy | 2.0.36 |
| 数据验证 | Pydantic v2 | 2.9.2 |
| 认证 | JWT (python-jose) + bcrypt | — |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）| — |
| AI | 兼容 OpenAI 格式（OpenAI / DeepSeek / 通义千问）| — |
| 文件处理 | aiofiles | 24.1.0 |
| HTTP 客户端 | httpx | 0.27.2 |

---

## 快速启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，至少修改 SECRET_KEY

# 启动开发服务器（表结构自动创建）
python run.py
# 或：uvicorn app.main:app --reload --port 8000
```

API 文档（开发模式）：http://localhost:8000/docs

---

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `True` | 生产环境改为 `False`，关闭 Swagger 并收紧 CORS |
| `DATABASE_URL` | `sqlite:///./dyslexia.db` | 数据库连接串 |
| `SECRET_KEY` | ⚠️ 默认值 | **生产必须修改** |
| `ALLOWED_ORIGINS` | 空 | 生产环境填前端域名，逗号分隔 |
| `AI_API_KEY` | 空 | 不填则使用规则型回复 |
| `AI_API_BASE_URL` | OpenAI 官方 | 兼容 DeepSeek / 通义千问 |
| `AI_MODEL` | `gpt-4o-mini` | 模型名称 |
| `UPLOAD_DIR` | `uploads` | 文件上传目录 |
| `WX_APPID` | 空 | 微信小程序 AppID |
| `WX_SECRET` | 空 | 微信小程序 Secret |

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API 模块

| 前缀 | 功能 |
|------|------|
| `/api/auth` | 注册、登录、验证码、微信登录 |
| `/api/children` | 儿童档案 CRUD |
| `/api/screenings` | 筛查流程（题目、提交、历史）|
| `/api/reports` | 评估报告查询与维度分析 |
| `/api/training` | 训练任务、成长记录、奖励 |
| `/api/ai` | AI 问答（LLM 或规则型降级）|
| `/api/upload` | 头像上传（最大 5MB）|

---

## 筛查游戏（6 种）

每种游戏分 3 个难度等级（L1/L2/L3），每级 10 题，根据儿童年级自动匹配：

| 类型 | 评估维度 | 时限 |
|------|---------|------|
| `visual` 视觉辨识 | 视觉辨识、持续注意力 | 6–10 秒/题 |
| `spelling` 拼字识别 | 音形映射、字序组织、拼写输出 | 6–10 秒/题 |
| `comprehension` 文字理解 | 阅读理解、语义整合、信息提取 | 6–10 秒/题 |
| `working_memory` 工作记忆 | 工作记忆容量、短时记忆 | 10–15 秒/题 |
| `rapid_naming` 快速命名 | 快速命名速度、音韵意识 | 5–8 秒/题 |
| `motor_coordination` 精细动作 | 精细动作控制、视动整合 | 8–12 秒/题 |

**评分算法：**
```
效率分 = 正确率(60%) + 反应时效率(40%)
注意力维度 = 基于反应时变异系数(CV)独立估算

风险等级：低风险 ≥75 / 中风险 ≥60 / 高风险 <60
```

---

## 开发说明

### 无 AI Key 时的降级处理

不配置 `AI_API_KEY` 时，`ai_service.py` 自动使用规则型回复模板，所有 AI 接口仍可正常响应，不会报错。

### 短信验证码

`DEBUG=True` 时验证码打印到后端日志，无需接入真实 SMS。生产环境需在 `app/api/auth.py` 中接入短信服务商 SDK。

### 数据库迁移

开发环境 SQLite 表结构在启动时自动创建（`create_all`）。生产环境建议切换 PostgreSQL 并使用 Alembic 管理迁移：

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dyslexia
```

### 生产部署

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
