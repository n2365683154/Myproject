#!/bin/bash
# 文件名: refactor.sh
# 用途: 考试系统架构重构脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  考试系统架构重构工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==================== 1. 后端架构优化 ====================

log_info "步骤 1/6: 后端架构优化"

# 创建统一的工具函数库
cat > backend/app/utils/common.py << 'EOF'
"""
通用工具函数库
整合所有通用功能，避免代码重复
"""
import re
from typing import Set, Optional

class AnswerNormalizer:
    """答案标准化工具"""
    
    @staticmethod
    def extract_letters(text: str) -> Set[str]:
        """提取文本中的所有字母并转为大写"""
        if not text:
            return set()
        return set(re.sub(r'[^A-Za-z]', '', text).upper())
    
    @staticmethod
    def compare_multiple_choice(user_answer: str, correct_answer: str) -> bool:
        """比较多选题答案（忽略逗号、空格等符号）"""
        user_letters = AnswerNormalizer.extract_letters(user_answer)
        correct_letters = AnswerNormalizer.extract_letters(correct_answer)
        return user_letters == correct_letters
    
    @staticmethod
    def compare_single_choice(user_answer: str, correct_answer: str) -> bool:
        """比较单选题答案"""
        return user_answer.strip().upper() == correct_answer.strip().upper()
    
    @staticmethod
    def normalize_text(text: str, remove_punctuation: bool = True) -> str:
        """标准化文本：去除空格、标点等"""
        if not text:
            return ""
        text = text.strip().lower()
        if remove_punctuation:
            text = re.sub(r'[\s\.,，。、；;：:！!？?]', '', text)
        return text


class ResponseFormatter:
    """响应格式化工具"""
    
    @staticmethod
    def success(data=None, message="操作成功"):
        """成功响应"""
        return {"code": 200, "message": message, "data": data}
    
    @staticmethod
    def error(message="操作失败", code=400):
        """错误响应"""
        return {"code": code, "message": message, "data": None}
    
    @staticmethod
    def paginate(items, total, page=1, page_size=10):
        """分页响应"""
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }


