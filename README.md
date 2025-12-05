# 楚然智考系统

一个功能完整的在线考试平台，支持管理员/学员双角色、题库管理、在线考试、自动判分等功能。

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **认证**: JWT + 图形验证码 + 短信验证码

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **图表**: ECharts
- **HTTP**: Axios

## 功能特性

### 用户管理
- 用户注册、登录（密码+手机验证码双通道）
- JWT身份认证与RBAC权限控制
- 图形验证码生成与校验
- 短信验证码发送与校验

### 题库管理
- 支持单选题、多选题、判断题、填空题、简答题
- Excel (.xlsx) 导入解析
- Word (.docx) 导入解析
- 图片OCR识别导入（PaddleOCR）
- 知识点树状管理

### 考试功能
- 顺序练习/模拟考试
- 固定组卷/随机组卷
- 自动计时、自动交卷
- 自动判分（选择题精确匹配，填空题模糊匹配）
- 错题记录与重做
- 学习记录统计

## 项目结构

```
考试系统/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库连接
│   │   ├── redis_client.py # Redis客户端
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── layouts/       # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── styles/        # 全局样式
│   │   └── views/         # 页面组件
│   ├── package.json
│   └── Dockerfile
├── database/              # 数据库脚本
│   └── init.sql
├── nginx/                 # Nginx配置
│   └── nginx.conf
├── docker-compose.yml     # Docker编排
└── README.md
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7+

### 本地开发

#### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. 访问系统

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/docs

### Docker部署

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 默认账号

系统启动后会自动创建默认管理员账号：

- **用户名**: admin
- **密码**: admin123

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 配置说明

### 后端配置 (.env)

```env
# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/exam_system

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 阿里云短信（可选）
ALIYUN_ACCESS_KEY_ID=your-key-id
ALIYUN_ACCESS_KEY_SECRET=your-key-secret
ALIYUN_SMS_SIGN_NAME=楚然智考
ALIYUN_SMS_TEMPLATE_CODE=SMS_123456789
```

### 前端配置

开发环境下，API请求会自动代理到后端服务。生产环境需要配置Nginx反向代理。

## 题库导入格式

### Excel格式
| 题型 | 题干 | 选项 | 答案 | 解析 | 知识点 | 难度 |
|------|------|------|------|------|--------|------|
| 单选题 | 题目内容 | A.选项A B.选项B | A | 解析内容 | 知识点名称 | 简单 |

### Word格式
```
【选择题】
1. 题目内容
A. 选项A
B. 选项B
C. 选项C
D. 选项D
答案：A
解析：解析内容
```

## 开发计划

- [ ] 支持更多题型（连线题、排序题）
- [ ] 支持试卷打印导出
- [ ] 支持成绩证书生成
- [ ] 移动端适配优化
- [ ] 支持视频题目

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
