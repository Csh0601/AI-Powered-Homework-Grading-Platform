# 🚀 增强型数据收集器使用指南

## 📚 概述

本项目新增了多个增强型数据收集器，专门用于收集网上高质量的教育数据和题目。所有收集器都严格遵守robots.txt和网站使用条款，确保合法合规。

## 🛠️ 新增收集器

### 1. 增强型网络爬虫 (`enhanced_web_crawler.py`)
- **功能**: 爬取多个高质量教育网站
- **目标网站**: 中考网、学科网、21世纪教育网
- **数据类型**: 知识点和题目
- **特点**: 智能内容识别，自动分类

### 2. 高质量题目收集器 (`high_quality_question_collector.py`)
- **功能**: 专门收集高质量题目和知识点
- **目标网站**: 高考网、教育24小时、考试吧
- **数据类型**: 重点题目和核心知识点
- **特点**: 高质量筛选，难度分级

### 3. 统一数据收集管理器 (`unified_data_collector.py`)
- **功能**: 统一管理所有数据收集器
- **特点**: 按优先级运行，统一统计
- **优势**: 一站式数据收集解决方案

## 🚀 快速开始

### 方式1: 使用批处理脚本（推荐）
```bash
# Windows用户
双击运行 start_data_collection.bat

# 或者命令行运行
cd llmhomework_Backend/data_collection
start_data_collection.bat
```

### 方式2: 直接运行Python脚本
```bash
cd llmhomework_Backend/data_collection
python run_data_collection.py
```

### 方式3: 使用统一管理器
```bash
cd llmhomework_Backend/data_collection
python collectors/unified_data_collector.py
```

## 📊 收集器详情

### 增强型网络爬虫
```python
from collectors.enhanced_web_crawler import EnhancedWebCrawler

crawler = EnhancedWebCrawler()
kp_count, q_count = crawler.run_enhanced_crawl()
```

**支持的网站**:
- 中考网 (zhongkao.com)
- 学科网 (zxxk.com)  
- 21世纪教育网 (21cnjy.com)

**收集内容**:
- 知识点: 考点、重点、难点、归纳总结
- 题目: 试题、真题、模拟题、练习题

### 高质量题目收集器
```python
from collectors.high_quality_question_collector import HighQualityQuestionCollector

collector = HighQualityQuestionCollector()
kp_count, q_count = collector.run_quality_crawl()
```

**支持的网站**:
- 高考网 (gaokao.com)
- 教育24小时 (edu24ol.com)
- 考试吧 (exam8.com)

**收集内容**:
- 高质量知识点
- 重点题目和真题
- 按难度分级

### 统一数据收集管理器
```python
from collectors.unified_data_collector import UnifiedDataCollector

collector = UnifiedDataCollector()
result = collector.run_all_collectors()
```

**功能特点**:
- 按优先级自动运行所有收集器
- 统一统计和报告
- 错误处理和重试机制
- 详细的收集日志

## 📁 输出文件结构

```
data_collection/
├── crawled_data/
│   ├── knowledge_points_enhanced_*.csv      # 增强爬虫知识点
│   ├── questions_enhanced_*.csv             # 增强爬虫题目
│   ├── knowledge_points_quality_*.csv       # 高质量收集器知识点
│   ├── questions_quality_*.csv              # 高质量收集器题目
│   └── unified_collection_report_*.json     # 统一收集报告
├── collectors/
│   ├── enhanced_web_crawler.py              # 增强型网络爬虫
│   ├── high_quality_question_collector.py   # 高质量题目收集器
│   └── unified_data_collector.py            # 统一数据收集管理器
└── run_data_collection.py                   # 运行脚本
```

## ⚙️ 配置说明

### 请求间隔设置
所有收集器都设置了合理的请求间隔（2-3秒），避免给目标网站造成压力。

### 内容过滤
- 自动过滤过短或过长的内容
- 智能识别知识点和题目
- 自动分类和标签

### 数据质量保证
- 严格遵守robots.txt
- 自动检查网站使用条款
- 内容去重和验证

## 📊 数据统计

运行完成后，系统会生成详细的统计报告：

```json
{
  "collection_stats": {
    "total_knowledge_points": 1500,
    "total_questions": 2000,
    "successful_collections": 4,
    "failed_collections": 0,
    "files_created": [...]
  }
}
```

## 🔄 后续处理

收集完成后，建议按以下顺序处理数据：

1. **数据统一处理**
   ```bash
   python scripts/unify_data.py
   ```

2. **数据质量验证**
   ```bash
   python scripts/validate_data.py
   ```

3. **导入数据库**
   ```bash
   python scripts/import_to_db.py
   ```

## ⚠️ 注意事项

1. **合法合规**: 所有收集器都严格遵守robots.txt和网站使用条款
2. **请求频率**: 设置了合理的请求间隔，避免给服务器造成压力
3. **数据质量**: 自动过滤和验证收集的数据
4. **错误处理**: 完善的错误处理和重试机制

## 🛠️ 自定义配置

### 修改收集网站
在收集器文件中修改 `education_sites` 或 `quality_sites` 配置：

```python
self.education_sites = {
    'new_site': {
        'base_url': 'https://example.com/',
        'name': '新网站',
        'description': '网站描述',
        'subjects': {...}
    }
}
```

### 调整收集参数
修改请求间隔、内容过滤条件等参数：

```python
self.request_delay = 3  # 请求间隔（秒）
```

## 📞 技术支持

如有问题，请检查：
1. 网络连接是否正常
2. 目标网站是否可访问
3. 是否安装了必要的依赖包

## 🔗 相关文档

- [数据收集模块README](README.md)
- [数据统一处理文档](scripts/README.md)
- [数据验证文档](schemas/README.md)

---

📅 最后更新: 2025-01-28  
🎯 版本: v2.0  
🚀 下个版本计划: 增加更多教育网站支持，优化收集效率

