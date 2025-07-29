from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class CustomSQLInterface(ABC):
    """自定义SQL执行接口
    
    该接口用于标识数据库实现层支持自定义SQL执行，包括DDL和DML操作。
    实现此接口的类可以执行原生SQL语句，提供更灵活的数据库操作能力。
    """
    
    @abstractmethod
    def execute_custom_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义SQL查询语句（DML）
        
        Args:
            sql: 要执行的SQL语句
            params: SQL参数元组，用于参数化查询
            
        Returns:
            查询结果列表，每个元素是一个字典，键为列名，值为对应的数据
            
        Raises:
            Exception: 当SQL执行失败时抛出异常
        """
        pass
    
    @abstractmethod
    def execute_custom_update(self, sql: str, params: tuple = None) -> int:
        """执行自定义更新语句（DML/DDL）
        
        Args:
            sql: 要执行的SQL语句（UPDATE, INSERT, DELETE, DDL等）
            params: SQL参数元组，用于参数化查询
            
        Returns:
            受影响的行数（对于DML语句）或0（对于DDL语句）
            
        Raises:
            Exception: 当SQL执行失败时抛出异常
        """
        pass
    
    def is_custom_sql_supported(self) -> bool:
        """检查是否支持自定义SQL执行
        
        Returns:
            始终返回True，表示支持自定义SQL执行
        """
        return True