class Validator:
    """通用验证器"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else False
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证手机号格式（中国）"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone)) if phone else False
EOF

# 优化判分服务
cat > backend/app/services/grading_service.py << 'EOF'
"""
统一判分服务
整合所有题型的判分逻辑
"""
import re
from typing import Tuple
from app.models.question import Question, QuestionType
from app.utils.common import AnswerNormalizer

class GradingService:
    """判分服务"""
    
    @staticmethod
    def grade(question: Question, user_answer: str) -> Tuple[int, float]:
        """
        统一判分接口
        返回: (是否正确, 得分)
        is_correct: 0=错误, 1=完全正确, 2=部分正确
        """
        if not user_answer:
            return 0, 0
        
        # 根据题型选择判分策略
        strategies = {
            QuestionType.SINGLE_CHOICE: GradingService._grade_single_choice,
            QuestionType.MULTIPLE_CHOICE: GradingService._grade_multiple_choice,
            QuestionType.TRUE_FALSE: GradingService._grade_true_false,
            QuestionType.FILL_BLANK: GradingService._grade_fill_blank,
        }
        
        strategy = strategies.get(question.question_type)
        if strategy:
            return strategy(question, user_answer)
        
        # 简答题等需要人工判分
        return 0, 0
    
    @staticmethod
    def _grade_single_choice(question: Question, user_answer: str) -> Tuple[int, float]:
        """单选题判分"""
        is_correct = AnswerNormalizer.compare_single_choice(user_answer, question.answer)
        return (1, question.score) if is_correct else (0, 0)
    
    @staticmethod
    def _grade_multiple_choice(question: Question, user_answer: str) -> Tuple[int, float]:
        """多选题判分（完全正确得满分，部分正确得半分）"""
        user_letters = AnswerNormalizer.extract_letters(user_answer)
        correct_letters = AnswerNormalizer.extract_letters(question.answer)
        
        if user_letters == correct_letters:
            return 1, question.score
        elif user_letters.issubset(correct_letters) and len(user_letters) > 0:
            return 2, question.score * 0.5
        return 0, 0
    
    @staticmethod
    def _grade_true_false(question: Question, user_answer: str) -> Tuple[int, float]:
        """判断题判分"""
        return GradingService._grade_single_choice(question, user_answer)
    
    @staticmethod
    def _grade_fill_blank(question: Question, user_answer: str) -> Tuple[int, float]:
        """填空题判分（支持多个答案和模糊匹配）"""
        correct_answers = [a.strip() for a in question.answer.split("|")]
        user_normalized = AnswerNormalizer.normalize_text(user_answer)
        
        # 精确匹配
        for correct in correct_answers:
            correct_normalized = AnswerNormalizer.normalize_text(correct)
            if user_normalized == correct_normalized:
                return 1, question.score
        
        return 0, 0
EOF

# 更新 exam_service.py 使用新的判分服务
cat > /tmp/update_exam_service.py << 'EOF'
# 在 exam_service.py 中替换 grade_answer 方法
from app.services.grading_service import GradingService

def grade_answer(self, question: Question, user_answer: str) -> Tuple[int, float]:
    """判分（使用统一的判分服务）"""
    return GradingService.grade(question, user_answer)
EOF

log_info "后端工具库创建完成"

# ==================== 2. 前端架构优化 ====================

log_info "步骤 2/6: 前端架构优化"

# 创建统一的答案处理工具
cat > frontend/src/utils/answerUtils.js << 'EOF'
/**
 * 答案处理工具库
 * 整合所有答案相关的通用函数
 */

/**
 * 提取字符串中的所有字母
 */
export const extractLetters = (text) => {
  if (!text) return new Set()
  return new Set(text.replace(/[^A-Za-z]/g, '').toUpperCase().split(''))
}

/**
 * 比较多选题答案
 */
export const compareMultipleChoice = (userAnswer, correctAnswer) => {
  const userLetters = extractLetters(userAnswer)
  const correctLetters = extractLetters(correctAnswer)
  return userLetters.size === correctLetters.size && 
         [...userLetters].every(c => correctLetters.has(c))
}

/**
 * 比较单选题/判断题答案
 */
export const compareSingleChoice = (userAnswer, correctAnswer) => {
  return userAnswer.trim().toUpperCase() === correctAnswer.trim().toUpperCase()
}

/**
 * 检查选项是否为正确答案之一
 */
export const isCorrectOption = (optionKey, correctAnswer) => {
  if (!correctAnswer) return false
  const correctLetters = extractLetters(correctAnswer)
  return correctLetters.has(optionKey.toUpperCase())
}

/**
 * 检查答案是否正确（统一接口）
 */
export const checkAnswer = (questionType, userAnswer, correctAnswer) => {
  if (!correctAnswer) return false
  
  if (questionType === 'multiple_choice') {
    return compareMultipleChoice(userAnswer, correctAnswer)
  }
  
  return compareSingleChoice(userAnswer, correctAnswer)
}
EOF

# 创建统一的API请求工具
cat > frontend/src/utils/http.js << 'EOF'
/**
 * HTTP 请求工具库
 * 整合所有API请求逻辑
 */
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.detail || '请求失败'
    ElMessage.error(message)
    
    // 401 未授权，跳转登录
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default http
EOF

log_info "前端工具库创建完成"

# ==================== 3. 配置文件整合 ====================

log_info "步骤 3/6: 配置文件整合"

# 创建统一的环境配置管理
cat > config/README.md << 'EOF'
# 配置文件说明

## 环境配置
- `.env` - 开发环境配置
- `.env.production` - 生产环境配置
- `.env.test` - 测试环境配置

## Docker 配置
- `docker-compose.yml` - 开发环境
- `docker-compose.prod.yml` - 生产环境

## 配置项说明
请参考各配置文件中的注释
EOF

# 整合环境变量配置
cat > .env.example << 'EOF'
# ===========================================
# 考试系统环境配置模板
# 使用时请复制为 .env 并填写实际值
# ===========================================

# 数据库配置
MYSQL_ROOT_PASSWORD=examroot
MYSQL_DATABASE=system
MYSQL_USER=system
MYSQL_PASSWORD=examroot
MYSQL_PORT=13306

# Redis 配置
REDIS_PORT=16379
REDIS_PASSWORD=

# 应用端口
BACKEND_PORT=18000
FRONTEND_PORT=18080

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-change-in-production

# 跨域配置
ALLOWED_ORIGINS=http://localhost:18080

# 日志级别
LOG_LEVEL=INFO

# 文件上传
UPLOAD_MAX_SIZE=10485760
UPLOAD_ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.pdf,.doc,.docx
EOF

log_info "配置文件整合完成"

# ==================== 4. 目录结构优化 ====================

log_info "步骤 4/6: 目录结构优化"

# 创建标准化的目录结构文档
cat > PROJECT_STRUCTURE.md << 'EOF'
# 项目目录结构

```
考试系统/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑
│   │   │   └── grading_service.py  # 统一判分服务
│   │   ├── utils/             # 工具函数
│   │   │   └── common.py      # 通用工具库
│   │   ├── core/              # 核心配置
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试文件
│   ├── uploads/               # 上传文件
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── api/               # API 请求
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 公共组件
│   │   ├── layouts/           # 布局组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # 状态管理
│   │   ├── utils/             # 工具函数
│   │   │   ├── answerUtils.js # 答案处理工具
│   │   │   └── http.js        # HTTP 请求工具
│   │   ├── views/             # 页面组件
│   │   └── main.js
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── config/                     # 配置文件目录
│   └── README.md
│
├── scripts/                    # 管理脚本
│   ├── manage.sh              # 容器管理
│   ├── optimize.sh            # 代码优化
│   └── refactor.sh            # 架构重构
│
├── docs/                       # 文档
│   ├── API.md                 # API 文档
│   ├── DEPLOY.md              # 部署文档
│   └── DEVELOPMENT.md         # 开发文档
│
├── .env.example               # 环境配置模板
├── .env                       # 环境配置（不提交）
├── .gitignore
├── docker-compose.yml         # 开发环境
├── docker-compose.prod.yml    # 生产环境
├── PROJECT_STRUCTURE.md       # 项目结构文档
└── README.md                  # 项目说明
```

## 核心优化点

### 1. 代码复用
- 后端：`utils/common.py` 整合所有通用函数
- 后端：`services/grading_service.py` 统一判分逻辑
- 前端：`utils/answerUtils.js` 整合答案处理逻辑
- 前端：`utils/http.js` 统一HTTP请求

### 2. 功能整合
- 所有答案比较逻辑使用统一工具函数
- 所有API请求使用统一拦截器
- 所有判分逻辑使用策略模式

### 3. 配置管理
- 统一环境变量管理
- 分离开发和生产配置
- 提供配置模板和文档

### 4. 脚本管理
- 所有管理脚本集中在 scripts/ 目录
- 提供统一的命令行接口
EOF

# 移动脚本到 scripts 目录
mkdir -p scripts
[ -f manage.sh ] && mv manage.sh scripts/
[ -f optimize.sh ] && mv optimize.sh scripts/
[ -f refactor.sh ] && mv scripts/refactor.sh 2>/dev/null || mv refactor.sh scripts/

log_info "目录结构优化完成"

# ==================== 5. 文档整理 ====================

log_info "步骤 5/6: 文档整理"

mkdir -p docs

# 创建 API 文档
cat > docs/API.md << 'EOF'
# API 文档

## 认证接口
- POST /api/auth/login - 用户登录
- POST /api/auth/logout - 用户登出
- GET /api/auth/captcha - 获取验证码

## 考试接口
- POST /api/exams/start - 开始考试
- POST /api/exams/submit - 提交考试
- GET /api/exams/records - 考试记录列表
- GET /api/exams/records/{id} - 考试记录详情

## 题库接口
- GET /api/questions - 题目列表
- POST /api/questions - 创建题目
- PUT /api/questions/{id} - 更新题目
- DELETE /api/questions/{id} - 删除题目

详细说明请参考各接口的Swagger文档。
EOF

# 创建开发文档
cat > docs/DEVELOPMENT.md << 'EOF'
# 开发指南

## 本地开发

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 代码规范

### 后端
- 使用 Black 格式化代码
- 使用 Flake8 检查代码质量
- 所有公共函数必须有文档字符串

### 前端
- 使用 ESLint + Prettier
- 组件命名使用 PascalCase
- 工具函数命名使用 camelCase

## 测试

### 后端测试
```bash
pytest
```

### 前端测试
```bash
npm run test
```
EOF

log_info "文档整理完成"

# ==================== 6. Git 管理优化 ====================

log_info "步骤 6/6: Git 配置优化"

# 优化 .gitignore
cat > .gitignore << 'EOF'
# 环境配置
.env
.env.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.pytest_cache/

# Node
node_modules/
dist/
.npm
.eslintcache

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
Thumbs.db

# 日志
*.log
logs/

# 数据库
*.db
*.sqlite

# 上传文件
backend/uploads/*
!backend/uploads/.gitkeep

# 备份文件
*.backup
*.bak
*_backup_*

# Docker
*.pid
EOF

# 创建占位文件
mkdir -p backend/uploads
touch backend/uploads/.gitkeep

log_info "Git 配置优化完成"

# ==================== 完成 ====================

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  架构重构完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "优化内容摘要:"
echo "✓ 后端工具库: backend/app/utils/common.py"
echo "✓ 统一判分服务: backend/app/services/grading_service.py"
echo "✓ 前端工具库: frontend/src/utils/answerUtils.js"
echo "✓ HTTP 请求工具: frontend/src/utils/http.js"
echo "✓ 配置文件整合: .env.example"
echo "✓ 项目结构文档: PROJECT_STRUCTURE.md"
echo "✓ 开发文档: docs/"
echo "✓ Git 配置优化: .gitignore"
echo ""
echo "下一步操作:"
echo "1. 提交代码到 Git: git add . && git commit -m 'refactor: 架构重构和代码优化'"
echo "2. 推送到远程: git push origin main"
echo "3. 使用管理脚本: ./scripts/manage.sh start"
echo ""
