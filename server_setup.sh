#!/bin/bash
# 服务器端Ollama配置脚本
# 在服务器172.31.179.77上运行此脚本

echo "配置Ollama API服务..."

# 1. 确保Ollama服务运行并监听所有接口
export OLLAMA_HOST=0.0.0.0:11434

# 2. 启动Ollama服务（后台运行）
nohup ollama serve > ollama.log 2>&1 &

# 3. 等待服务启动
sleep 5

# 4. 验证qwen3:30B模型是否存在
echo "检查qwen3:30B模型..."
ollama list | grep qwen3:30B

if [ $? -eq 0 ]; then
    echo "qwen3:30B模型已就绪"
else
    echo "警告：qwen3:30B模型未找到，请确保已下载"
fi

# 5. 测试API接口
echo "测试API接口..."
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:30B",
    "prompt": "你好，这是一个测试",
    "stream": false
  }'

echo ""
echo "Ollama API服务配置完成！"
echo "服务地址: http://172.31.179.77:11434"
echo "请确保防火墙开放11434端口"
