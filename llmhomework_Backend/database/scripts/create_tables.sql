-- AI作业批改系统 - 知识库数据库建表脚本（精简版）
-- 去除冗余功能，保留核心结构
-- 兼容MySQL，支持AI作业批改、知识点分析等核心功能

-- 创建数据库
CREATE DATABASE IF NOT EXISTS llmhomework_knowledge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE llmhomework_knowledge_db;

-- ========================================
-- 1. 基础层级结构表
-- ========================================

-- 年级表
CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL COMMENT '年级名称',
    code VARCHAR(10) UNIQUE NOT NULL COMMENT '年级代码',
    description TEXT COMMENT '年级描述',
    sort_order SMALLINT DEFAULT 0 COMMENT '排序顺序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_grade_code (code),
    INDEX idx_grade_active (is_active)
);

-- 学科表
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL COMMENT '年级ID',
    name VARCHAR(30) NOT NULL COMMENT '学科名称',
    code VARCHAR(15) UNIQUE NOT NULL COMMENT '学科代码',
    description TEXT COMMENT '学科描述',
    difficulty_level TINYINT DEFAULT 1 COMMENT '难度等级：1-5',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
    INDEX idx_subject_grade (grade_id),
    INDEX idx_subject_code (code)
);

-- 章节表
CREATE TABLE chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    name VARCHAR(100) NOT NULL COMMENT '章节名称',
    code VARCHAR(30) NOT NULL COMMENT '章节代码',
    description TEXT COMMENT '章节描述',
    chapter_number SMALLINT COMMENT '章节编号',
    difficulty_level TINYINT DEFAULT 1 COMMENT '难度等级：1-5',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX idx_chapter_subject (subject_id),
    INDEX idx_chapter_number (chapter_number)
);

-- 知识点表
CREATE TABLE knowledge_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL COMMENT '章节ID',
    name VARCHAR(200) NOT NULL COMMENT '知识点名称',
    code VARCHAR(50) NOT NULL COMMENT '知识点代码',
    description TEXT COMMENT '知识点详细描述',
    difficulty_level TINYINT DEFAULT 1 COMMENT '难度等级：1-5',
    importance_level TINYINT DEFAULT 1 COMMENT '重要程度：1-5',
    exam_frequency FLOAT DEFAULT 0.0 COMMENT '考试频率比例(0.0-1.0)',
    learning_objectives TEXT COMMENT '学习目标',
    common_mistakes TEXT COMMENT '常见错误',
    learning_tips TEXT COMMENT '学习技巧',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    INDEX idx_kp_chapter (chapter_id),
    INDEX idx_kp_difficulty (difficulty_level),
    INDEX idx_kp_importance (importance_level)
);

-- ========================================
-- 2. 题目相关表
-- ========================================

-- 题目表
CREATE TABLE questions (
    question_id VARCHAR(100) PRIMARY KEY COMMENT '题目唯一业务ID',
    subject_id INT NOT NULL COMMENT '学科ID',
    number VARCHAR(20) NOT NULL COMMENT '题号',
    stem TEXT NOT NULL COMMENT '题目内容',
    answer TEXT NOT NULL COMMENT '学生答案',
    type VARCHAR(20) NOT NULL COMMENT '题目类型',
    timestamp BIGINT NOT NULL COMMENT '时间戳',
    correct_answer TEXT COMMENT '正确答案',
    explanation TEXT COMMENT '解析',
    difficulty_level TINYINT DEFAULT 1 COMMENT '难度等级：1-5',
    source VARCHAR(100) COMMENT '题目来源',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX idx_question_subject (subject_id),
    INDEX idx_question_type (type),
    INDEX idx_question_difficulty (difficulty_level)
);

-- 题目选项表
CREATE TABLE question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(100) NOT NULL COMMENT '题目业务ID',
    option_key VARCHAR(10) NOT NULL COMMENT '选项键：A、B、C、D等',
    option_value TEXT NOT NULL COMMENT '选项内容',
    is_correct BOOLEAN DEFAULT FALSE COMMENT '是否为正确答案',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    UNIQUE KEY uk_question_option (question_id, option_key)
);

