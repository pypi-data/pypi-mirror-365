import requests
import json
import time
from typing import Optional
from queue import Empty, Full
from xianbao.core.ProcessQueueInterface import ProcessQueueBase
from xianbao.core.DtypeConver import convert_payload


class HttpSQLiteProcessQueue(ProcessQueueBase):
    """
    基于HTTP API的SQLite进程安全队列实现
    
    通过HTTP API与SQLite数据库进行交互，实现进程安全的队列操作。
    支持use_lock模式，可选择使用带锁的接口。
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000', 
                 table_name: str = 'http_queue', max_size: int = 10000,
                 timeout: float = 30.0, use_lock: bool = False):
        """
        初始化HTTP SQLite进程队列客户端
        
        Args:
            base_url: API服务的基础URL，默认为 http://localhost:5000
            table_name: 队列表名，默认为 'http_queue'
            max_size: 队列最大容量，默认为10000
            timeout: 默认操作超时时间（秒），默认为30.0
            use_lock: 是否使用带锁的接口，默认为False
        """
        super().__init__(max_size=max_size, timeout=timeout)
        
        self.base_url = base_url.rstrip('/')
        self.table_name = table_name
        self.use_lock = use_lock
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 根据是否使用锁选择不同的端点
        if use_lock:
            self.sql_endpoint = f"{self.base_url}/api/sql/lock"
        else:
            self.sql_endpoint = f"{self.base_url}/api/sql"
            
        # 初始化队列表
        self._init_queue_table()
    
    def _execute_sql(self, sql: str, params: tuple = None) -> dict:
        """执行SQL语句的通用方法
        
        Args:
            sql: 要执行的SQL语句
            params: SQL参数列表
            
        Returns:
            API响应数据
            
        Raises:
            Exception: 当SQL执行失败时抛出异常
        """
        payload = {
            "sql": sql,
            "params": params or []
        }
        
        try:
            response = self.session.post(self.sql_endpoint, json=convert_payload(payload))
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                error_msg = result.get('error', 'Unknown error')
                raise Exception(f"SQL execution failed: {error_msg}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def _init_queue_table(self) -> None:
        """初始化队列表结构"""
        create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self._execute_sql(create_table_sql)
        
        # 创建索引以加速查询
        create_index_sql = f'''
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_order 
            ON {self.table_name}(id ASC)
        '''
        self._execute_sql(create_index_sql)
    
    def put(self, item, block: bool = True, timeout: float = None) -> None:
        """将项目放入队列
        
        Args:
            item: 要放入队列的数据（必须是bytes类型）
            block: 如果队列满是否阻塞等待，默认为True
            timeout: 阻塞等待的最大时间（秒），None表示无限等待
            
        Raises:
            Full: 当队列满且block为False或超时
            TypeError: 当item不是bytes类型
            Exception: HTTP请求失败
        """
        self._validate_item(item)
        
        timeout = timeout or self.timeout
        start_time = time.monotonic()
        poll_interval = 0.1
        max_poll_interval = 1.0
        
        while True:
            try:
                # 检查队列当前大小
                current_size = self.qsize()
                
                if self.max_size is not None and current_size >= self.max_size:
                    if not block:
                        raise Full("Queue full")
                    
                    elapsed = time.monotonic() - start_time
                    if timeout is not None and elapsed >= timeout:
                        raise Full("Queue full")
                    
                    time.sleep(poll_interval)
                    poll_interval = min(poll_interval * 2, max_poll_interval)
                    continue
                
                # 插入数据
                insert_sql = f'''
                    INSERT INTO {self.table_name} (data) VALUES (?)
                '''
                self._execute_sql(insert_sql, (item,))
                return
                
            except Exception as e:
                if "Queue full" in str(e):
                    raise
                # 其他错误直接抛出
                raise Exception(f"Failed to put item into queue: {str(e)}")
    
    def get(self, block: bool = True, timeout: float = None) -> bytes:
        """从队列获取项目
        
        Args:
            block: 如果队列空是否阻塞等待，默认为True
            timeout: 阻塞等待的最大时间（秒），None表示无限等待
            
        Returns:
            从队列中获取的数据
            
        Raises:
            Empty: 当队列空且block为False或超时
            Exception: HTTP请求失败
        """
        timeout = timeout or self.timeout
        start_time = time.monotonic()
        poll_interval = 0.1
        max_poll_interval = 1.0
        
        while True:
            try:
                # 获取并删除最旧的项目
                delete_sql = f'''
                    DELETE FROM {self.table_name} 
                    WHERE id = (
                        SELECT id FROM {self.table_name} 
                        ORDER BY id ASC LIMIT 1
                    )
                    RETURNING data
                '''
                result = self._execute_sql(delete_sql)
                
                data = result.get('data', [])
                if data and len(data) > 0:
                    # 提取BLOB数据
                    blob_data = data[0].get('data')
                    if blob_data is not None:
                        # 如果数据是base64编码的，需要解码
                        if isinstance(blob_data, str):
                            import base64
                            return base64.b64decode(blob_data)
                        return blob_data
                
                # 队列为空
                if not block:
                    raise Empty("Queue empty")
                
                elapsed = time.monotonic() - start_time
                if timeout is not None and elapsed >= timeout:
                    raise Empty("Queue empty")
                
                time.sleep(poll_interval)
                poll_interval = min(poll_interval * 2, max_poll_interval)
                
            except Exception as e:
                if "Queue empty" in str(e):
                    raise
                # 其他错误直接抛出
                raise Exception(f"Failed to get item from queue: {str(e)}")
    
    def qsize(self) -> int:
        """返回队列中的项目数
        
        Returns:
            当前队列中的项目数量
        """
        count_sql = f'''
            SELECT COUNT(*) as count FROM {self.table_name}
        '''
        result = self._execute_sql(count_sql)
        
        data = result.get('data', [])
        if data and len(data) > 0:
            return data[0].get('count', 0)
        return 0
    
    def clear(self) -> None:
        """清空队列中的所有项目"""
        clear_sql = f'''
            DELETE FROM {self.table_name}
        '''
        self._execute_sql(clear_sql)
    
    def close(self) -> None:
        """关闭队列，释放相关资源"""
        if self.session:
            self.session.close()
    
    def vacuum(self) -> None:
        """回收数据库空间"""
        vacuum_sql = 'VACUUM'
        self._execute_sql(vacuum_sql)
    
    def maintenance(self) -> None:
        """执行数据库维护任务"""
        # WAL检查点
        checkpoint_sql = 'PRAGMA wal_checkpoint(TRUNCATE)'
        try:
            self._execute_sql(checkpoint_sql)
        except:
            pass  # 某些配置可能不支持
        
        # 重新构建索引
        reindex_sql = f'REINDEX {self.table_name}'
        self._execute_sql(reindex_sql)