from abc import ABC, abstractmethod
from queue import Empty, Full
import time


class ProcessQueueInterface(ABC):
    """
    进程安全队列的抽象接口
    
    定义了所有进程安全队列实现都应该支持的基本操作，
    包括入队、出队、队列状态查询等功能。
    """
    
    @abstractmethod
    def put(self, item: bytes, block: bool = True, timeout: float = None) -> None:
        """
        将项目放入队列
        
        :param item: 要放入队列的数据（必须是bytes类型）
        :param block: 如果队列满是否阻塞等待，默认为True
        :param timeout: 阻塞等待的最大时间（秒），None表示无限等待
        :raises Full: 当队列满且block为False或超时
        :raises TypeError: 当item不是bytes类型
        :raises TimeoutError: 获取锁超时
        """
        pass
    
    @abstractmethod
    def get(self, block: bool = True, timeout: float = None) -> bytes:
        """
        从队列获取项目
        
        :param block: 如果队列空是否阻塞等待，默认为True
        :param timeout: 阻塞等待的最大时间（秒），None表示无限等待
        :return: 从队列中获取的数据
        :raises Empty: 当队列空且block为False或超时
        :raises TimeoutError: 获取锁超时
        """
        pass
    
    @abstractmethod
    def qsize(self) -> int:
        """
        返回队列中的项目数
        
        :return: 当前队列中的项目数量
        """
        pass
    
    @abstractmethod
    def empty(self) -> bool:
        """
        检查队列是否为空
        
        :return: 如果队列为空返回True，否则False
        """
        pass
    
    @abstractmethod
    def full(self) -> bool:
        """
        检查队列是否已满
        
        :return: 如果队列已满返回True，否则False
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        清空队列中的所有项目
        
        注意：此操作通常需要获取锁，可能会阻塞
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        关闭队列，释放相关资源
        
        应该清理所有打开的数据库连接、文件句柄等资源
        """
        pass


class ProcessQueueBase(ProcessQueueInterface):
    """
    进程安全队列的基类实现
    
    提供了一些通用功能的默认实现，可以被具体实现类继承
    """
    
    def __init__(self, max_size: int = None, timeout: float = 30.0):
        """
        初始化队列基类
        
        :param max_size: 队列最大容量，None表示无限制
        :param timeout: 默认操作超时时间（秒）
        """
        self.max_size = max_size
        self.timeout = timeout
    
    def empty(self) -> bool:
        """默认实现：检查队列是否为空"""
        return self.qsize() == 0
    
    def full(self) -> bool:
        """默认实现：检查队列是否已满"""
        if self.max_size is None:
            return False
        return self.qsize() >= self.max_size
    
    def _validate_item(self, item: bytes) -> None:
        """
        验证数据项的有效性
        
        :param item: 要验证的数据项
        :raises TypeError: 当item不是bytes类型
        """
        if not isinstance(item, bytes):
            raise TypeError("Only bytes are supported")
    
    def _calculate_timeout(self, start_time: float, timeout: float = None) -> float:
        """
        计算剩余的超时时间
        
        :param start_time: 操作开始时间（monotonic）
        :param timeout: 设定的超时时间，None表示使用默认超时
        :return: 剩余的超时时间
        """
        if timeout is None:
            timeout = self.timeout
        
        if timeout is None:
            return None
        
        elapsed = time.monotonic() - start_time
        return max(0, timeout - elapsed)
    
    def _should_retry(self, start_time: float, timeout: float = None) -> bool:
        """
        判断是否应重试操作
        
        :param start_time: 操作开始时间
        :param timeout: 超时时间
        :return: 如果应继续重试返回True
        """
        if timeout is None:
            return True
        return time.monotonic() - start_time < timeout
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()