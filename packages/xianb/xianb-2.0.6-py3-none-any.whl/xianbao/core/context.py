"""
全局上下文管理器
提供应用程序范围内的共享变量池
"""

class GlobalContext:
    """全局上下文单例类"""
    _instance = None
    _context = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """获取全局上下文实例"""
        return cls()
    
    def set(self, key, value):
        """设置全局变量"""
        self._context[key] = value
    
    def get(self, key, default=None):
        """获取全局变量"""
        return self._context.get(key, default)
    
    def update(self, **kwargs):
        """批量更新全局变量"""
        self._context.update(kwargs)
    
    def remove(self, key):
        """移除全局变量"""
        if key in self._context:
            del self._context[key]
    
    def clear(self):
        """清空所有全局变量"""
        self._context.clear()
    
    def keys(self):
        """获取所有键"""
        return list(self._context.keys())
    
    def __getitem__(self, key):
        """支持字典式访问"""
        return self._context[key]
    
    def __setitem__(self, key, value):
        """支持字典式设置"""
        self._context[key] = value
    
    def __contains__(self, key):
        """支持in操作符"""
        return key in self._context

# 创建全局上下文实例
global_context = GlobalContext.get_instance()