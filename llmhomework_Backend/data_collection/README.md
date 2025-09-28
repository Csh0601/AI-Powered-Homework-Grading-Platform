# 📚 数据收集模块 (Data Collection)

AI智能作业批改系统的数据收集、处理和管理模块。

## 📁 目录结构

```
data_collection/
├── 📂 collectors/           # 数据收集器（已精简）
│   ├── smart_data_generator.py      # AI智能数据生成器（核心）
│   ├── data_enhancer.py            # 数据增强器（质量提升）
│   ├── legal_education_crawler.py   # 合法教育网站爬虫（唯一爬虫）
│   └── pdf_document_processor.py    # PDF文档处理器
├── 📂 raw/                  # 原始数据存储
│   └── subjects/            # 按学科分类的原始数据
│       ├── math/            # 数学
│       ├── chinese/         # 语文
│       ├── english/         # 英语
│       ├── physics/         # 物理
│       ├── chemistry/       # 化学
│       ├── biology/         # 生物
│       ├── history/         # 历史
│       ├── geography/       # 地理
│       └── politics/        # 政治
├── 📂 processed/            # 处理后的数据
│   ├── knowledge_points_unified.csv # 统一的知识点数据
│   ├── questions_unified.csv        # 统一的题目数据
│   ├── aligned_education.db         # 对齐后的教育数据库
│   └── validation_report.json       # 数据验证报告
├── 📂 imports/              # 数据导入目录
├── 📂 exports/              # 数据导出目录
├── 📂 temp/                 # 临时文件
├── 📂 logs/                 # 日志文件
├── 📂 reports/              # 数据收集报告
├── 📂 schemas/              # 数据结构定义
│   ├── knowledge_point_schema.json  # 知识点数据结构
│   └── question_schema.json         # 题目数据结构
├── 📂 scripts/              # 数据处理脚本
│   ├── unify_data.py                # 数据统一处理
│   ├── unify_data_new.py            # 新版数据统一处理
│   ├── validate_data.py             # 数据验证
│   └── import_to_db.py              # 导入数据库
├── data_collection_manager.py       # 数据收集管理平台（统一入口）
├── config.json              # 配置文件
└── README.md               # 本文档
```

## 🚀 快速开始

### 1. 运行数据收集

```bash
# 方式1: 使用统一管理平台（推荐）
python data_collection_manager.py full

# 方式2: 单独运行各个收集器
python collectors/smart_data_generator.py     # AI生成数据
python collectors/data_enhancer.py           # 数据质量增强
python collectors/legal_education_crawler.py  # 爬取网站数据
python collectors/pdf_document_processor.py   # 处理PDF文档

# 方式3: 分步骤执行
python data_collection_manager.py step collection   # 数据收集
python data_collection_manager.py step unification  # 数据统一
python data_collection_manager.py step enhancement  # 数据增强
python data_collection_manager.py step validation   # 数据验证
```

### 2. 数据处理流程

```bash
# 1. 统一数据格式
python scripts/unify_data.py

# 2. 验证数据质量
python scripts/validate_data.py

# 3. 导入数据库
python scripts/import_to_db.py
```

## 📊 数据来源

### 🤖 AI智能生成
- **文件**: `collectors/smart_data_generator.py`
- **说明**: 基于课程标准和教学大纲，AI生成高质量的知识点和题目
- **覆盖**: 9个学科，7-9年级
- **数量**: 每次生成约100个知识点，200道题目

### 🌐 官方网站爬取
- **文件**: `collectors/legal_education_crawler.py`
- **数据源**:
  - 中考网 (zhongkao.com) - 专业中考资源
  - 学科网 (zxxk.com) - 优质教育资源
  - 教育部官网 - 课程标准
  - 国家智慧教育平台 - 官方教材
- **特点**: 严格遵守robots.txt，合法合规

### 📄 PDF文档处理
- **文件**: `collectors/pdf_document_processor.py`
- **说明**: 自动提取教材PDF中的知识点和题目
- **支持格式**: PDF教材、试卷、教辅资料

## 📋 数据结构

