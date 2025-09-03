# 📚 数据收集目录结构说明

## 📁 目录概览

本目录包含AI作业批改系统的所有数据收集、处理和管理功能。

```
data_collection/
├── 📁 raw/                     # 原始数据存储
│   └── subjects/               # 按学科分类的原始数据
│       ├── math/               # 数学
│       ├── chinese/            # 语文
│       ├── english/            # 英语
│       ├── physics/            # 物理
│       ├── chemistry/          # 化学
│       ├── biology/            # 生物
│       ├── history/            # 历史
│       ├── geography/          # 地理
│       └── politics/           # 政治
├── 📁 processed/               # 处理后的数据
├── 📁 templates/               # 数据模板和示例
├── 📁 schemas/                 # 数据结构定义
├── 📁 exports/                 # 导出的数据文件
├── 📁 imports/                 # 待导入的数据文件
├── 📁 reports/                 # 数据收集报告
├── 📁 logs/                    # 操作日志
├── 📁 temp/                    # 临时文件
├── 📁 exam_papers/             # 考试试卷数据
├── 📁 mock_exams/              # 模拟考试数据
└── 📁 textbooks/               # 教材相关数据
```

## 🎯 各目录功能说明

### 📂 raw/ - 原始数据存储
存储从各种来源收集的原始数据，按学科进行分类管理。

**每个学科目录包含：**
- `knowledge_points/` - 知识点原始数据
- `exam_questions/` - 中考真题原始数据  
- `mock_questions/` - 模拟题原始数据

### 📂 processed/ - 处理后数据
存储经过清洗、验证和标准化的数据，可直接用于系统导入。

**主要文件：**
- `knowledge_points_unified.csv` - 统一格式的知识点数据
- `questions_unified.csv` - 统一格式的题目数据
- `validation_report.json` - 数据验证报告

### 📂 templates/ - 数据模板
包含数据收集的标准模板和示例格式。

**主要文件：**
- `knowledge_data_template.json` - 知识点数据模板
- `question_data_template.json` - 题目数据模板

### 📂 schemas/ - 数据结构定义
定义各种数据的标准结构和验证规则。

### 📂 exports/ - 导出数据
存储从系统导出的数据文件，用于备份或交换。

### 📂 imports/ - 导入数据
存储待导入到系统的数据文件。

### 📂 reports/ - 数据报告
包含数据收集进度、质量分析等各类报告。

### 📂 logs/ - 操作日志
记录数据收集、处理、验证等操作的详细日志。

### 📂 temp/ - 临时文件
存储处理过程中的临时文件，定期清理。

## 📋 数据管理规范

### ✅ 文件命名规范
- 使用小写字母和下划线
- 包含日期：`filename_YYYYMMDD.extension`
- 版本控制：`filename_v1.0.extension`

### 📊 数据质量标准
- **完整性**：所有必填字段完整
- **准确性**：内容符合教学大纲
- **一致性**：格式统一规范
- **时效性**：数据及时更新

### 🔄 数据处理流程
1. **收集** → `raw/` 目录
2. **清洗** → 标准化处理
3. **验证** → 质量检查
4. **存储** → `processed/` 目录
5. **导入** → 系统数据库

## 🛠️ 常用操作

### 数据收集
```bash
# 执行数据收集脚本
python ../app/scripts/collect_knowledge_data.py
```

### 数据验证
```bash
# 执行数据验证
python ../app/scripts/validate_collected_data.py
```

### 数据导入
```bash
# 导入到数据库
python ../app/scripts/import_collected_data.py
```

## 📞 支持与维护

如遇问题或需要协助，请参考：
- `REAL_DATA_COLLECTION_PLAN.md` - 详细的数据收集计划
- `reports/` 目录下的最新报告
- 系统日志文件

---
**维护人员：成员B（数据架构与后端工程师）**  
**最后更新：2025年1月28日**
