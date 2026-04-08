# 儿童读写障碍智能筛查与干预系统 - 后端

## 技术栈
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Authentication

## 快速开始

1. 创建虚拟环境并安装依赖：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 启动服务器：
```bash
python run.py
```

3. 访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 认证
- POST /api/auth/register - 注册
- POST /api/auth/login - 登录
- GET /api/auth/me - 获取当前用户

### 儿童档案
- GET /api/children/ - 获取所有儿童
- POST /api/children/ - 创建儿童档案
- GET /api/children/{id} - 获取单个儿童
- PUT /api/children/{id} - 更新儿童
- DELETE /api/children/{id} - 删除儿童

### 筛查
- GET /api/screenings/questions/{game_type} - 获取题目
- POST /api/screenings/start - 开始筛查
- POST /api/screenings/submit - 提交筛查结果
- GET /api/screenings/history - 获取筛查历史

### 报告
- GET /api/reports/ - 获取报告列表
- GET /api/reports/{id} - 获取报告详情

### 训练
- GET /api/training/tasks - 获取训练任务
- POST /api/training/tasks - 创建训练任务
- GET /api/training/growth - 获取成长记录
- GET /api/training/rewards - 获取奖励
- GET /api/training/stars - 获取星星数量

### AI 问答
- POST /api/ai/chat - 发送消息
- GET /api/ai/history - 获取对话历史

## 游戏类型
- visual - 视觉辨识
- spelling - 拼字识别
- comprehension - 文字理解

## 难度级别
- L1 - 初级
- L2 - 中级
- L3 - 高级
