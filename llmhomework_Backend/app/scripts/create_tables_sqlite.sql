-- AI作业批改系统 - 知识库数据库建表脚本（SQLite版本）
-- 用于快速测试和开发，兼容SQLite
-- 支持AI作业批改、知识点分析等核心功能

-- ========================================
-- 1. 基础层级结构表
-- ========================================

-- 年级表
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL, -- 年级名称
    code VARCHAR(10) UNIQUE NOT NULL, -- 年级代码
    description TEXT, -- 年级描述
    sort_order INTEGER DEFAULT 0, -- 排序顺序
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grade_code ON grades(code);
CREATE INDEX idx_grade_active ON grades(is_active);

-- 学科表
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL, -- 年级ID
    name VARCHAR(30) NOT NULL, -- 学科名称
    code VARCHAR(15) UNIQUE NOT NULL, -- 学科代码
    description TEXT, -- 学科描述
    difficulty_level INTEGER DEFAULT 1, -- 难度等级：1-5
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE
);

CREATE INDEX idx_subject_grade ON subjects(grade_id);
CREATE INDEX idx_subject_code ON subjects(code);

-- 章节表
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL, -- 学科ID
    name VARCHAR(100) NOT NULL, -- 章节名称
    code VARCHAR(30) NOT NULL, -- 章节代码
    description TEXT, -- 章节描述
    chapter_number INTEGER, -- 章节编号
    difficulty_level INTEGER DEFAULT 1, -- 难度等级：1-5
    estimated_hours REAL DEFAULT 1.0, -- 预估学习时长（小时）
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE INDEX idx_chapter_subject ON chapters(subject_id);
CREATE INDEX idx_chapter_number ON chapters(chapter_number);

-- 知识点表
CREATE TABLE knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL, -- 章节ID
    name VARCHAR(200) NOT NULL, -- 知识点名称
    code VARCHAR(50) NOT NULL, -- 知识点代码
    description TEXT, -- 知识点详细描述
    difficulty_level INTEGER DEFAULT 1, -- 难度等级：1-5
    importance_level INTEGER DEFAULT 1, -- 重要程度：1-5
    exam_frequency REAL DEFAULT 0.0, -- 考试频率比例(0.0-1.0)
    learning_objectives TEXT, -- 学习目标
    common_mistakes TEXT, -- 常见错误
    learning_tips TEXT, -- 学习技巧
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE INDEX idx_kp_chapter ON knowledge_points(chapter_id);
CREATE INDEX idx_kp_code ON knowledge_points(code);
CREATE INDEX idx_kp_difficulty ON knowledge_points(difficulty_level);
CREATE INDEX idx_kp_importance ON knowledge_points(importance_level);
CREATE INDEX idx_kp_exam_freq ON knowledge_points(exam_frequency);

-- ========================================
-- 2. 题目相关表
-- ========================================

-- 题目表
CREATE TABLE questions (
    question_id VARCHAR(100) PRIMARY KEY, -- 题目唯一业务ID
    subject_id INTEGER NOT NULL, -- 学科ID
    number VARCHAR(20) NOT NULL, -- 题号
    stem TEXT NOT NULL, -- 题目内容
    answer TEXT NOT NULL, -- 学生答案
    type VARCHAR(20) NOT NULL, -- 题目类型
    timestamp INTEGER NOT NULL, -- 时间戳
    correct_answer TEXT, -- 正确答案
    explanation TEXT, -- 解析
    difficulty_level INTEGER DEFAULT 1, -- 难度等级：1-5
    source VARCHAR(100), -- 题目来源
    source_type VARCHAR(20), -- 来源类型：textbook、exam、exercise
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE INDEX idx_question_subject ON questions(subject_id);
CREATE INDEX idx_question_type ON questions(type);
CREATE INDEX idx_question_difficulty ON questions(difficulty_level);
CREATE INDEX idx_question_timestamp ON questions(timestamp);
CREATE INDEX idx_question_number ON questions(number);

-- 题目选项表
CREATE TABLE question_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id VARCHAR(100) NOT NULL, -- 题目业务ID
    option_key VARCHAR(10) NOT NULL, -- 选项键：A、B、C、D等
    option_value TEXT NOT NULL, -- 选项内容
    is_correct BOOLEAN DEFAULT FALSE, -- 是否为正确答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);

CREATE INDEX idx_qo_question ON question_options(question_id);
CREATE INDEX idx_qo_correct ON question_options(is_correct);
CREATE UNIQUE INDEX uk_question_option ON question_options(question_id, option_key);

