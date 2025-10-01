# FastAPI服务器对话端点实现指南

## 📋 服务器信息

**地址**: 172.31.179.77:8007  
**框架**: FastAPI (异步框架)  
**项目路径**: `/home/cshcsh/rag知识系统`  
**主文件**: 需要确认 (通常是 `main.py` 或 `app.py`)

---

## 🎯 实施步骤

### 步骤 1: 登录服务器并定位文件

```bash
# 1. SSH登录
ssh cshcsh@172.31.179.77

# 2. 进入项目目录
cd /home/cshcsh/rag知识系统

# 3. 查找FastAPI主文件
ls -la *.py

# 4. 查找可能的文件
find . -maxdepth 2 -name "*.py" -type f | grep -E "(main|app|server)"
```

---

### 步骤 2: 添加Pydantic模型定义

在FastAPI主文件中添加以下内容（通常在文件开头的导入后）：

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time

# ============================================
# 对话功能的数据模型
# ============================================

class ChatMessage(BaseModel):
    """单条聊天消息"""
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")

class GradingSummary(BaseModel):
    """批改摘要"""
    total_questions: int = Field(0, description="总题数")
    correct_count: int = Field(0, description="正确题数")
    accuracy_rate: float = Field(0.0, description="正确率")

class GradingResultItem(BaseModel):
    """单个批改结果"""
    question: str = Field("", description="题目内容")
    answer: str = Field("", description="学生答案")
    correct_answer: str = Field("", description="正确答案")
    correct: bool = Field(False, description="是否正确")
    explanation: str = Field("", description="批改说明")

