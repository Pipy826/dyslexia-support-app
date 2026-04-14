# 儿童读写障碍智能筛查与干预系统 — 后端

## 技术栈

- **FastAPI** 0.115 + **Uvicorn**
- **SQLAlchemy** 2.0 + **SQLite**（开发）/ PostgreSQL（生产）
- **Pydantic** v2 + **pydantic-settings**
- **JWT** 认证（python-jose）
- **AI**：兼容 OpenAI 格式（OpenAI / DeepSeek / 通义千问）

---

## 快速启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，至少修改 SECRET_KEY

# 4. 启动开发服务器
python run.py
# 或：uvicorn app.main:app --reload --port 8000
```

API 文档（开发模式）：http://localhost:8000/docs

---

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `True` | 生产环境改为 `False` |
| `DATABASE_URL` | `sqlite:///./dyslexia.db` | 数据库连接串 |
| `SECRET_KEY` | ⚠️ 默认值 | **生产必须修改**，生成命令见下 |
| `ALLOWED_ORIGINS` | 空 | 生产环境填前端域名，逗号分隔 |
| `AI_API_KEY` | 空 | 不填则使用规则型回复 |
| `AI_API_BASE_URL` | OpenAI | 兼容 DeepSeek / 通义千问 |
| `AI_MODEL` | `gpt-4o-mini` | 模型名称 |

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API 模块

| 前缀 | 功能 |
|------|------|
| `/api/auth` | 注册、登录、验证码 |
| `/api/children` | 儿童档案 CRUD |
| `/api/screenings` | 筛查流程（题目、提交、历史） |
| `/api/reports` | 评估报告查询 |
| `/api/training` | 训练任务、成长记录、奖励 |
| `/api/ai` | AI 问答（LLM 或规则型） |
| `/api/upload` | 头像上传 |

---

## 筛查游戏

三种类型，各三个难度（L1/L2/L3），每级 10 题：

| 类型 | 评估维度 |
|------|---------|
| `visual` | 视觉辨识、注意力 |
| `spelling` | 音形映射、字序组织、拼写输出 |
| `comprehension` | 阅读理解、语义整合、信息提取 |

风险等级：平均分 ≥75 → 低风险；≥60 → 中风险；<60 → 高风险
