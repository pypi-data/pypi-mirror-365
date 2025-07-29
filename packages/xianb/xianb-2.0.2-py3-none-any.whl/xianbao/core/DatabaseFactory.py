from typing import Dict, Any, Optional
from xianbao.core.DatabaseInterface import DatabaseInterface
from xianbao.core.SQLiteDatabase import SQLiteDatabase
from xianbao.core.HttpSQLiteDatabase import HttpSQLiteDatabase


class DatabaseFactory:
    """数据库工厂类 - 用于创建和管理数据库实例
    
    提供统一的数据库实例创建接口，支持多种数据库类型和配置。
    实现了单例模式，确保同一配置的数据库实例只创建一次。
    """
    
    _instances: Dict[str, DatabaseInterface] = {}
    
    DATABASE_TYPES = {
        'sqlite': SQLiteDatabase,
        'http_sqlite': HttpSQLiteDatabase,
    }
    
    @classmethod
    def create_database(
        cls,
        db_type: str = 'sqlite',
        config: Optional[Dict[str, Any]] = None
    ) -> DatabaseInterface:
        """创建数据库实例
        
        Args:
            db_type: 数据库类型，支持 'sqlite' 和 'http_sqlite'
            config: 数据库配置字典，包含连接参数
            
        Returns:
            数据库接口实例
            
        Raises:
            ValueError: 当数据库类型不支持时抛出
        """
        if db_type not in cls.DATABASE_TYPES:
            raise ValueError(
                f"不支持的数据库类型: {db_type}. "
                f"支持的类型: {list(cls.DATABASE_TYPES.keys())}"
            )
        
        # 生成实例标识符
        instance_key = cls._generate_instance_key(db_type, config or {})
        
        # 检查是否已存在实例
        if instance_key in cls._instances:
            return cls._instances[instance_key]
        
        # 创建新实例
        database_class = cls.DATABASE_TYPES[db_type]
        
        if db_type == 'sqlite':
            instance = cls._create_sqlite_database(config or {})
        elif db_type == 'http_sqlite':
            instance = cls._create_http_sqlite_database(config or {})
        else:
            raise ValueError(f"未知的数据库类型: {db_type}")
        
        # 缓存实例
        cls._instances[instance_key] = instance
        return instance
    
    @classmethod
    def _create_sqlite_database(cls, config: Dict[str, Any]) -> SQLiteDatabase:
        """创建SQLite数据库实例"""
        db_path = config.get('db_path', 'rpa_ztdb.db')
        return SQLiteDatabase(db_path)
    
    @classmethod
    def _create_http_sqlite_database(cls, config: Dict[str, Any]) -> HttpSQLiteDatabase:
        """创建HTTP SQLite数据库实例"""
        base_url = config.get('base_url', 'http://localhost:5000')
        use_lock = config.get('use_lock', False)
        return HttpSQLiteDatabase(base_url, use_lock)
    
    @classmethod
    def _generate_instance_key(cls, db_type: str, config: Dict[str, Any]) -> str:
        """生成实例标识符
        
        Args:
            db_type: 数据库类型
            config: 配置字典
            
        Returns:
            唯一标识符字符串
        """
        # 将配置字典转换为排序后的字符串，确保一致性
        config_str = str(sorted(config.items())) if config else ""
        return f"{db_type}_{config_str}"
    
    @classmethod
    def get_instance(cls, instance_key: str) -> Optional[DatabaseInterface]:
        """根据标识符获取已创建的数据库实例
        
        Args:
            instance_key: 实例标识符
            
        Returns:
            数据库实例，如果不存在则返回None
        """
        return cls._instances.get(instance_key)
    
    @classmethod
    def clear_instance(cls, instance_key: str) -> bool:
        """清除指定的数据库实例
        
        Args:
            instance_key: 实例标识符
            
        Returns:
            是否成功清除
        """
        if instance_key in cls._instances:
            instance = cls._instances[instance_key]
            try:
                instance.close()
            except Exception:
                pass  # 忽略关闭时的错误
            del cls._instances[instance_key]
            return True
        return False
    
    @classmethod
    def clear_all_instances(cls) -> None:
        """清除所有数据库实例"""
        for instance in cls._instances.values():
            try:
                instance.close()
            except Exception:
                pass  # 忽略关闭时的错误
        cls._instances.clear()
    
    @classmethod
    def get_instance_keys(cls) -> list:
        """获取所有实例标识符
        
        Returns:
            实例标识符列表
        """
        return list(cls._instances.keys())
    
    @classmethod
    def register_database_type(cls, name: str, database_class: type) -> None:
        """注册新的数据库类型
        
        Args:
            name: 数据库类型名称
            database_class: 数据库类，必须实现DatabaseInterface
            
        Raises:
            ValueError: 如果类未实现DatabaseInterface接口
        """
        if not issubclass(database_class, DatabaseInterface):
            raise ValueError(
                f"数据库类 {database_class.__name__} 必须实现 DatabaseInterface"
            )
        cls.DATABASE_TYPES[name] = database_class
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取支持的数据库类型列表
        
        Returns:
            支持的数据库类型列表
        """
        return list(cls.DATABASE_TYPES.keys())


class DatabaseConfigBuilder:
    """数据库配置构建器 - 用于简化数据库配置的创建"""
    
    def __init__(self):
        self._config = {}
    
    def sqlite(self, db_path: str = 'rpa_ztdb.db') -> 'DatabaseConfigBuilder':
        """配置SQLite数据库"""
        self._config = {
            'type': 'sqlite',
            'db_path': db_path
        }
        return self
    
    def http_sqlite(
        self, 
        base_url: str = 'http://localhost:5000',
        use_lock: bool = False
    ) -> 'DatabaseConfigBuilder':
        """配置HTTP SQLite数据库"""
        self._config = {
            'type': 'http_sqlite',
            'base_url': base_url,
            'use_lock': use_lock
        }
        return self
    
    def with_config(self, key: str, value: Any) -> 'DatabaseConfigBuilder':
        """添加额外配置"""
        self._config[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """构建配置字典"""
        return self._config.copy()
    
    def create(self) -> DatabaseInterface:
        """直接创建数据库实例"""
        db_type = self._config.pop('type', 'sqlite')
        return DatabaseFactory.create_database(db_type, self._config)