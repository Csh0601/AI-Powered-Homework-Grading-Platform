# OCR作业批改系统部署指南

## 环境要求
- Python 3.8+
- Node.js 16+
- Expo CLI

## 后端部署

### 1. 安装Python依赖
```bash
cd llmhomework_Backend
pip install -r requirements.txt
```

### 2. OCR引擎选择
系统支持多种OCR引擎，按优先级自动降级：

#### PaddleOCR (推荐)
```bash
pip install paddlepaddle paddleocr
```

#### EasyOCR (备选)
```bash
pip install easyocr
```

#### Tesseract (备选)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang

# Windows
# 下载并安装: https://github.com/UB-Mannheim/tesseract/wiki

pip install pytesseract
```

#### LaTeX OCR (数学公式，可选)
```bash
pip install git+https://github.com/lukas-blecher/LaTeX-OCR.git
```

### 3. 启动后端服务
```bash
python run.py
```
默认运行在 `http://localhost:5000`

## 前端部署

### 1. 安装依赖
```bash
cd llmhomework_Frontend
npm install
```

 
```

### 3. 启动前端
```bash
npx expo start
```

## 网络配置

### 开发环境
1. 确保前后端在同一网络
2. 后端需要绑定到 `0.0.0.0:5000` 而不是 `127.0.0.1:5000`
3. 前端配置后端的实际IP地址

### 生产环境
1. 配置防火墙开放5000端口
2. 考虑使用反向代理（nginx）
3. 配置HTTPS（推荐）

## 性能优化

### OCR性能
- PaddleOCR: 中文识别效果最好，但占用资源较多
- EasyOCR: 平衡性能和效果
- Tesseract: 最轻量，但中文效果一般

### 图像预处理
- 自动调整图像大小和对比度
- 支持图像旋转和裁剪
- 建议图像分辨率不超过2048x2048

## 故障排除

### OCR识别失败
1. 检查OCR引擎是否正确安装
2. 确保图像清晰且包含文字
3. 查看后端日志获取详细错误信息

### 网络连接问题
1. 检查IP地址配置
2. 确认防火墙设置
3. 验证端口是否被占用

### 内存不足
1. 减少图像分辨率
2. 只安装一种OCR引擎
3. 增加系统内存

## 日志和调试

### 后端日志
- 启动时会显示可用的OCR引擎
- 每次识别会输出详细的处理步骤
- 错误会包含具体的异常信息

### 前端调试
- 使用Expo开发工具
- 检查网络请求状态
- 查看控制台错误信息
