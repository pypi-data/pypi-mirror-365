from typing import Dict, Any, Optional, List
from xianbao.core.ProcessQueueInterface import ProcessQueueInterface, ProcessQueueBase
from xianbao.core.BlockDeque import SQLiteProcessQueue
from xianbao.core.HttpSQLiteProcessQueue import HttpSQLiteProcessQueue


class QueueFactory:
    """
    队列工厂类，负责创建和管理各种队列实现
    
    提供统一的接口来创建不同类型的进程安全队列，
    支持SQLite本地队列和HTTP远程队列等多种实现。
    """
    
    # 支持的队列类型
    QUEUE_TYPES = {
        'sqlite': SQLiteProcessQueue,
        'http': HttpSQLiteProcessQueue,
        'http_lock': HttpSQLiteProcessQueue,
    }
    
    @classmethod
    def create_queue(cls, 
                    queue_type: str = 'sqlite',
                    **kwargs) -> ProcessQueueInterface:
        """
        创建指定类型的队列实例
        
        Args:
            queue_type: 队列类型，支持 'sqlite', 'http', 'http_lock'
            **kwargs: 传递给具体队列实现的参数
            
        Returns:
            队列实例
            
        Raises:
            ValueError: 当指定的队列类型不支持时
        """
        if queue_type not in cls.QUEUE_TYPES:
            raise ValueError(
                f"不支持的队列类型: {queue_type}. "
                f"支持的类型: {list(cls.QUEUE_TYPES.keys())}"
            )
        
        queue_class = cls.QUEUE_TYPES[queue_type]
        
        # 根据队列类型处理特定参数
        if queue_type == 'sqlite':
            return cls._create_sqlite_queue(**kwargs)
        elif queue_type == 'http':
            kwargs.pop('use_lock', None)  # 移除可能冲突的参数
            return cls._create_http_queue(use_lock=False, **kwargs)
        elif queue_type == 'http_lock':
            kwargs.pop('use_lock', None)  # 移除可能冲突的参数
            return cls._create_http_queue(use_lock=True, **kwargs)
    
    @classmethod
    def _create_sqlite_queue(cls, **kwargs) -> SQLiteProcessQueue:
        """创建SQLite本地队列"""
        # 设置SQLite队列的默认参数
        sqlite_defaults = {
            'db_path': 'rpa_ztdb.db',
            'table_name': 'queue',
            'max_size': 10000,
            'timeout': 30.0,
            'lock_path': 'rpa_queue',
            'journal_mode': 'WAL',
            'busy_timeout': 5000,
            'poll_interval': 0.1,
            'max_poll_interval': 1.0
        }
        
        # 合并用户参数和默认参数
        config = {**sqlite_defaults, **kwargs}
        return SQLiteProcessQueue(**config)
    
    @classmethod
    def _create_http_queue(cls, use_lock: bool = False, **kwargs) -> HttpSQLiteProcessQueue:
        """创建HTTP远程队列"""
        # 设置HTTP队列的默认参数
        http_defaults = {
            'base_url': 'http://localhost:5000',
            'table_name': 'http_queue',
            'max_size': 10000,
            'timeout': 30.0
        }
        
        # 合并用户参数和默认参数
        config = {**http_defaults, **kwargs}
        config['use_lock'] = use_lock
        return HttpSQLiteProcessQueue(**config)
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """获取支持的队列类型列表"""
        return list(cls.QUEUE_TYPES.keys())
    
    @classmethod
    def get_default_config(cls, queue_type: str) -> Dict[str, Any]:
        """
        获取指定队列类型的默认配置
        
        Args:
            queue_type: 队列类型
            
        Returns:
            默认配置字典
            
        Raises:
            ValueError: 当指定的队列类型不支持时
        """
        if queue_type not in cls.QUEUE_TYPES:
            raise ValueError(f"不支持的队列类型: {queue_type}")
        
        if queue_type == 'sqlite':
            return {
                'db_path': 'rpa_ztdb.db',
                'table_name': 'queue',
                'max_size': 10000,
                'timeout': 30.0,
                'lock_path': 'rpa_queue',
                'journal_mode': 'WAL',
                'busy_timeout': 5000,
                'poll_interval': 0.1,
                'max_poll_interval': 1.0
            }
        elif queue_type in ['http', 'http_lock']:
            return {
                'base_url': 'http://localhost:5000',
                'table_name': 'http_queue',
                'max_size': 10000,
                'timeout': 30.0,
                'use_lock': queue_type == 'http_lock'
            }


