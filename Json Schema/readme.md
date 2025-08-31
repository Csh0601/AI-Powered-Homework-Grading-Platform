# JSON Schema 使用说明

## 概述
本项目使用JSON Schema来规范不同模块间的数据交换格式，确保数据一致性和系统稳定性。

## Schema文件说明

### 1. `ocr_output.json`
**用途**: 定义OCR模块输出的数据格式  
**使用者**: C同学（OCR开发）→ B同学（后端）  
**验证位置**: `app/services/ocr_engine.py`中的`smart_extract_questions()`

### 2. `llm_output.json`  
**用途**: 定义大模型批改结果的数据格式  
**使用者**: A同学（大模型）→ B同学（后端）→ C同学（前端）  
**验证位置**: `app/services/grading_new.py`中的`grade_homework_improved()`

### 3. `database_schema.json`
**用途**: 定义数据库存储记录的数据格式  
**使用者**: B同学（后端数据存储）  
**验证位置**: `app/models/record.py`中的`save_record()`

## 使用方法

### 安装依赖
```bash
pip install jsonschema
```

### 在代码中使用
```python
from app.utils.schema_validator import validate_ocr_output, validate_llm_output, validate_database_record

# 验证OCR输出
validation = validate_ocr_output(ocr_data)
if not validation['valid']:
    print(f"验证失败: {validation['error']}")

# 验证大模型输出  
validation = validate_llm_output(llm_data)
if not validation['valid']:
    print(f"验证失败: {validation['error']}")

# 验证数据库记录
validation = validate_database_record(record_data)
if not validation['valid']:
    print(f"验证失败: {validation['error']}")
```

## 数据流程

```
C(OCR) → ocr_output.json → B(后端) → database_schema.json 
                                ↓
A(大模型) ← llm_output.json ← B(后端) → C(前端)
```

## 验证结果

当运行项目时，你会在控制台看到以下验证信息：
- ✅ OCR输出格式验证通过
- ✅ 大模型输出格式验证通过  
- ✅ 数据库记录格式验证通过
- ⚠️ 格式验证失败: [具体错误信息]

## 注意事项

1. **向后兼容**: 当前实现保持了向后兼容性，验证失败不会中断程序运行
2. **错误处理**: 可以根据需要调整验证失败时的处理策略
3. **Schema更新**: 修改Schema后需要同步更新相关代码
4. **团队协作**: 所有成员都应该遵循Schema定义的数据格式

## 团队分工

- **A同学（大模型）**: 确保输出符合`llm_output.json`格式
- **B同学（后端）**: 维护所有Schema，处理数据验证和存储
- **C同学（OCR+前端）**: 确保OCR输出符合`ocr_output.json`格式，前端正确解析数据
