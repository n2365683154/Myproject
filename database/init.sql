-- 楚然智考系统 - 数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS exam_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE exam_system;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密密码',
    real_name VARCHAR(50) COMMENT '真实姓名',
    avatar VARCHAR(255) COMMENT '头像URL',
    gender TINYINT DEFAULT 0 COMMENT '性别：0未知 1男 2女',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE COMMENT '是否超级管理员',
    last_login DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_phone (phone),
    INDEX idx_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '角色ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码',
    description VARCHAR(255) COMMENT '角色描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '权限ID',
    name VARCHAR(100) NOT NULL COMMENT '权限名称',
    code VARCHAR(100) NOT NULL UNIQUE COMMENT '权限编码',
    description VARCHAR(255) COMMENT '权限描述',
    module VARCHAR(50) COMMENT '所属模块',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_permission_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    role_id INT NOT NULL COMMENT '角色ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE INDEX idx_user_role (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE INDEX idx_role_permission (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- 知识点表
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '知识点ID',
    name VARCHAR(100) NOT NULL COMMENT '知识点名称',
    code VARCHAR(50) UNIQUE COMMENT '知识点编码',
    parent_id INT COMMENT '父级ID',
    level INT DEFAULT 1 COMMENT '层级深度',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    description VARCHAR(500) COMMENT '知识点描述',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_knowledge_parent (parent_id),
    INDEX idx_knowledge_level (level),
    FOREIGN KEY (parent_id) REFERENCES knowledge_points(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点表';

-- 题目表
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '题目ID',
    question_type ENUM('single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'short_answer') NOT NULL DEFAULT 'single_choice' COMMENT '题目类型',
    title TEXT NOT NULL COMMENT '题干内容',
    options TEXT COMMENT '选项JSON',
    answer TEXT NOT NULL COMMENT '正确答案',
    analysis TEXT COMMENT '答案解析',
    difficulty ENUM('easy', 'medium', 'hard') NOT NULL DEFAULT 'medium' COMMENT '难度等级',
    score INT DEFAULT 1 COMMENT '题目分值',
    image_url VARCHAR(500) COMMENT '题目图片URL',
    source VARCHAR(100) COMMENT '题目来源',
    creator_id INT COMMENT '创建者ID',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    use_count INT DEFAULT 0 COMMENT '使用次数',
    correct_count INT DEFAULT 0 COMMENT '正确次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_question_type (question_type),
    INDEX idx_question_difficulty (difficulty),
    INDEX idx_question_active (is_active),
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';

-- 题目知识点关联表
CREATE TABLE IF NOT EXISTS question_knowledge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL COMMENT '题目ID',
    knowledge_id INT NOT NULL COMMENT '知识点ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE INDEX idx_question_knowledge (question_id, knowledge_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目知识点关联表';

-- 考试表
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '考试ID',
    title VARCHAR(200) NOT NULL COMMENT '考试标题',
    description TEXT COMMENT '考试描述',
    exam_type ENUM('practice', 'mock', 'formal') NOT NULL DEFAULT 'mock' COMMENT '考试类型',
    status ENUM('draft', 'published', 'closed') NOT NULL DEFAULT 'draft' COMMENT '考试状态',
    total_score INT DEFAULT 100 COMMENT '总分',
    pass_score INT DEFAULT 60 COMMENT '及格分数',
    duration INT DEFAULT 120 COMMENT '考试时长(分钟)',
    question_count INT DEFAULT 0 COMMENT '题目数量',
    is_random TINYINT DEFAULT 0 COMMENT '是否随机组卷',
    random_config TEXT COMMENT '随机组卷配置JSON',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    allow_review TINYINT DEFAULT 1 COMMENT '是否允许查看解析',
    show_answer TINYINT DEFAULT 1 COMMENT '交卷后是否显示答案',
    max_attempts INT DEFAULT 0 COMMENT '最大尝试次数',
    creator_id INT COMMENT '创建者ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_exam_type (exam_type),
    INDEX idx_exam_status (status),
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试表';

-- 考试题目关联表
CREATE TABLE IF NOT EXISTS exam_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL COMMENT '考试ID',
    question_id INT NOT NULL COMMENT '题目ID',
    sort_order INT DEFAULT 0 COMMENT '题目顺序',
    score INT DEFAULT 1 COMMENT '该题分值',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_exam_question (exam_id, question_id),
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试题目关联表';

-- 考试记录表
CREATE TABLE IF NOT EXISTS exam_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    exam_id INT NOT NULL COMMENT '考试ID',
    status ENUM('in_progress', 'submitted', 'graded') NOT NULL DEFAULT 'in_progress' COMMENT '记录状态',
    score DECIMAL(5,2) DEFAULT 0 COMMENT '得分',
    correct_count INT DEFAULT 0 COMMENT '正确题数',
    wrong_count INT DEFAULT 0 COMMENT '错误题数',
    unanswered_count INT DEFAULT 0 COMMENT '未答题数',
    accuracy DECIMAL(5,2) DEFAULT 0 COMMENT '正确率',
    duration INT DEFAULT 0 COMMENT '实际用时(秒)',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    submit_time DATETIME COMMENT '提交时间',
    is_passed TINYINT DEFAULT 0 COMMENT '是否及格',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_record_user (user_id),
    INDEX idx_record_exam (exam_id),
    INDEX idx_record_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试记录表';

-- 答题详情表
CREATE TABLE IF NOT EXISTS exam_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL COMMENT '考试记录ID',
    question_id INT NOT NULL COMMENT '题目ID',
    user_answer TEXT COMMENT '用户答案',
    is_correct TINYINT DEFAULT 0 COMMENT '是否正确：0错误 1正确 2部分正确',
    score DECIMAL(5,2) DEFAULT 0 COMMENT '得分',
    answer_time INT DEFAULT 0 COMMENT '答题用时(秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_answer_record (record_id),
    INDEX idx_answer_question (question_id),
    FOREIGN KEY (record_id) REFERENCES exam_records(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='答题详情表';

-- 错题本表
CREATE TABLE IF NOT EXISTS wrong_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    question_id INT NOT NULL COMMENT '题目ID',
    wrong_count INT DEFAULT 1 COMMENT '错误次数',
    last_wrong_answer TEXT COMMENT '最近一次错误答案',
    is_mastered TINYINT DEFAULT 0 COMMENT '是否已掌握',
    note TEXT COMMENT '用户笔记',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '首次错误时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_wrong_user (user_id),
    INDEX idx_wrong_question (question_id),
    UNIQUE INDEX idx_wrong_user_question (user_id, question_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='错题本表';

-- 学习记录表
CREATE TABLE IF NOT EXISTS study_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    study_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '学习日期',
    study_duration INT DEFAULT 0 COMMENT '学习时长(分钟)',
    question_count INT DEFAULT 0 COMMENT '练习题数',
    correct_count INT DEFAULT 0 COMMENT '正确题数',
    exam_count INT DEFAULT 0 COMMENT '参加考试次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_study_user (user_id),
    INDEX idx_study_date (study_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习记录表';