class GradingContext(BaseModel):
    """批改上下文"""
    summary: Optional[GradingSummary] = None
    grading_result: List[GradingResultItem] = Field(default_factory=list)
    wrong_knowledges: List[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    """对话请求模型"""
    task_id: str = Field(..., description="任务ID")
    conversation_history: List[ChatMessage] = Field(..., description="对话历史")
    grading_context: GradingContext = Field(..., description="批改上下文")

class ChatResponse(BaseModel):
    """对话响应模型"""
    success: bool = Field(True, description="是否成功")
    response: str = Field("", description="AI回复内容")
    context_used: bool = Field(True, description="是否使用了上下文")
    timestamp: int = Field(..., description="时间戳")
    error: Optional[str] = Field(None, description="错误信息")
```

---

### 步骤 3: 添加对话端点

在FastAPI应用中添加以下路由：

```python
# ============================================
# 对话端点实现
# ============================================

@app.post("/chat", response_model=ChatResponse)
async def chat_with_context(request: ChatRequest):
    """
    带上下文的对话接口
    支持基于批改结果的智能对话
    """
    try:
        print(f"\n{'='*60}")
        print(f"💬 [对话] 收到对话请求")
        print(f"   任务ID: {request.task_id}")
        print(f"   历史消息数: {len(request.conversation_history)}")
        print(f"   批改上下文: 已提供")
        print(f"{'='*60}\n")
        
        # 1. 构建系统提示词
        system_prompt = build_chat_system_prompt(request.grading_context)
        
        # 2. 构建完整对话消息
        messages = []
        
        # 添加系统角色
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 添加对话历史（最近20轮）
        recent_history = request.conversation_history[-20:] if len(request.conversation_history) > 20 else request.conversation_history
        for msg in recent_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        print(f"📝 构建对话上下文: {len(messages)} 条消息")
        
        # 3. 调用模型生成回复
        response_text = await generate_chat_response(messages)
        
        print(f"✅ [对话] 生成回复成功，长度: {len(response_text)}")
        
        return ChatResponse(
            success=True,
            response=response_text,
            context_used=True,
            timestamp=int(time.time()),
            error=None
        )
        
    except Exception as e:
        print(f"❌ [对话] 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return ChatResponse(
            success=False,
            response="",
            context_used=False,
            timestamp=int(time.time()),
            error=str(e)
        )


def build_chat_system_prompt(grading_context: GradingContext) -> str:
    """
    构建包含批改信息的系统提示词
    """
    # 提取批改信息
    summary = grading_context.summary
    total_questions = summary.total_questions if summary else 0
    correct_count = summary.correct_count if summary else 0
    accuracy_rate = summary.accuracy_rate if summary else 0
    
    grading_results = grading_context.grading_result
    wrong_knowledges = grading_context.wrong_knowledges
    
    # 构建系统提示词
    prompt = f"""你是一个专业的AI学习伙伴，刚刚批改了学生的作业。以下是批改结果：

【批改概况】
- 总题数：{total_questions}题
- 正确题数：{correct_count}题
- 正确率：{accuracy_rate*100:.1f}%

"""
    
    # 添加错题详情
    if grading_results:
        wrong_questions = [r for r in grading_results if not r.correct]
        if wrong_questions:
            prompt += "【错题详情】\n"
            for i, q in enumerate(wrong_questions[:5], 1):  # 最多显示5道
                prompt += f"{i}. 题目：{q.question[:100]}...\n"
                prompt += f"   学生答案：{q.answer}\n"
                prompt += f"   正确答案：{q.correct_answer}\n"
                prompt += f"   错误原因：{q.explanation[:150]}...\n\n"
    
    # 添加薄弱知识点
    if wrong_knowledges:
        prompt += "【薄弱知识点】\n"
        for kp in wrong_knowledges[:10]:
            prompt += f"- {kp}\n"
        prompt += "\n"
    
    prompt += """【你的任务】
1. 基于上述批改结果回答学生的问题
2. 提供针对性的学习建议和解题思路
3. 解释错误原因，帮助学生理解知识点
4. 语言要友好、耐心、鼓励性
5. 回答要具体、清晰、有帮助

请开始对话吧！"""
    
    return prompt


async def generate_chat_response(messages: List[Dict]) -> str:
    """
    使用模型生成对话回复（异步版本）
    
    Args:
        messages: 对话消息列表
        
    Returns:
        AI回复内容
    """
    try:
        # 格式化消息为文本
        conversation_text = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                conversation_text += f"System: {content}\n\n"
            elif role == 'user':
                conversation_text += f"User: {content}\n\n"
            elif role == 'assistant':
                conversation_text += f"Assistant: {content}\n\n"
        
        conversation_text += "Assistant: "
        
        print(f"📤 发送对话到模型...")
        
        # 使用tokenizer处理
        inputs = tokenizer(
            conversation_text,
            return_tensors="pt",
            truncation=True,
            max_length=4096  # 对话模式使用较短的上下文
        ).to(model.device)
        
        # 对话生成参数（更自然的对话）
        generation_config = {
            "max_new_tokens": 512,        # 对话回复较短
            "temperature": 0.7,           # 增加创造性
            "top_p": 0.9,                 # 核采样
            "top_k": 50,
            "do_sample": True,            # 启用采样
            "repetition_penalty": 1.1,    # 避免重复
            "pad_token_id": tokenizer.pad_token_id,
            "eos_token_id": tokenizer.eos_token_id,
        }
        
        # 生成回复（同步调用，但在async函数中）
        import torch
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                **generation_config
            )
        
        # 解码
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取助手回复
        if "Assistant: " in full_response:
            parts = full_response.split("Assistant: ")
            response = parts[-1].strip()
        else:
            response = full_response.strip()
        
        # 清理响应
        response = response.replace("User:", "").strip()
        
        print(f"✅ 生成回复完成")
        
        return response
        
    except Exception as e:
        print(f"❌ 生成回复失败: {str(e)}")
        return "抱歉，我在思考时遇到了一些问题。能否换个方式问我呢？"
```

---

### 步骤 4: 确认必要的导入和变量

确保文件顶部有以下导入：

```python
import torch
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
```

确认全局变量已定义：

```python
# 应该在文件中已有这些变量
tokenizer = ...  # AutoTokenizer实例
model = ...      # 模型实例
app = FastAPI()  # FastAPI应用实例
```

---

### 步骤 5: 重启FastAPI服务

```bash
# 1. 查找FastAPI进程
ps aux | grep -E "(uvicorn|fastapi|python.*main\.py)"

# 2. 停止旧进程
pkill -f "uvicorn\|python.*main\.py"

