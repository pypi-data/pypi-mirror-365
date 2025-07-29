import numpy as np
import pandas as pd
import datetime
from decimal import Decimal
import base64
import json

def json_serializer(obj):
    """将常见非标准Python类型转换为JSON可序列化格式"""
    if isinstance(obj, (np.integer, np.int_)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float_)):
        return float(obj)
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()  # 转换数组为列表
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()  # 转换时间戳为ISO字符串
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)  # 或 str(obj) 根据需求
    elif isinstance(obj, bytes):
        # 处理bytes类型数据
        return base64.b64encode(obj).decode('utf-8')
    elif hasattr(obj, 'to_dict'):
        # 支持Pandas DataFrame等可转换为字典的对象
        return obj.to_dict()
    elif hasattr(obj, 'to_json'):
        # 支持直接转换为JSON的对象
        return json.loads(obj.to_json())
    elif isinstance(obj, pd.DataFrame):
        # DataFrame特殊处理
        return obj.to_dict(orient='records')
    
    # 对于其他类型，可以添加更多处理，或者抛出异常
    raise TypeError(f"类型 {type(obj)} 不可JSON序列化")

def convert_payload(payload):
    """递归转换payload中的所有元素为JSON兼容类型"""
    if isinstance(payload, (list, tuple)):
        return [convert_payload(item) for item in payload]
    elif isinstance(payload, dict):
        return {k: convert_payload(v) for k, v in payload.items()}
    else:
        try:
            # 尝试直接序列化Python原生类型
            json.dumps(payload)
            return payload
        except TypeError:
            # 使用自定义序列化器处理复杂类型
            return json_serializer(payload)