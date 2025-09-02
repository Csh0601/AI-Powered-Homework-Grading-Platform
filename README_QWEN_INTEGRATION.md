# Qwen3:30B 大模型集成说明

## 概述

本项目已成功集成 Qwen3:30B 远程大模型，实现了智能作业批改、知识点分析和练习题生成功能。

## 功能特性

### 1. 多模态智能批改
- 结合 OCR 图像识别和 Qwen3:30B 文本理解
- 支持选择题、判断题、填空题、计算题等多种题型
- 提供详细的批改说明和评分

### 2. 知识点分析
- AI 自动识别错题涉及的知识点
- 生成个性化学习建议
- 分析题目难度和类型分布

### 3. 练习题生成
- 根据错题知识点自动生成相关练习题
- 支持不同难度梯度的题目生成
- 包含答案和详细解析

### 4. 回退机制
- 当 Qwen3:30B 服务不可用时自动回退到传统批改方式
- 确保系统稳定性和可用性

## 安装和配置

### 1. 服务器端配置 Qwen3:30B 模型

```bash
# 在远程服务器上配置
ssh cshcsh@172.31.179.77

# 下载 Qwen3:30B 模型
ollama pull qwen3:30B

# 配置服务监听
export OLLAMA_HOST=0.0.0.0:11434
nohup ollama serve > ollama.log 2>&1 &

# 验证模型安装
ollama list
```

### 2. 安装 Python 依赖

```bash
cd llmhomework_Backend
pip install -r requirements.txt
```

### 3. 配置设置

在 `app/config.py` 中已预配置了 Qwen2 设置：

```python
# Qwen 模型配置
QWEN_MODEL_NAME = 'qwen3:30B'
QWEN_MODEL_PATH = r'C:\Users\48108\.ollama\models'
USE_QWEN_GRADING = True  # 是否使用 Qwen 进行智能批改
QWEN_MAX_TOKENS = 1000   # Qwen 响应的最大 token 数

# 批改配置
ENABLE_MULTIMODAL = True  # 启用多模态分析
ENABLE_KNOWLEDGE_ANALYSIS = True  # 启用知识点分析
ENABLE_PRACTICE_GENERATION = True  # 启用练习题生成
```

## 使用方法

### 1. 启动系统

使用提供的启动脚本：
```bash
start_with_qwen.bat
```

或手动启动：
```bash
cd llmhomework_Backend
python test_ollama.py  # 测试连接
python run.py          # 启动服务
```

### 2. API 接口

#### 上传试卷图片（支持 AI 批改）
```
POST /upload_image
Content-Type: multipart/form-data

参数：
- file: 试卷图片文件
- use_ai: true/false (是否使用AI批改，默认true)
- user_id: 用户ID (可选)

响应：
{
    "task_id": "任务ID",
    "grading_result": [...],
    "knowledge_analysis": {...},
    "practice_questions": [...],
    "study_suggestions": [...],
    "ai_enabled": true
}
```

#### 查询 AI 服务状态
```
GET /ai_status

响应：
{
    "status": "success",
    "ai_service": {
        "qwen_available": true,
        "model_name": "qwen2:13b",
        "multimodal_enabled": true,
        "knowledge_analysis_enabled": true,
        "practice_generation_enabled": true
    }
}
```

#### 生成练习题
```
POST /generate_practice
Content-Type: application/json

请求体：
{
    "knowledge_points": ["加法运算", "基础计算"],
    "count": 3
}

响应：
{
    "status": "success",
    "practice_questions": [...],
    "generated_count": 3
}
```

## 核心文件说明

### 后端文件结构
```
llmhomework_Backend/
├── app/
│   ├── services/
│   │   ├── qwen_service.py      # Qwen2 服务封装
│   │   ├── grading_qwen.py      # AI 批改引擎
│   │   └── knowledge.py          # 知识点分析（已增强）
│   ├── routes/
│   │   └── upload.py             # 上传路由（已更新）
│   └── config.py                 # 配置文件（已更新）
├── requirements.txt              # 依赖列表（已更新）
└── test_ollama.py               # Oqwen 测试脚本
```

### 关键功能模块

1. **QwenService** (`qwen_service.py`)
   - 与 Oqwen 服务通信
   - 题目类型识别
   - 智能批改
   - 知识点分析
   - 练习题生成

2. **QwenGradingEngine** (`grading_qwen.py`)
   - 批改流程控制
   - 多模态分析
   - 回退机制
   - 结果整合

3. **KnowledgeAnalyzer** (`knowledge.py`)
   - 错题知识点提取
   - 学习建议生成
   - 学习计划制定

## 测试验证

### 1. 基础连接测试
```bash
python test_ollama.py
```

### 2. 完整功能测试
使用前端上传测试图片，观察：
- AI 批改结果的准确性
- 知识点分析的合理性
- 练习题生成的质量

### 3. 性能监控
- 检查 Oqwen 服务资源使用
- 监控批改响应时间
- 观察模型输出质量

## 故障排除

### 常见问题

1. **Oqwen 连接失败**
   - 确保 Oqwen 服务已启动
   - 检查端口 11434 是否可用
   - 验证模型是否正确安装

2. **模型响应缓慢**
   - 检查系统资源（CPU/内存）
   - 调整 QWEN_MAX_TOKENS 参数
   - 考虑使用更小的模型

3. **批改结果不准确**
   - 检查提示词模板
   - 调整温度参数
   - 验证输入数据格式

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看 Oqwen 日志
ollama logs
```

## 性能优化建议

1. **硬件要求**
   - 推荐 16GB+ 内存
   - 支持 CUDA 的 GPU（可选）
   - SSD 存储以提高模型加载速度

2. **配置优化**
   - 调整 temperature 参数控制输出随机性
   - 设置合适的 max_tokens 限制
   - 启用 GPU 加速（如果可用）

3. **缓存策略**
   - 对相同题目类型使用缓存
   - 预加载常用知识点模板
   - 批量处理相似题目

## 扩展功能

### 计划中的增强功能
1. 支持更多题型（证明题、图形题等）
2. 多学科适配（数学、语文、英语等）
3. 个性化学习路径推荐
4. 错题本智能管理
5. 学习进度追踪分析

### 模型升级
- 支持更大的 Qwen2 模型（70B）
- 集成专门的教育领域模型
- 支持多模态模型（图像+文本）

## 技术支持

如遇问题，请检查：
1. Oqwen 服务状态：`ollama list`
2. 模型可用性：`ollama show qwen2:13b`
3. Python 依赖：`pip list`
4. 应用日志：查看控制台输出

---

**注意：首次使用时模型加载可能需要较长时间，请耐心等待。**
