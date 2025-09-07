#!/usr/bin/env python3
"""
API响应辅助函数
统一API响应格式
"""

from flask import jsonify
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

def success_response(data: Any = None, message: str = "操作成功", code: int = 200) -> Dict:
    """
    成功响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
        
    Returns:
        统一格式的响应
    """
    response = {
        "code": code,
        "message": message,
        "success": True,
        "data": data
    }
    
    return jsonify(response)

def error_response(message: str = "操作失败", code: int = 400, error_code: Optional[str] = None, details: Any = None) -> Dict:
    """
    错误响应格式
    
    Args:
        message: 错误消息
        code: HTTP状态码
        error_code: 业务错误码
        details: 错误详情
        
    Returns:
        统一格式的错误响应
    """
    response = {
        "code": code,
        "message": message,
        "success": False,
        "error": {
            "error_code": error_code,
            "details": details
        }
    }
    
    # 记录错误日志
    if code >= 500:
        logger.error(f"服务器错误: {message}, 详情: {details}")
    elif code >= 400:
        logger.warning(f"客户端错误: {message}, 详情: {details}")
    
    return jsonify(response), code

def paginated_response(data: list, total: int, page: int = 1, page_size: int = 20, message: str = "查询成功") -> Dict:
    """
    分页响应格式
    
    Args:
        data: 当前页数据
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
        
    Returns:
        分页格式的响应
    """
    total_pages = (total + page_size - 1) // page_size
    
    response = {
        "code": 200,
        "message": message,
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return jsonify(response)

def validate_request(request_data: dict, required_fields: list, optional_fields: list = None) -> tuple:
    """
    请求数据验证
    
    Args:
        request_data: 请求数据
        required_fields: 必需字段列表
        optional_fields: 可选字段列表
        
    Returns:
        (is_valid, error_message, validated_data)
    """
    if not isinstance(request_data, dict):
        return False, "请求数据格式错误", None
    
    # 检查必需字段
    missing_fields = []
    for field in required_fields:
        if field not in request_data or request_data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}", None
    
    # 提取有效数据
    validated_data = {}
    all_fields = required_fields + (optional_fields or [])
    
    for field in all_fields:
        if field in request_data:
            validated_data[field] = request_data[field]
    
    return True, None, validated_data