-- ========================================
-- 3. 关联关系表
-- ========================================

-- 题目知识点关联表
CREATE TABLE question_knowledge_association (
    question_id VARCHAR(100) NOT NULL,
    knowledge_point_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 1.0, -- 关联度评分(0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (question_id, knowledge_point_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
);

CREATE INDEX idx_qka_question ON question_knowledge_association(question_id);
CREATE INDEX idx_qka_knowledge ON question_knowledge_association(knowledge_point_id);
CREATE INDEX idx_qka_relevance ON question_knowledge_association(relevance_score);

-- 知识点关系表
CREATE TABLE knowledge_relationship (
    prerequisite_id INTEGER NOT NULL,
    dependent_id INTEGER NOT NULL,
    relationship_type VARCHAR(20) NOT NULL, -- 关系类型
    strength REAL DEFAULT 1.0, -- 关系强度(0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (prerequisite_id, dependent_id),
    FOREIGN KEY (prerequisite_id) REFERENCES knowledge_points(id) ON DELETE CASCADE,
    FOREIGN KEY (dependent_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
);

CREATE INDEX idx_kr_prerequisite ON knowledge_relationship(prerequisite_id);
CREATE INDEX idx_kr_dependent ON knowledge_relationship(dependent_id);
CREATE INDEX idx_kr_type ON knowledge_relationship(relationship_type);

-- 知识点关键词表
CREATE TABLE knowledge_point_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_point_id INTEGER NOT NULL, -- 知识点ID
    keyword VARCHAR(100) NOT NULL, -- 关键词
    weight REAL DEFAULT 1.0, -- 权重(0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
);

CREATE INDEX idx_kpk_knowledge ON knowledge_point_keywords(knowledge_point_id);
CREATE INDEX idx_kpk_keyword ON knowledge_point_keywords(keyword);

-- ========================================
-- 4. 批改结果表
-- ========================================

-- 批改结果表
CREATE TABLE grading_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(100) NOT NULL, -- 任务唯一ID
    question_id VARCHAR(100) NOT NULL, -- 题目业务ID
    question TEXT NOT NULL, -- 题目内容快照
    answer TEXT NOT NULL, -- 学生答案快照
    type VARCHAR(20) NOT NULL, -- 题目类型
    correct BOOLEAN NOT NULL, -- 是否正确
    score REAL NOT NULL, -- 得分
    explanation TEXT NOT NULL, -- 批改解释
    confidence REAL DEFAULT 1.0, -- 批改置信度(0.0-1.0)
    grading_engine VARCHAR(30), -- 批改引擎
    processing_time REAL, -- 处理时间（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);

CREATE INDEX idx_gr_task ON grading_results(task_id);
CREATE INDEX idx_gr_question ON grading_results(question_id);
CREATE INDEX idx_gr_correct ON grading_results(correct);
CREATE INDEX idx_gr_score ON grading_results(score);

-- 任务记录表
CREATE TABLE task_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(100) UNIQUE NOT NULL, -- 任务唯一ID
    timestamp INTEGER NOT NULL, -- 时间戳
    user_id VARCHAR(100), -- 用户ID
    total_questions INTEGER NOT NULL, -- 总题目数
    correct_count INTEGER NOT NULL, -- 正确数量
    total_score REAL NOT NULL, -- 总分
    accuracy_rate REAL NOT NULL, -- 正确率
    wrong_knowledges TEXT, -- 错误知识点，JSON格式
    ai_analysis TEXT, -- AI分析结果，JSON格式
    processing_status VARCHAR(20) DEFAULT 'pending', -- 处理状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tr_task_id ON task_records(task_id);
CREATE INDEX idx_tr_user ON task_records(user_id);
CREATE INDEX idx_tr_timestamp ON task_records(timestamp);
CREATE INDEX idx_tr_status ON task_records(processing_status);

-- ========================================
-- 5. 学习分析表
-- ========================================

-- 学习记录表
CREATE TABLE learning_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL, -- 用户ID
    question_id VARCHAR(100) NOT NULL, -- 题目业务ID
    knowledge_point_id INTEGER NOT NULL, -- 知识点ID
    answer_time INTEGER, -- 答题用时（秒）
    is_correct BOOLEAN NOT NULL, -- 是否答对
    attempt_count INTEGER DEFAULT 1, -- 尝试次数
    confidence_level INTEGER, -- 学生信心等级(1-5)
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
);

CREATE INDEX idx_lr_user ON learning_records(user_id);
CREATE INDEX idx_lr_question ON learning_records(question_id);
CREATE INDEX idx_lr_knowledge ON learning_records(knowledge_point_id);
CREATE INDEX idx_lr_correct ON learning_records(is_correct);

-- 用户学习画像表
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) UNIQUE NOT NULL, -- 用户ID
    math_level INTEGER DEFAULT 1, -- 数学水平等级(1-5)
    chinese_level INTEGER DEFAULT 1, -- 语文水平等级(1-5)
    english_level INTEGER DEFAULT 1, -- 英语水平等级(1-5)
    preferred_difficulty INTEGER DEFAULT 3, -- 偏好难度等级(1-5)
    learning_style VARCHAR(20) DEFAULT 'mixed', -- 学习风格
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_up_user ON user_profiles(user_id);

-- ========================================
-- 6. 辅助表
-- ========================================

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL, -- 标签名称
    category VARCHAR(30), -- 标签分类
    description TEXT, -- 标签描述
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tag_name ON tags(name);
CREATE INDEX idx_tag_category ON tags(category);

-- 题目标签关联表
CREATE TABLE question_tags (
    question_id VARCHAR(100) NOT NULL,
    tag_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 1.0, -- 关联度评分(0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (question_id, tag_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 教材表
CREATE TABLE textbooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL, -- 学科ID
    name VARCHAR(200) NOT NULL, -- 教材名称
    publisher VARCHAR(100), -- 出版社
    edition VARCHAR(50), -- 版本
    publish_year INTEGER, -- 出版年份
    isbn VARCHAR(20), -- ISBN
    description TEXT, -- 教材描述
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE INDEX idx_textbook_subject ON textbooks(subject_id);

-- 试卷表
CREATE TABLE exam_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL, -- 学科ID
    name VARCHAR(200) NOT NULL, -- 试卷名称
    exam_type VARCHAR(20) NOT NULL, -- 考试类型
    exam_year INTEGER, -- 考试年份
    region VARCHAR(100), -- 考试地区
    total_score INTEGER, -- 总分
    duration INTEGER, -- 考试时长（分钟）
    description TEXT, -- 试卷描述
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE INDEX idx_exam_subject ON exam_papers(subject_id);
CREATE INDEX idx_exam_type ON exam_papers(exam_type);

-- 题库表
CREATE TABLE question_banks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL, -- 学科ID
    name VARCHAR(200) NOT NULL, -- 题库名称
    description TEXT, -- 题库描述
    question_count INTEGER DEFAULT 0, -- 题目数量
    difficulty_distribution TEXT, -- 难度分布，JSON格式
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE INDEX idx_bank_subject ON question_banks(subject_id);

-- ========================================
-- 7. 初始化基础数据
-- ========================================

-- 插入年级数据
INSERT INTO grades (name, code, description, sort_order) VALUES
('初一', 'grade7', '初中一年级', 1),
('初二', 'grade8', '初中二年级', 2),
('初三', 'grade9', '初中三年级', 3);

-- 插入学科数据
INSERT INTO subjects (grade_id, name, code, description, difficulty_level) VALUES
(1, '数学', 'math_grade7', '初一数学', 2),
(1, '语文', 'chinese_grade7', '初一语文', 2),
(1, '英语', 'english_grade7', '初一英语', 2),
(2, '数学', 'math_grade8', '初二数学', 3),
(2, '语文', 'chinese_grade8', '初二语文', 3),
(2, '英语', 'english_grade8', '初二英语', 3),
(2, '物理', 'physics_grade8', '初二物理', 3),
(3, '数学', 'math_grade9', '初三数学', 4),
(3, '语文', 'chinese_grade9', '初三语文', 4),
(3, '英语', 'english_grade9', '初三英语', 4),
(3, '物理', 'physics_grade9', '初三物理', 4),
(3, '化学', 'chemistry_grade9', '初三化学', 4);

-- 插入基础标签
INSERT INTO tags (name, category, description) VALUES
('选择题', 'question_type', '选择题类型标签'),
('填空题', 'question_type', '填空题类型标签'),
('判断题', 'question_type', '判断题类型标签'),
('计算题', 'question_type', '计算题类型标签'),
('应用题', 'question_type', '应用题类型标签'),
('简单', 'difficulty', '简单难度标签'),
('中等', 'difficulty', '中等难度标签'),
('困难', 'difficulty', '困难难度标签');

-- 创建完成提示
SELECT '✅ 数据库表结构创建完成！' as status;
SELECT '📊 共创建 ' || COUNT(*) || ' 个表' as table_count FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';
