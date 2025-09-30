# AI Homework Backend

## 项目简介
本项目为作业自动批改后端，支持图片上传、OCR识别、自动判题、错题分析、题目生成等功能，支持与前端联调。

## 依赖安装
```bash
pip install -r requirements.txt
```

## 运行方式
```bash
python run.py
```

> 注意：启动前会自动禁用 Flash Attention / Triton，以避免 `wrap_triton` 相关报错。

## 主要接口
- `POST /upload_image`：上传作业图片，返回结构化批改结果
- `GET /get_results`：获取历史批改记录
- `POST /generate_exercise`：根据知识点生成新题

## 前后端联调
前端通过上述接口与后端交互，数据格式为 JSON，图片通过 multipart/form-data 上传。

## 目录结构
- app/ 业务代码
- uploads/ 图片存储
- run.py 启动入口
- requirements.txt 依赖