### 知识点数据结构 (Knowledge Points)
```json
{
  "id": "唯一标识符",
  "name": "知识点名称",
  "subject": "学科 (数学/语文/英语等)",
  "grade": "年级 (Grade 7/8/9)",
  "chapter": "章节",
  "description": "详细描述",
  "difficulty_level": "难度等级 (1-5)",
  "importance_level": "重要程度 (1-5)",
  "exam_frequency": "考试频率 (0.0-1.0)",
  "keywords": ["关键词列表"],
  "learning_objectives": "学习目标",
  "common_mistakes": "常见错误",
  "learning_tips": "学习建议"
}
```

### 题目数据结构 (Questions)
```json
{
  "question_id": "题目唯一标识",
  "subject": "学科",
  "grade": "年级",
  "question_type": "题目类型 (choice/fill_blank/calculation/application)",
  "stem": "题目内容",
  "options": ["选项列表"],
  "correct_answer": "正确答案",
  "explanation": "答案解析",
  "difficulty_level": "难度等级",
  "knowledge_points": ["关联知识点"],
  "source": "数据来源",
  "tags": ["标签"]
}
```

## ⚙️ 配置说明

### config.json 配置文件
```json
{
  "subjects": {
    "数学": {
      "code": "math",
      "grades": ["Grade 7", "Grade 8", "Grade 9"],
      "target_knowledge_points": 50,
      "target_questions": 35,
      "priority": 1
    }
  },
  "data_quality_standards": {
    "knowledge_points": {
      "min_description_length": 10,
      "max_description_length": 1000,
      "difficulty_range": [1, 5]
    }
  }
}
```

## 🔧 主要脚本说明

### 数据收集器 (Collectors)

#### 1. 智能数据生成器
```python
# 使用示例
from collectors.smart_data_generator import SmartDataGenerator

generator = SmartDataGenerator()
generator.generate_all_subjects()  # 生成所有学科数据
```

#### 2. 数据增强器
```python
# 使用示例
from collectors.data_enhancer import DataEnhancer

enhancer = DataEnhancer()
kp_file, q_file = enhancer.run_full_enhancement()  # 增强数据质量
```

#### 3. 合法教育爬虫
```python
# 使用示例
from collectors.legal_education_crawler import LegalEducationCrawler

crawler = LegalEducationCrawler()
kp_count, q_count = crawler.run_full_crawl()  # 爬取合法教育资源
```

### 数据处理脚本 (Scripts)

#### 1. 数据统一处理
- **脚本**: `scripts/unify_data_new.py` (推荐)
- **功能**: 将不同来源的数据统一格式，支持去重和质量修复
- **输出**: `processed/knowledge_points_unified_*.csv`, `processed/questions_unified_*.csv`

#### 2. 数据质量验证
- **脚本**: `scripts/validate_data.py`
- **功能**: 验证数据完整性和质量
- **输出**: `processed/validation_report.json`

#### 3. 数据库导入
- **脚本**: `scripts/import_to_db.py`
- **功能**: 将处理后的数据导入系统数据库

#### 4. 统一管理平台
- **脚本**: `data_collection_manager.py`
- **功能**: 一站式数据收集、处理、增强管理平台

## 📈 数据统计

当前数据状况：
- **知识点总数**: 96个
- **题目总数**: 94道
- **覆盖学科**: 数学、语文、英语 (重点)
- **年级覆盖**: 7-9年级
- **数据质量**: 优秀 ✅

## 🛠️ 维护和扩展

### 添加新的数据源
1. 在 `collectors/` 目录下创建新的收集器
2. 继承基础类并实现必要方法
3. 在 `data_collection_manager.py` 中注册新收集器
4. 更新配置文件 `config.json`

### 数据质量控制
1. 所有数据必须通过schema验证
2. 定期运行数据质量检查
3. 维护数据来源的合法性和时效性

### 性能优化
- 使用缓存减少重复处理
- 并行处理提高数据收集效率
- 定期清理临时文件和过期数据

## 📞 支持与维护

- **负责人**: 项目成员B (数据库+后端)
- **更新频率**: 每周更新数据
- **质量保证**: 自动化验证 + 人工审核

## 🔗 相关文档

- [API接口文档](../app/api/README.md)
- [数据库设计文档](../app/models/README.md)
- [系统架构文档](../../开发计划/项目技术架构说明.md)

---

📅 最后更新: 2025-09-07  
📊 数据版本: v1.2  
🎯 下个版本计划: 增加更多学科支持，优化数据质量