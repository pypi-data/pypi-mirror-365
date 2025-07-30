from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    """数据库操作接口抽象类"""
    
    @abstractmethod
    def query(self, **kwargs) -> List[Dict]:
        """通用查询方法"""
        pass
    
    @abstractmethod
    def update(self, **kwargs) -> int:
        """通用更新方法"""
        pass
    
    @abstractmethod
    def insert(self, **data) -> Any:
        """通用插入方法"""
        pass
    
    @abstractmethod
    def delete(self, **kwargs) -> int:
        """通用删除方法"""
        pass

    @abstractmethod
    def count(self, **kwargs) -> int:
        """通用计数方法"""
        pass
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """开始事务"""
        pass
    
    @abstractmethod
    def commit_transaction(self) -> None:
        """提交事务"""
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> None:
        """回滚事务"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def query_with_pagination(self, **kwargs) -> List[Dict]:
        """分页查询方法"""
        pass
    
    @abstractmethod
    def query_with_sorting(self, **kwargs) -> List[Dict]:
        """排序查询方法"""
        pass
    
    @abstractmethod
    def batch_insert(self, **kwargs) -> List[Any]:
        """批量插入方法"""
        pass
    
    @abstractmethod
    def batch_update(self, **kwargs) -> int:
        """批量更新方法"""
        pass

    @abstractmethod
    def batch_delete(self, **kwargs) -> int:
        """批量删除方法"""
        pass

    @abstractmethod
    def exists(self, **kwargs) -> bool:
        """检查记录是否存在"""
        pass
    
    @abstractmethod
    def get_field_values(
        self, 
        collection: str, 
        field: str, 
        conditions: Dict = None,
        distinct: bool = False
    ) -> List[Any]:
        """获取指定字段的值列表"""
        pass