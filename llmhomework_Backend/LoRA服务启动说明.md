# LoRA服务启动说明

## 🎯 概述

本地项目已配置为使用训练后的LoRA模型 (`qwen_vl_lora`)，并集成了自动启动LoRA服务的功能。

## 📋 配置修改总结

### 1. 配置文件修改
- `app/config.py`: `LLM_PROVIDER = 'qwen_vl_lora'`
- `app/services/huggingface_service.py`: 默认值更新为 `qwen_vl_lora`

### 2. 自动启动功能
- `run.py`: 集成了 `ensure_lora_service_running()` 函数
- 启动后端时会自动检查并启动LoRA服务

## 🚀 启动方式

### 方式一：自动启动（推荐）
直接启动后端，系统会自动启动LoRA服务：
```bash
python run.py
```

### 方式二：手动启动LoRA服务
如果需要单独启动LoRA服务：
```bash
python start_lora_service.py
```

### 方式三：一键启动（包含LoRA服务）
使用一键启动脚本：
```bash
python start_backend_with_lora.py
```

### 方式四：批处理文件启动
Windows用户可以使用批处理文件：
```bash
# 启动LoRA服务
start_lora_service.bat

# 一键启动后端（包含LoRA服务）
start_backend_with_lora.bat
```

## ⚙️ SSH配置要求

自动启动功能需要SSH连接，请确保：

1. **SSH密钥配置**（推荐）：
   ```bash
   # 生成SSH密钥
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   
   # 复制公钥到服务器
   ssh-copy-id cshcsh@172.31.179.77
   ```

2. **或者使用SSH密码认证**：
   - 确保SSH客户端已安装
   - 配置SSH客户端使用密码认证

## 🔧 故障排除

### SSH连接失败
如果SSH连接失败，可以手动启动LoRA服务：

1. **SSH登录服务器**：
   ```bash
   ssh cshcsh@172.31.179.77
   ```

2. **启动LoRA服务**：
   ```bash
   cd /home/cshcsh/rag知识系统
   python3 auto_start_lora.py
   ```

3. **检查服务状态**：
   ```bash
   curl http://172.31.179.77:8007/health
   ```

### 服务启动失败
如果LoRA服务启动失败：

1. **检查服务器资源**：
   - 确保服务器有足够的内存和GPU资源
   - 检查是否有其他进程占用端口8007

2. **查看日志**：
   ```bash
   # 查看LoRA服务日志
   tail -f /tmp/qwen_vl_lora_auto.log
   ```

3. **重启服务**：
   ```bash
   # 停止现有服务
   pkill -f qwen_vl_lora.py
   
   # 重新启动
   python3 auto_start_lora.py
   ```

## 📊 服务状态检查

### 健康检查
```bash
curl http://172.31.179.77:8007/health
```

### 本地测试
```bash
# 测试本地后端连接
curl http://127.0.0.1:5000/health/multimodal
```

## 🎯 使用流程

1. **启动LoRA服务**（自动或手动）
2. **启动本地后端**：`python run.py`
3. **启动前端应用**
4. **测试图片上传功能**

## 📝 注意事项

1. **首次启动**：LoRA服务首次启动需要1-2分钟加载模型
2. **资源要求**：确保服务器有足够的GPU内存
3. **网络连接**：确保本地与服务器网络连接正常
4. **SSH配置**：建议配置SSH密钥认证以提高安全性

## 🔄 更新日志

- **2024-01-XX**: 集成LoRA服务自动启动功能
- **2024-01-XX**: 修改配置使用训练后的LoRA模型
- **2024-01-XX**: 添加多种启动方式支持
