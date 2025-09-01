-- 教材知识库数据库建表脚本
-- 符合JSON Schema规范的数据模型

-- 创建数据库
CREATE DATABASE IF NOT EXISTS llmhomework_knowledge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE llmhomework_knowledge_db;

-- 年级表
CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '年级名称，如：初一、初二、初三',
    code VARCHAR(20) UNIQUE NOT NULL COMMENT '年级代码，如：grade7、grade8、grade9',
    description TEXT COMMENT '年级描述',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 学科表
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL COMMENT '年级ID',
    name VARCHAR(50) NOT NULL COMMENT '学科名称，如：数学、语文、英语',
    code VARCHAR(20) UNIQUE NOT NULL COMMENT '学科代码，如：math、chinese、english',
    description TEXT COMMENT '学科描述',
    difficulty_level INT DEFAULT 1 COMMENT '难度等级：1-5',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES grades(id)
);

-- 章节表
CREATE TABLE chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    name VARCHAR(100) NOT NULL COMMENT '章节名称',
    code VARCHAR(50) NOT NULL COMMENT '章节代码',
    description TEXT COMMENT '章节描述',
    chapter_number INT COMMENT '章节序号',
    difficulty_level INT DEFAULT 1 COMMENT '难度等级：1-5',
    estimated_hours FLOAT DEFAULT 1.0 COMMENT '预计学习时长（小时）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 知识点表
CREATE TABLE knowledge_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL COMMENT '章节ID',
    name VARCHAR(200) NOT NULL COMMENT '知识点名称',
    code VARCHAR(100) NOT NULL COMMENT '知识点代码',
    description TEXT COMMENT '知识点详细描述',
    keywords TEXT COMMENT '关键词，逗号分隔',
    difficulty_level INT DEFAULT 1 COMMENT '难度等级：1-5',
    importance_level INT DEFAULT 1 COMMENT '重要程度：1-5',
    exam_frequency INT DEFAULT 0 COMMENT '考试出现频率',
    learning_objectives TEXT COMMENT '学习目标',
    common_mistakes TEXT COMMENT '常见错误',
    learning_tips TEXT COMMENT '学习技巧',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);

-- 题目表 - 符合JSON Schema
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    
    -- JSON Schema字段
    number VARCHAR(20) NOT NULL COMMENT '题号',
    stem TEXT NOT NULL COMMENT '题目内容',
    answer TEXT NOT NULL COMMENT '学生答案',
    options TEXT COMMENT '选项内容，JSON格式',
    type VARCHAR(50) NOT NULL COMMENT '题目类型：选择题、判断题、填空题等',
    question_id VARCHAR(100) UNIQUE NOT NULL COMMENT '题目唯一ID',
    timestamp BIGINT NOT NULL COMMENT '时间戳',
    
    -- 扩展字段
    correct_answer TEXT COMMENT '正确答案',
    explanation TEXT COMMENT '解析说明',
    difficulty_level INT DEFAULT 1 COMMENT '难度等级：1-5',
    source VARCHAR(200) COMMENT '题目来源',
    source_type VARCHAR(50) COMMENT '来源类型：textbook(教材), exam(考试), exercise(练习)',
    tags TEXT COMMENT '标签，逗号分隔',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 批改结果表 - 符合JSON Schema
CREATE TABLE grading_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL COMMENT '任务唯一ID',
    question_id VARCHAR(100) NOT NULL COMMENT '题目ID',
    
    -- JSON Schema字段
    question TEXT NOT NULL COMMENT '题目内容',
    answer TEXT NOT NULL COMMENT '学生答案',
    type VARCHAR(50) NOT NULL COMMENT '题目类型',
    correct BOOLEAN NOT NULL COMMENT '是否正确',
    score FLOAT NOT NULL COMMENT '得分',
    explanation TEXT NOT NULL COMMENT '批改说明',
    
    -- 扩展字段
    confidence FLOAT DEFAULT 1.0 COMMENT '批改置信度',
    grading_engine VARCHAR(50) COMMENT '批改引擎',
    processing_time FLOAT COMMENT '处理时间（秒）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 任务记录表 - 符合JSON Schema
