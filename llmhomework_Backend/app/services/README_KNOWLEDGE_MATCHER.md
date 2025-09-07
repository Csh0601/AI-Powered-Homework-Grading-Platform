# 题目到知识点智能匹配算法

## 概述

实现题目文本到知识点的自动匹配，支持多标签分类和智能推荐。

## 主要功能

- **TF-IDF关键词匹配**：基于词频算法的文本匹配
- **语义相似度计算**：语义关联分析
- **多标签分类**：一题匹配多个知识点
- **难度评估**：自动分析题目难度
- **个性化推荐**：基于薄弱点推荐

## 基本使用

```python
from app.services.knowledge_matcher import KnowledgeMatcher

# 初始化并匹配
matcher = KnowledgeMatcher()
matches = matcher.ensemble_match("解一元一次方程：2x + 3 = 7", top_k=3)

# 批量匹配
questions = ["题目1", "题目2", "题目3"]
batch_results = matcher.batch_match(questions, top_k=3)
```

## API接口

```
POST /api/knowledge-matcher/match          # 单题目匹配
POST /api/knowledge-matcher/batch-match    # 批量匹配
POST /api/knowledge-matcher/recommend      # 知识点推荐
GET  /api/knowledge-matcher/statistics     # 获取统计信息
```

## 支持的知识点

- **数学**: 代数(方程、不等式)、几何(三角形、圆)、函数(一次、二次)
- **语文**: 文学(诗歌、散文)、语法(句式结构)
- **物理**: 力学(运动学、力学)

## 性能指标

- 响应时间: < 0.5秒/题
- 匹配准确率: ≥ 75%
- 支持13个预定义知识点