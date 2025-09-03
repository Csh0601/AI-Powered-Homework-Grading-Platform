# 📁 Data Collection 目录结构完整说明

## 🎯 总览

data_collection 目录已完全重构并标准化，建立了科学、规范的数据管理体系。

## 📊 目录统计

- **总目录数**: 35个
- **学科数量**: 9个（数学、语文、英语、物理、化学、生物、历史、地理、政治）
- **配置文件**: 3个
- **模板文件**: 2个
- **Schema文件**: 2个

## 🗂️ 完整目录结构

```
data_collection/
│
├── 📄 README.md                              # 主要说明文档
├── 📄 config.json                            # 数据收集配置
├── 📄 REAL_DATA_COLLECTION_PLAN.md          # 数据收集计划
├── 📄 DIRECTORY_STRUCTURE.md                # 本目录结构说明
│
├── 📁 raw/                                   # 原始数据存储区
│   └── subjects/                             # 按学科分类的原始数据
│       ├── math/                             # 数学
│       │   ├── 📄 README.md                  # 数学学科说明
│       │   ├── knowledge_points/            # 数学知识点原始数据
│       │   ├── exam_questions/               # 数学中考真题
│       │   └── mock_questions/               # 数学模拟题
│       ├── chinese/                          # 语文
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── english/                          # 英语
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── physics/                          # 物理
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── chemistry/                        # 化学
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── biology/                          # 生物
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── history/                          # 历史
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       ├── geography/                        # 地理
│       │   ├── knowledge_points/
│       │   ├── exam_questions/
│       │   └── mock_questions/
│       └── politics/                         # 政治
│           ├── knowledge_points/
│           ├── exam_questions/
│           └── mock_questions/
│
├── 📁 processed/                             # 处理后数据存储区
│   ├── 📄 knowledge_points_unified.csv       # 统一格式知识点数据
│   ├── 📄 questions_unified.csv              # 统一格式题目数据
│   ├── 📄 validation_report.json             # 数据验证报告
│   └── 📄 aligned_education.db               # 临时数据库文件
│
├── 📁 templates/                             # 数据模板和示例
│   ├── 📄 knowledge_data_template.json       # 知识点数据模板
│   └── 📄 subject_readme_template.md         # 学科README模板
│
├── 📁 schemas/                               # 数据结构定义
│   ├── 📄 knowledge_point_schema.json        # 知识点数据结构Schema
│   └── 📄 question_schema.json               # 题目数据结构Schema
│
├── 📁 reports/                               # 数据收集报告
│   ├── 📄 collection_summary.json            # 收集汇总报告
│   └── 📄 day2_progress_report_*.json        # 第二天进度报告
│
├── 📁 exports/                               # 导出数据存储区
│   └── (待导出的数据文件)
│
├── 📁 imports/                               # 导入数据存储区
│   └── (待导入的数据文件)
│
├── 📁 logs/                                  # 操作日志存储区
│   └── (系统操作日志文件)
│
├── 📁 temp/                                  # 临时文件存储区
│   └── (临时处理文件)
│
├── 📁 exam_papers/                           # 考试试卷数据
│   └── 📄 sample_questions.json              # 示例题目
│
├── 📁 mock_exams/                            # 模拟考试数据
│   └── (模拟考试相关文件)
│
└── 📁 textbooks/                             # 教材相关数据
    └── 📄 knowledge_points.json              # 教材知识点
```

## 🎯 各目录功能详细说明

### 📂 raw/subjects/ - 学科原始数据区

每个学科目录包含三个子目录：

- **knowledge_points/**: 存储该学科的原始知识点数据
  - 文件格式：CSV, JSON
  - 命名规范：`knowledge_points_[grade]_[date].csv`
  
- **exam_questions/**: 存储该学科的中考真题
  - 文件格式：CSV, JSON
  - 命名规范：`exam_questions_[year]_[region].csv`
  
- **mock_questions/**: 存储该学科的模拟题
  - 文件格式：CSV, JSON  
  - 命名规范：`mock_questions_[source]_[date].csv`

### 📂 processed/ - 处理后数据区

存储经过清洗、验证、标准化的数据：

- **knowledge_points_unified.csv**: 所有学科知识点的统一格式数据
- **questions_unified.csv**: 所有学科题目的统一格式数据
- **validation_report.json**: 数据质量验证报告

### 📂 templates/ - 模板区

提供标准化的数据模板：

- **knowledge_data_template.json**: 九科知识点数据收集模板
- **subject_readme_template.md**: 学科说明文档模板

### 📂 schemas/ - 数据结构定义区

定义数据的标准结构和验证规则：

- **knowledge_point_schema.json**: 知识点数据的JSON Schema定义
- **question_schema.json**: 题目数据的JSON Schema定义

## 📋 数据流转流程

```
1. 原始数据收集 → raw/subjects/[subject]/
2. 数据清洗验证 → temp/
3. 格式标准化  → processed/
4. 质量检查    → reports/
5. 系统导入    → imports/
6. 备份导出    → exports/
```

## 🛠️ 目录使用指南

### 新增数据收集
1. 将原始数据放入对应的 `raw/subjects/[subject]/` 目录
2. 运行数据验证脚本检查质量
3. 处理后的数据自动存储到 `processed/` 目录

### 数据导入系统
1. 从 `processed/` 目录获取标准化数据
2. 使用导入脚本将数据导入数据库
3. 生成导入报告存储到 `reports/` 目录

### 数据备份导出
1. 从系统导出数据到 `exports/` 目录
2. 按时间和版本管理导出文件
3. 定期清理临时文件

## 📊 当前数据统计

### 知识点数据
- **数学**: 8个知识点 (目标50个)
- **语文**: 2个知识点 (目标50个)  
- **英语**: 3个知识点 (目标50个)
- **其他学科**: 待收集

### 题目数据
- **中考真题**: 7道 (目标180道)
- **模拟题**: 2道 (目标135道)

## 🔧 维护与管理

### 定期清理
- **temp/** 目录：每周清理
- **logs/** 目录：保留30天
- **exports/** 目录：按需清理

### 备份策略
- **重要数据**: 每日备份
- **配置文件**: 版本控制
- **处理结果**: 定期归档

### 监控指标
- 数据质量评分
- 收集进度跟踪
- 存储空间使用

## 📞 技术支持

**维护团队**: 成员B（数据架构与后端工程师）  
**联系方式**: 项目内部沟通  
**更新频率**: 根据数据收集进度实时更新

---

**文档版本**: v1.0  
**创建时间**: 2025年9月3日  
**最后更新**: 2025年9月3日
