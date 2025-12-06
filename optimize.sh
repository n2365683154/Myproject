#!/bin/bash
# 文件名: optimize.sh
# 用途: 考试系统代码优化

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印标题
print_header() {
  echo -e "${BLUE}====================================${NC}"
  echo -e "${BLUE} 考试系统代码优化 ${NC}"
  echo -e "${BLUE}====================================${NC}"
}

# 打印日志
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 优化前端代码
optimize_frontend() {
  log_info "优化前端代码..."
  
  # 1. 优化 TakeExam.vue 中的判题逻辑
  log_info "优化多选题判题逻辑..."
  cat > /tmp/optimized_checkAnswer.js << 'EOF'
// 检查答案并显示结果
const checkAnswer = () => {
  if (!currentQuestion.value) return
  
  const qId = currentQuestion.value.id
  const userAnswer = currentAnswer.value || ''
  const correctAnswer = currentQuestion.value.answer || ''
  
  // 如果没有正确答案（非练习模式），不进行判断
  if (!correctAnswer) {
    console.warn('无法获取正确答案，可能不是练习模式')
    return
  }
  
  // 判断是否正确
  let isCorrect = false
  if (currentQuestion.value.question_type === 'multiple_choice') {
    // 多选题：只保留字母，忽略逗号空格等符号
    const userLetters = new Set(userAnswer.replace(/[^A-Za-z]/g, '').toUpperCase().split(''))
    const correctLetters = new Set(correctAnswer.replace(/[^A-Za-z]/g, '').toUpperCase().split(''))
    isCorrect = userLetters.size === correctLetters.size && [...userLetters].every(c => correctLetters.has(c))
  } else {
    // 单选题、判断题：直接比较
    isCorrect = userAnswer.trim().toUpperCase() === correctAnswer.trim().toUpperCase()
  }
  answeredResults[qId] = isCorrect
  showResultMap[qId] = true
  
  // 如果答对且开启自动下一题
  if (isCorrect && autoNext.value) {
    setTimeout(() => {
      if (examStore.currentIndex < examStore.totalQuestions - 1) {
        examStore.nextQuestion()
      }
    }, 800)
  }
}

// 检查是否正确选项
const isCorrectOption = (key) => {
  if (!currentQuestion.value?.answer) return false
  // 只保留字母后检查是否包含该选项
  const correctLetters = currentQuestion.value.answer.replace(/[^A-Za-z]/g, '').toUpperCase()
  return correctLetters.includes(key.toUpperCase())
}
EOF

  docker cp /tmp/optimized_checkAnswer.js exam_frontend:/tmp/optimized_checkAnswer.js
  
  # 将优化后的代码应用到前端容器中
  docker exec -it exam_frontend sh -c "
    cd /usr/share/nginx/html && \
    find . -name '*.js' | xargs grep -l 'checkAnswer' > /tmp/target_files.txt
    
    if [ -s /tmp/target_files.txt ]; then
      TARGET_FILE=\$(cat /tmp/target_files.txt | head -1)
      echo \"找到目标文件: \$TARGET_FILE\"
      
      # 备份原始文件
      cp \"\$TARGET_FILE\" \"/tmp/\$(basename \$TARGET_FILE).backup\"
      
      # 替换判题逻辑
      sed -i 's/function(){var.\+=function(){var.\+=.\+currentQuestion.\+;var.\+=.\+currentAnswer.\+||\"\".\+correctAnswer.\+=.\+currentQuestion.\+||\"\".\+if(!.\+correctAnswer.\+){.\+return}.\+isCorrect.\+=.\+if(.\+question_type.\+===.\+multiple_choice.\+){.\+userSet.\+=.\+Set(.\+).\+correctSet.\+=.\+Set(.\+).\+isCorrect.\+=.\+userSet.\+===.\+correctSet.\+&&.\+}else{.\+isCorrect.\+=.\+userAnswer.\+===.\+correctAnswer.\+}.\+answeredResults.\+=.\+isCorrect.\+showResultMap.\+=.\+true.\+if(.\+isCorrect.\+&&.\+autoNext.\+){.\+setTimeout.\+}.\+}/$(cat /tmp/optimized_checkAnswer.js | tr '\n' ' ' | sed 's/\//\\\//g')/' \"\$TARGET_FILE\"
      
      echo \"判题逻辑已优化\"
    else
      echo \"未找到包含checkAnswer的文件\"
    fi
  "
  
  log_info "前端代码优化完成"
}

