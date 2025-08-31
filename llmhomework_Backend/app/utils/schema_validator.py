import json
import os
from jsonschema import validate, ValidationError
from typing import Dict, List, Any, Optional

class SchemaValidator:
    """JSON Schema验证器"""
    
    def __init__(self):
        self.schema_dir = os.path.join(os.path.dirname(__file__), '../../../Json Schema')
        self._schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载所有Schema文件"""
        schema_files = {
            'ocr_output': 'ocr_output.json',
            'llm_output': 'llm_output.json', 
            'database': 'database_schema.json'
        }
        
        for name, filename in schema_files.items():
            schema_path = os.path.join(self.schema_dir, filename)
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self._schemas[name] = json.load(f)
                    print(f"✅ 加载Schema: {name}")
                except Exception as e:
                    print(f"❌ 加载Schema失败 {name}: {e}")
            else:
                print(f"⚠️ Schema文件不存在: {schema_path}")
    
    def validate_ocr_output(self, data: List[Dict]) -> Dict[str, Any]:
        """验证OCR输出数据"""
        return self._validate_data(data, 'ocr_output', 'OCR输出')
    
    def validate_llm_output(self, data: Dict) -> Dict[str, Any]:
        """验证大模型输出数据"""
        return self._validate_data(data, 'llm_output', '大模型输出')
    
    def validate_database_record(self, data: Dict) -> Dict[str, Any]:
        """验证数据库记录"""
        return self._validate_data(data, 'database', '数据库记录')
    
    def _validate_data(self, data: Any, schema_name: str, data_type: str) -> Dict[str, Any]:
        """通用数据验证方法"""
        if schema_name not in self._schemas:
            return {
                'valid': False,
                'error': f'Schema {schema_name} 未加载',
                'data_type': data_type
            }
        
        try:
            validate(instance=data, schema=self._schemas[schema_name])
            return {
                'valid': True,
                'error': None,
                'data_type': data_type
            }
        except ValidationError as e:
            return {
                'valid': False,
                'error': f'{data_type}格式验证失败: {e.message}',
                'data_type': data_type,
                'validation_path': list(e.path) if e.path else []
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'{data_type}验证异常: {str(e)}',
                'data_type': data_type
            }

# 全局验证器实例
validator = SchemaValidator()

def validate_ocr_output(data: List[Dict]) -> Dict[str, Any]:
    """验证OCR输出"""
    return validator.validate_ocr_output(data)

def validate_llm_output(data: Dict) -> Dict[str, Any]:
    """验证大模型输出"""
    return validator.validate_llm_output(data)

def validate_database_record(data: Dict) -> Dict[str, Any]:
    """验证数据库记录"""
    return validator.validate_database_record(data)