# 3. 重新启动服务（根据实际启动方式）
# 方式A: 使用uvicorn
nohup uvicorn main:app --host 0.0.0.0 --port 8007 > fastapi.log 2>&1 &

# 方式B: 直接运行Python文件
nohup python3 main.py > fastapi.log 2>&1 &

# 4. 验证服务启动
ps aux | grep python
netstat -tlnp | grep 8007

# 5. 查看日志
tail -f fastapi.log
```

---

### 步骤 6: 测试对话端点

```bash
# 使用curl测试
curl -X POST http://172.31.179.77:8007/chat \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test_123",
    "conversation_history": [
      {
        "role": "user",
        "content": "为什么我的第一题错了？"
      }
    ],
    "grading_context": {
      "summary": {
        "total_questions": 5,
        "correct_count": 3,
        "accuracy_rate": 0.6
      },
      "grading_result": [
        {
          "question": "1+1=?",
          "answer": "3",
          "correct_answer": "2",
          "correct": false,
          "explanation": "基本算术错误"
        }
      ],
      "wrong_knowledges": ["基础加法"]
    }
  }'
```

**预期返回**：
```json
{
  "success": true,
  "response": "第一题你答错了是因为...",
  "context_used": true,
  "timestamp": 1234567890,
  "error": null
}
```

---

## 🔍 关键差异：Flask vs FastAPI

### Flask版本（旧）
```python
@app.route('/chat', methods=['POST'])
def chat_with_context():
    data = request.get_json()
    # ... 同步处理
    return jsonify(result)
```

### FastAPI版本（新）
```python
@app.post("/chat", response_model=ChatResponse)
async def chat_with_context(request: ChatRequest):
    # ... 异步处理
    return ChatResponse(...)
```

### 主要变化
1. ✅ **装饰器**: `@app.route` → `@app.post`
2. ✅ **参数**: `request.get_json()` → 直接使用Pydantic模型
3. ✅ **返回**: `jsonify()` → 直接返回Pydantic模型
4. ✅ **异步**: 支持 `async def`
5. ✅ **类型验证**: 自动验证请求格式

---

## 🐛 故障排除

### 问题1: Pydantic验证错误
```bash
# 检查请求格式是否符合模型定义
# 查看日志中的详细错误信息
tail -100 fastapi.log
```

### 问题2: tokenizer未定义
```python
# 确保在文件中已加载模型
tokenizer = AutoTokenizer.from_pretrained(...)
model = AutoModel.from_pretrained(...)
```

### 问题3: 端口被占用
```bash
# 查找占用8007端口的进程
lsof -i :8007
# 或
netstat -tlnp | grep 8007
```

### 问题4: GPU内存不足
```python
# 减少max_new_tokens
"max_new_tokens": 256,  # 从512减少到256
```

---

## ✅ 完成后验证

1. ✅ FastAPI服务在8007端口运行
2. ✅ `/chat` 端点返回200状态码
3. ✅ 响应格式符合ChatResponse模型
4. ✅ success字段为true
5. ✅ response字段包含AI回复
6. ✅ 日志无错误

---

## 📊 本地后端已适配

本地后端(`chat_service.py`)已更新为：
- ✅ 发送FastAPI格式的请求
- ✅ 解析FastAPI格式的响应
- ✅ 处理success字段
- ✅ 提取response内容
- ✅ 错误处理和降级响应

---

## 🎯 完整的数据流

```
前端ChatScreen
    ↓
本地后端 POST /api/chat/message
    ↓
chat_service._call_server_api()
    ↓
POST http://172.31.179.77:8007/chat
    ↓
FastAPI服务器
    ↓
build_chat_system_prompt() + generate_chat_response()
    ↓
返回 ChatResponse(success=True, response="AI回复")
    ↓
本地后端提取 result['response']
    ↓
返回给前端
    ↓
ChatScreen显示AI消息
```

---

**改造难度**: ⭐⭐⭐☆☆ (中等)  
**风险等级**: 🟢 低  
**预期效果**: 🚀 完整的AI对话功能

完成后即可使用完整的AI学习伙伴功能！🎉
