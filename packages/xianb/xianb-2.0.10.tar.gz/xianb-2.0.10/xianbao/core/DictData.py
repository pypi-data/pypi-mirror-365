
from typing import Dict, List, Optional
from xianbao.core.DictApi import DictApi
from xianbao.core.DatabaseInterface import DatabaseInterface


class DictManager:
    """数据字典管理类 - 外观模式，委托给DictApi实现"""

    def __init__(self, db_interface: DatabaseInterface, db_language: tuple) -> None:
        """初始化数据字典管理器"""
        self.dict_api = DictApi(db_interface=db_interface, db_language=db_language)
        self.initialize()

    def initialize(self) -> None:
        """初始化数据字典表结构"""
        self.dict_api.initialize_tables()

    # 字典类型管理
    def add_dict_type(self, name: str, code: str, description: str = "") -> int:
        """添加字典类型"""
        return self.dict_api.add_dict_type(name, code, description)

    def get_dict_type_by_code(self, code: str) -> Optional[Dict]:
        """根据编码获取字典类型"""
        return self.dict_api.get_dict_type_by_code(code)

    def list_all_dict_types(self) -> List[Dict]:
        """获取所有字典类型"""
        return self.dict_api.list_all_dict_types()

    def delete_dict_type(self, code: str) -> bool:
        """删除字典类型"""
        return self.dict_api.delete_dict_type(code)

    def search_dict_types(self, keyword: str) -> List[Dict]:
        """搜索字典类型"""
        return self.dict_api.search_dict_types(keyword)

    # 字典项管理
    def add_dict_item(
            self,
            type_code: str,
            key: str,
            value: str,
            sort_order: int = 0
    ) -> int:
        """添加字典项到指定类型的字典"""
        return self.dict_api.add_dict_item(type_code, key, value, sort_order)

    def get_dict_items(self, type_code: str) -> List[Dict]:
        """根据字典类型编码获取所有字典项"""
        return self.dict_api.get_dict_items(type_code)

    def get_dict_value(self, type_code: str, key: str) -> Optional[str]:
        """获取指定字典类型和键对应的值"""
        return self.dict_api.get_dict_value(type_code, key)

    def update_dict_item(
            self,
            type_code: str,
            key: str,
            new_value: str,
            new_sort_order: Optional[int] = None
    ) -> bool:
        """更新字典项"""
        return self.dict_api.update_dict_item(type_code, key, new_value, new_sort_order)

    def delete_dict_item(self, type_code: str, key: str) -> bool:
        """删除字典项"""
        return self.dict_api.delete_dict_item(type_code, key)

    def get_dict_item_by_key(self, type_code: str, key: str) -> Optional[Dict]:
        """根据字典类型编码和键获取单个字典项"""
        return self.dict_api.get_dict_item_by_key(type_code, key)

    def clear_dict_items(self, type_code: str) -> int:
        """清空指定字典类型的所有字典项"""
        return self.dict_api.clear_dict_items(type_code)

    # 高级功能
    def get_dict_as_mapping(self, type_code: str) -> Dict[str, str]:
        """将字典类型的所有项转换为字典映射"""
        return self.dict_api.get_dict_as_mapping(type_code)

    def get_dict_lookup(self, type_code: str) -> Dict[str, str]:
        """获取反向字典（值到键的映射）"""
        return self.dict_api.get_dict_lookup(type_code)

    def execute_custom_sql(self, sql: str, params: tuple = ()) -> List[Dict]:
        """执行自定义SQL查询"""
        return self.dict_api.execute_custom_sql(sql, params)