-- ========================================
-- 3. 关联关系表
-- ========================================

-- 题目知识点关联表
CREATE TABLE question_knowledge_association (
    question_id VARCHAR(100) NOT NULL,
    knowledge_point_id INT NOT NULL,
    relevance_score FLOAT DEFAULT 1.0 COMMENT '关联度评分(0.0-1.0)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (question_id, knowledge_point_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE,
    INDEX idx_qka_relevance (relevance_score)
);

-- 知识点关键词表
CREATE TABLE knowledge_point_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    knowledge_point_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0 COMMENT '权重(0.0-1.0)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE,
    INDEX idx_kpk_keyword (keyword)
);

-- ========================================
-- 4. 批改结果表
-- ========================================

-- 批改结果表
CREATE TABLE grading_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL COMMENT '任务唯一ID',
    question_id VARCHAR(100) NOT NULL COMMENT '题目业务ID',
    question TEXT NOT NULL COMMENT '题目内容快照',
    answer TEXT NOT NULL COMMENT '学生答案快照',
    type VARCHAR(20) NOT NULL COMMENT '题目类型',
    correct BOOLEAN NOT NULL COMMENT '是否正确',
    score FLOAT NOT NULL COMMENT '得分',
    explanation TEXT NOT NULL COMMENT '批改解释',
    confidence FLOAT DEFAULT 1.0 COMMENT '批改置信度(0.0-1.0)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_gr_task (task_id),
    INDEX idx_gr_correct (correct)
);

-- 任务记录表
CREATE TABLE task_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL COMMENT '任务唯一ID',
    timestamp BIGINT NOT NULL COMMENT '时间戳',
    user_id VARCHAR(100) COMMENT '用户ID',
    total_questions INT NOT NULL COMMENT '总题目数',
    correct_count INT NOT NULL COMMENT '正确数量',
    total_score FLOAT NOT NULL COMMENT '总分',
    accuracy_rate FLOAT NOT NULL COMMENT '正确率',
    wrong_knowledges JSON COMMENT '错误知识点，JSON格式',
    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_tr_user (user_id),
    INDEX idx_tr_status (processing_status)
);

-- ========================================
-- 5. 插入基础数据
-- ========================================

-- 插入年级数据
INSERT INTO grades (name, code, description, sort_order) VALUES
('Grade 7', 'grade7', '初一', 1),
('Grade 8', 'grade8', '初二', 2),
('Grade 9', 'grade9', '初三', 3);

-- 插入学科数据
INSERT INTO subjects (grade_id, name, code, description, difficulty_level) VALUES
(1, 'Mathematics', 'math', '数学', 3),
(1, 'Chinese', 'chinese', '语文', 2),
(1, 'English', 'english', '英语', 2),
(2, 'Physics', 'physics', '物理', 4),
(2, 'Chemistry', 'chemistry', '化学', 4),
(2, 'Biology', 'biology', '生物', 3),
(3, 'History', 'history', '历史', 2),
(3, 'Geography', 'geography', '地理', 3),
(3, 'Politics', 'politics', '政治', 2);

-- ========================================
-- 6. 创建核心视图
-- ========================================

-- 知识点层级视图
CREATE VIEW v_knowledge_hierarchy AS
SELECT 
    g.name as grade_name,
    s.name as subject_name,
    c.name as chapter_name,
    kp.name as knowledge_point_name,
    kp.difficulty_level,
    kp.importance_level
FROM grades g
JOIN subjects s ON g.id = s.grade_id
JOIN chapters c ON s.id = c.subject_id
JOIN knowledge_points kp ON c.id = kp.chapter_id
WHERE g.is_active = TRUE AND s.is_active = TRUE 
  AND c.is_active = TRUE AND kp.is_active = TRUE;
