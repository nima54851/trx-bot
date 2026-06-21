# TRX Energy Bot — TRX能量租赁Telegram机器人系统

> 一套完整的 TRX 能量租赁系统：Telegram Bot + 后端API + 前端闪租页面 + 管理仪表盘，支持 Docker 一键部署。

## 🏗 系统架构

```
用户 Telegram
    ├── /start → 引导页
    ├── /buy   → 闪租页面（跳转前端）
    ├── /wallet → 钱包地址/余额
    └── /help  → 帮助

管理仪表盘 (localhost:5173/admin)
    ├── 订单管理
    ├── 租户列表
    ├── 收入统计
    └── 系统配置
```

## 📁 项目结构

```
trx-bot/
├── bot/                        # Telegram Bot
│   ├── main.py                 # Bot入口
│   ├── handlers.py             # 命令/回调处理器
│   ├── keyboards.py            # Inline键盘
│   ├── states.py               # 状态机
│   └── config.py               # Bot配置
├── backend/                    # FastAPI 后端
│   ├── main.py                 # API入口
│   ├── config.py               # 配置
│   ├── database.py             # 数据库连接
│   ├── models.py               # SQLAlchemy模型
│   ├── schemas.py              # Pydantic模型
│   ├── api/
│   │   ├── orders.py           # 订单API
│   │   ├── energy.py           # 能量API
│   │   └── admin.py            # 管理API
│   ├── services/
│   │   ├── tron_service.py     # TRON链交互
│   │   ├── payment_service.py   # 支付服务
│   │   └── lease_service.py    # 租赁服务
│   ├── tron_worker.py          # Celery任务
│   └── requirements.txt
├── frontend/                   # 前端
│   ├── index.html              # 闪租页面
│   ├── admin.html              # 管理仪表盘
│   ├── css/style.css
│   └── js/app.js
├── docker-compose.yml          # Docker部署
├── Dockerfile.bot
├── Dockerfile.backend
└── README.md
```

## 🚀 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/trx-bot.git
cd trx-bot

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 TRON API Key 和 Telegram Bot Token

# 3. 一键启动
docker-compose up -d

# 4. 访问
# 闪租页面: http://your-domain/
# 管理后台: http://your-domain/admin
```

## ⚙️ 环境变量

| 变量 | 说明 | 必填 |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Father 获取 | ✅ |
| `TRON_API_KEY` | TRONGrid API Key | ✅ |
| `TRON_WALLET_PRIVATE_KEY` | 能量出租方私钥 | ✅ |
| `DATABASE_URL` | PostgreSQL 连接串 | ✅ |
| `REDIS_URL` | Redis 连接串 | ✅ |
| `ADMIN_USERNAME` | 仪表盘管理员账号 | ✅ |
| `ADMIN_PASSWORD` | 仪表盘管理员密码 | ✅ |

## 📦 获取依赖

```bash
# 后端
cd backend && pip install -r requirements.txt

# Celery Worker
celery -A tron_worker worker --loglevel=info

# 开发模式运行
uvicorn backend.main:app --reload --port 8000
```

## 🔧 TRON 能量租赁原理

1. 用户在前端选择「能量」数量和租用时长
2. 前端调用后端 `/api/orders/create` 创建订单
3. 用户往指定地址转入 TRX 作为押金
4. 后端监听链上交易确认
5. 确认后自动执行 `witness_productivity` 抵押冻结 TRX 获取能量
6. 租期结束后自动解冻返还 TRX

## 📄 许可证

MIT License