class QueueConfigBuilder:
    """
    队列配置构建器，用于简化队列配置的创建
    """
    
    def __init__(self, queue_type: str):
        """
        初始化配置构建器
        
        Args:
            queue_type: 队列类型
        """
        self.queue_type = queue_type
        self.config = {}
    
    def with_db_path(self, db_path: str) -> 'QueueConfigBuilder':
        """设置数据库路径（仅SQLite队列）"""
        self.config['db_path'] = db_path
        return self
    
    def with_base_url(self, base_url: str) -> 'QueueConfigBuilder':
        """设置HTTP服务基础URL（仅HTTP队列）"""
        self.config['base_url'] = base_url
        return self
    
    def with_table_name(self, table_name: str) -> 'QueueConfigBuilder':
        """设置队列表名"""
        self.config['table_name'] = table_name
        return self
    
    def with_max_size(self, max_size: int) -> 'QueueConfigBuilder':
        """设置队列最大容量"""
        self.config['max_size'] = max_size
        return self
    
    def with_timeout(self, timeout: float) -> 'QueueConfigBuilder':
        """设置操作超时时间"""
        self.config['timeout'] = timeout
        return self
    
    def with_use_lock(self, use_lock: bool) -> 'QueueConfigBuilder':
        """设置是否使用锁模式（仅HTTP队列）"""
        self.config['use_lock'] = use_lock
        return self
    
    def build(self) -> ProcessQueueInterface:
        """根据配置创建队列实例"""
        return QueueFactory.create_queue(self.queue_type, **self.config)
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置字典"""
        return self.config.copy()


class QueueManager:
    """
    队列管理器，提供队列的集中管理和监控
    """
    
    def __init__(self):
        """初始化队列管理器"""
        self._queues: Dict[str, ProcessQueueInterface] = {}
    
    def create_and_register(self, 
                         name: str,
                         queue_type: str,
                         **kwargs) -> ProcessQueueInterface:
        """
        创建并注册队列实例
        
        Args:
            name: 队列名称（用于后续管理）
            queue_type: 队列类型
            **kwargs: 队列参数
            
        Returns:
            创建的队列实例
        """
        if name in self._queues:
            raise ValueError(f"队列名称已存在: {name}")
        
        queue = QueueFactory.create_queue(queue_type, **kwargs)
        self._queues[name] = queue
        return queue
    
    def get_queue(self, name: str) -> Optional[ProcessQueueInterface]:
        """获取已注册的队列实例"""
        return self._queues.get(name)
    
    def remove_queue(self, name: str) -> bool:
        """移除并关闭队列实例"""
        if name in self._queues:
            queue = self._queues.pop(name)
            queue.close()
            return True
        return False
    
    def list_queues(self) -> List[str]:
        """获取所有已注册的队列名称"""
        return list(self._queues.keys())
    
    def close_all(self):
        """关闭所有已注册的队列"""
        for name, queue in self._queues.items():
            queue.close()
        self._queues.clear()
    
    def get_queue_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取队列的基本信息"""
        queue = self.get_queue(name)
        if queue is None:
            return None
        
        return {
            'name': name,
            'type': type(queue).__name__,
            'size': queue.qsize(),
            'empty': queue.empty(),
            'full': queue.full()
        }
    
    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有队列的信息"""
        return {
            name: self.get_queue_info(name)
            for name in self.list_queues()
        }