# 优化后端代码
optimize_backend() {
  log_info "优化后端代码..."
  
  # 1. 优化 exam_service.py 中的多选题判分逻辑
  cat > /tmp/optimized_grading.py << 'EOF'
    def grade_answer(self, question: Question, user_answer: str) -> Tuple[int, float]:
        """
        判分
        返回: (是否正确, 得分)
        is_correct: 0错误 1正确 2部分正确
        """
        if not user_answer:
            return 0, 0
        
        correct_answer = question.answer.strip()
        user_answer = user_answer.strip()
        
        if question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE]:
            # 单选题、判断题：精确匹配
            if user_answer.upper() == correct_answer.upper():
                return 1, question.score
            return 0, 0
        
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：只保留字母，忽略逗号空格等符号
            correct_letters = set(re.sub(r'[^A-Za-z]', '', correct_answer).upper())
            user_letters = set(re.sub(r'[^A-Za-z]', '', user_answer).upper())
            
            if correct_letters == user_letters:
                return 1, question.score
            elif user_letters.issubset(correct_letters) and len(user_letters) > 0:
                return 2, question.score * 0.5
            return 0, 0
        
        elif question.question_type == QuestionType.FILL_BLANK:
            # 填空题：支持多个答案（用|分隔）和模糊匹配
            correct_answers = [a.strip().lower() for a in correct_answer.split("|")]
            user_answer_lower = user_answer.lower()
            
            # 精确匹配
            if user_answer_lower in correct_answers:
                return 1, question.score
            
            # 模糊匹配（去除空格和标点）
            def normalize(s):
                return re.sub(r'[\s\.,，。、；;：:！!？?]', '', s)
            
            normalized_user = normalize(user_answer_lower)
            for ans in correct_answers:
                if normalize(ans) == normalized_user:
                    return 1, question.score
            
            return 0, 0
        
        # 简答题需要人工判分
        return 0, 0
EOF

  docker cp /tmp/optimized_grading.py exam_backend:/tmp/optimized_grading.py
  
  # 应用到后端容器
  docker exec -it exam_backend sh -c "
    cd /app && \
    grep -r 'def grade_answer' --include='*.py' . > /tmp/target_files.txt
    
    if [ -s /tmp/target_files.txt ]; then
      TARGET_FILE=\$(cat /tmp/target_files.txt | head -1 | cut -d':' -f1)
      echo \"找到目标文件: \$TARGET_FILE\"
      
      # 备份原始文件
      cp \"\$TARGET_FILE\" \"/tmp/\$(basename \$TARGET_FILE).backup\"
      
      # 查找函数的开始和结束行
      LINE_START=\$(grep -n 'def grade_answer' \"\$TARGET_FILE\" | cut -d':' -f1)
      NEXT_DEF=\$(tail -n +\$((LINE_START+1)) \"\$TARGET_FILE\" | grep -n '^    def ' | head -1)
      
      if [ -z \"\$NEXT_DEF\" ]; then
        # 如果没有找到下一个函数定义，使用文件结束
        LINE_END=\$(wc -l < \"\$TARGET_FILE\")
      else
        # 找到下一个函数的行号
        NEXT_DEF_NUM=\$(echo \$NEXT_DEF | cut -d':' -f1)
        LINE_END=\$((LINE_START + NEXT_DEF_NUM - 1))
      fi
      
      # 删除原函数并插入新函数
      sed -i \"\${LINE_START},\${LINE_END}d\" \"\$TARGET_FILE\"
      sed -i \"\${LINE_START}r /tmp/optimized_grading.py\" \"\$TARGET_FILE\"
      
      echo \"判分逻辑已优化\"
    else
      echo \"未找到grade_answer函数\"
    fi
  "
  
  log_info "后端代码优化完成"
}

# 优化 Docker 配置
optimize_docker() {
  log_info "优化 Docker 配置..."
  
  # 备份原始docker-compose文件
  cp docker-compose.prod.yml docker-compose.prod.yml.backup
  
  # 添加资源限制和优化设置
  cat > /tmp/optimized_docker.yml << 'EOF'
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: exam_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-examroot}
      MYSQL_DATABASE: system
      MYSQL_USER: system
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-examroot}
      TZ: Asia/Shanghai
    ports:
      - "13306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    networks:
      - exam_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    # 资源限制
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: exam_redis
    restart: always
    ports:
      - "16379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy volatile-lru
    networks:
      - exam_network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.2'

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: exam_backend
    restart: always
    environment:
      - DATABASE_URL=mysql+pymysql://system:${MYSQL_PASSWORD:-examroot}@mysql:3306/system?charset=utf8mb4
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-production-secret-key-change-this}
      - DEBUG=False
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}
      - TZ=Asia/Shanghai
    ports:
      - "18000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - exam_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  # 前端Nginx服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: exam_frontend
    restart: always
    ports:
      - "18080:80"
    depends_on:
      - backend
    networks:
      - exam_network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.3'

volumes:
  mysql_data:
  redis_data:

networks:
  exam_network:
    driver: bridge
EOF

  cp /tmp/optimized_docker.yml docker-compose.prod.yml
  
  log_info "Docker 配置已优化"
}

# 主函数
main() {
  print_header
  
  log_info "开始项目优化..."
  
  # 备份数据
  log_info "备份当前数据..."
  docker exec exam_mysql mysqldump -u root -pexamroot system > exam_backup_$(date +%Y%m%d_%H%M%S).sql
  
  # 优化各个组件
  optimize_frontend
  optimize_backend
  optimize_docker
  
  log_info "重启服务应用优化..."
  docker-compose -f docker-compose.prod.yml up -d --build
  
  log_info "项目优化完成！"
  echo ""
  echo "请使用 ./manage.sh 脚本进行日常管理操作"
  echo "例如: ./manage.sh start - 启动所有容器"
  echo "      ./manage.sh stop - 停止所有容器"
  echo "      ./manage.sh logs backend - 查看后端日志"
}

# 执行主函数
main "$@"