CREATE TABLE task_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL COMMENT '任务唯一ID',
    timestamp BIGINT NOT NULL COMMENT '时间戳',
    user_id VARCHAR(100) COMMENT '用户ID',
    
    -- JSON Schema字段
    total_questions INT NOT NULL COMMENT '总题数',
    correct_count INT NOT NULL COMMENT '正确题数',
    total_score FLOAT NOT NULL COMMENT '总分',
    accuracy_rate FLOAT NOT NULL COMMENT '正确率',
    
    -- 扩展字段
    wrong_knowledges TEXT COMMENT '错题知识点，JSON格式',
    ai_analysis TEXT COMMENT 'AI分析结果，JSON格式',
    processing_status VARCHAR(20) DEFAULT 'pending' COMMENT '处理状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 题目与知识点的多对多关系表
CREATE TABLE question_knowledge_association (
    question_id INT NOT NULL,
    knowledge_point_id INT NOT NULL,
    relevance_score FLOAT DEFAULT 1.0 COMMENT '关联度评分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id, knowledge_point_id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
);

-- 知识点与知识点的关联关系表
CREATE TABLE knowledge_relationship (
    prerequisite_id INT NOT NULL COMMENT '前置知识点ID',
    dependent_id INT NOT NULL COMMENT '依赖知识点ID',
    relationship_type VARCHAR(50) COMMENT '关系类型：prerequisite(前置), related(相关), advanced(进阶)',
    strength FLOAT DEFAULT 1.0 COMMENT '关系强度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prerequisite_id, dependent_id),
    FOREIGN KEY (prerequisite_id) REFERENCES knowledge_points(id),
    FOREIGN KEY (dependent_id) REFERENCES knowledge_points(id)
);

-- 教材表
CREATE TABLE textbooks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    name VARCHAR(200) NOT NULL COMMENT '教材名称',
    publisher VARCHAR(100) COMMENT '出版社',
    edition VARCHAR(50) COMMENT '版本',
    publish_year INT COMMENT '出版年份',
    isbn VARCHAR(20) COMMENT 'ISBN号',
    description TEXT COMMENT '教材描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 试卷表
CREATE TABLE exam_papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    name VARCHAR(200) NOT NULL COMMENT '试卷名称',
    exam_type VARCHAR(50) COMMENT '考试类型：midterm(期中), final(期末), mock(模拟)',
    exam_year INT COMMENT '考试年份',
    region VARCHAR(100) COMMENT '考试地区',
    total_score INT COMMENT '总分',
    duration INT COMMENT '考试时长（分钟）',
    description TEXT COMMENT '试卷描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 题库表
CREATE TABLE question_banks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL COMMENT '学科ID',
    name VARCHAR(200) NOT NULL COMMENT '题库名称',
    description TEXT COMMENT '题库描述',
    question_count INT DEFAULT 0 COMMENT '题目数量',
    difficulty_distribution TEXT COMMENT '难度分布，JSON格式',
    tags TEXT COMMENT '标签，逗号分隔',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 创建索引
CREATE INDEX idx_subjects_grade_id ON subjects(grade_id);
CREATE INDEX idx_chapters_subject_id ON chapters(subject_id);
CREATE INDEX idx_knowledge_points_chapter_id ON knowledge_points(chapter_id);
CREATE INDEX idx_questions_subject_id ON questions(subject_id);
CREATE INDEX idx_questions_type ON questions(type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX idx_grading_results_task_id ON grading_results(task_id);
CREATE INDEX idx_grading_results_question_id ON grading_results(question_id);
CREATE INDEX idx_task_records_user_id ON task_records(user_id);
CREATE INDEX idx_task_records_timestamp ON task_records(timestamp);

-- 插入基础数据
INSERT INTO grades (name, code, description, sort_order) VALUES
('初一', 'grade7', '初中一年级', 1),
('初二', 'grade8', '初中二年级', 2),
('初三', 'grade9', '初中三年级', 3);

INSERT INTO subjects (grade_id, name, code, description, difficulty_level) VALUES
(1, '数学', 'math', '初中数学', 3),
(1, '语文', 'chinese', '初中语文', 2),
(1, '英语', 'english', '初中英语', 2),
(2, '数学', 'math', '初中数学', 4),
(2, '语文', 'chinese', '初中语文', 3),
(2, '英语', 'english', '初中英语', 3),
(3, '数学', 'math', '初中数学', 5),
(3, '语文', 'chinese', '初中语文', 4),
(3, '英语', 'english', '初中英语', 4);
