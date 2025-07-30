from typing import Dict, List, Optional, Any
from xianbao.core.DatabaseInterface import DatabaseInterface
from xianbao.core.CustomSQLInterface import CustomSQLInterface


class DictApi:
    """数据字典API - 基于AdvancedDatabaseLanguageFactory优化实现"""
    
    def __init__(self, db_interface: DatabaseInterface = None, db_language: tuple = None) -> None:
        """初始化DictApiEnhanced
        Args:
            db_interface: 数据库接口实现，如果提供则直接使用
            db_language: 数据库语言实现，如果提供则直接使用
        """
        self.db_interface = db_interface
        self.ddl, self.dml = db_language
        self.initialize_tables()

    def initialize_tables(self) -> None:
        """初始化数据字典表结构"""
        try:
            # 检查表是否已存在
            result = self.db_interface.execute_custom_sql(
                sql="SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'sys_dict_type'",
                params=[]
            )
            
            if not result:
                # 表不存在，创建表和索引
                self.db_interface.begin_transaction()
                try:
                    # 创建字典类型表
                    create_dict_type_sql = """
                        CREATE TABLE IF NOT EXISTS sys_dict_type (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            code TEXT NOT NULL UNIQUE,
                            description TEXT
                        )
                    """
                    self.db_interface.execute_custom_sql(create_dict_type_sql, [])
                    
                    # 创建字典项表
                    create_dict_data_sql = """
                        CREATE TABLE IF NOT EXISTS sys_dict_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            key TEXT NOT NULL,
                            value TEXT NOT NULL,
                            type_id INTEGER NOT NULL,
                            sort_order INTEGER DEFAULT 0,
                            FOREIGN KEY (type_id) REFERENCES sys_dict_type(id)
                        )
                    """
                    self.db_interface.execute_custom_sql(create_dict_data_sql, [])
                    
                    # 创建索引优化查询
                    self.db_interface.execute_custom_sql(
                        "CREATE INDEX IF NOT EXISTS idx_dict_type_code ON sys_dict_type(code)",
                        []
                    )
                    
                    self.db_interface.execute_custom_sql(
                        "CREATE INDEX IF NOT EXISTS idx_dict_data_type_id ON sys_dict_data(type_id)",
                        []
                    )
                    
                    self.db_interface.execute_custom_sql(
                        "CREATE INDEX IF NOT EXISTS idx_dict_data_key ON sys_dict_data(key)",
                        []
                    )
                    
                    # 创建复合索引
                    self.db_interface.execute_custom_sql(
                        "CREATE UNIQUE INDEX IF NOT EXISTS idx_dict_data_composite ON sys_dict_data(type_id, key)",
                        []
                    )
                    
                    self.db_interface.commit_transaction()
                except Exception as e:
                    self.db_interface.rollback_transaction()
                    raise e
        except Exception as e:
            raise Exception(f"初始化数据字典表结构失败: {str(e)}")

    # 字典类型相关操作
    def add_dict_type(self, name: str, code: str, description: str = "") -> int:
        """添加字典类型"""
        try:
            self.db_interface.begin_transaction()
            type_id = self.db_interface.insert(
                table="sys_dict_type",
                data={
                    "name": name,
                    "code": code,
                    "description": description
                }
            )
            self.db_interface.commit_transaction()
            return type_id
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"添加字典类型失败: {str(e)}")

    def get_dict_type_by_code(self, code: str) -> Optional[Dict]:
        """根据编码获取字典类型"""
        try:
            result = self.db_interface.query(
                table="sys_dict_type",
                where={"code": {"=": code}}
            )
            # HttpSQLiteDatabase返回列表格式
            if isinstance(result, list):
                return result[0] if result else None
            return result
        except Exception as e:
            raise Exception(f"获取字典类型失败: {str(e)}")

    def get_dict_type_by_id(self, type_id: int) -> Optional[Dict]:
        """根据ID获取字典类型"""
        try:
            result = self.db_interface.query(
                table="sys_dict_type",
                where={"id": {"=": type_id}}
            )
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"获取字典类型失败: {str(e)}")

    def list_all_dict_types(self) -> List[Dict]:
        """获取所有字典类型"""
        try:
            result = self.db_interface.query_with_pagination(
                table="sys_dict_type",
                order_by="id",
                ascending=True
            )
            # HttpSQLiteDatabase返回分页格式，提取data字段
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except Exception as e:
            raise Exception(f"获取字典类型列表失败: {str(e)}")

    def delete_dict_type(self, code: str) -> bool:
        """删除字典类型（会级联删除相关字典项）"""
        try:
            self.db_interface.begin_transaction()
            
            # 先获取类型ID
            type_info = self.get_dict_type_by_code(code)
            if not type_info:
                return False
            
            type_id = type_info["id"]
            
            # 删除相关字典项
            self.db_interface.delete(
                table="sys_dict_data",
                where={"type_id": {"=": type_id}}
            )
            
            # 删除字典类型
            affected = self.db_interface.delete(
                table="sys_dict_type",
                where={"code": {"=": code}}
            )
            
            self.db_interface.commit_transaction()
            return affected > 0
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"删除字典类型失败: {str(e)}")

    # 字典项相关操作
    def add_dict_item(self, type_code: str, key: str, value: str, sort_order: int = 0) -> int:
        """添加字典项到指定类型的字典"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                raise ValueError(f"字典类型不存在: {type_code}")
            
            type_id = type_info["id"]
            
            self.db_interface.begin_transaction()
            item_id = self.db_interface.insert(
                table="sys_dict_data",
                data={
                    "key": key,
                    "value": value,
                    "type_id": type_id,
                    "sort_order": sort_order
                }
            )
            self.db_interface.commit_transaction()
            return item_id
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"添加字典项失败: {str(e)}")

    def get_dict_items(self, type_code: str) -> List[Dict]:
        """根据字典类型编码获取所有字典项"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return []
            
            type_id = type_info["id"]
            
            result = self.db_interface.query(
                table="sys_dict_data",
                where={"type_id": {"=": type_id}},
                order_by="sort_order ASC, id ASC"
            )
            
            # HttpSQLiteDatabase返回列表格式
            if isinstance(result, list):
                return [{"key": item["key"], "value": item["value"], "sort_order": item["sort_order"]} 
                       for item in result]
            return []
        except Exception as e:
            raise Exception(f"获取字典项失败: {str(e)}")

    def get_dict_item_by_key(self, type_code: str, key: str) -> Optional[Dict[str, Any]]:
        """根据键获取字典项"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return None
            
            type_id = type_info["id"]
            
            result = self.db_interface.query(
                table="sys_dict_data",
                where={
                    "type_id": {
                        "AND": [
                            {"=": type_id},
                            {"=": key}
                        ]
                    }
                }
            )
            
            if result and len(result) > 0:
                item = result[0]
                return {
                    "key": item["key"],
                    "value": item["value"],
                    "sort_order": item["sort_order"]
                }
            return None
        except Exception as e:
            raise Exception(f"根据键获取字典项失败: {str(e)}")

    def get_dict_value(self, type_code: str, key: str) -> Optional[str]:
        """获取指定字典类型和键对应的值"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return None
            
            type_id = type_info["id"]
            
            result = self.db_interface.query(
                table="sys_dict_data",
                where={"type_id": {"=": type_id}, "key": {"=": key}}
            )
            
            return result[0]["value"] if result else None
        except Exception as e:
            raise Exception(f"获取字典值失败: {str(e)}")

    def update_dict_item(self, type_code: str, key: str, new_value: str, new_sort_order: Optional[int] = None) -> bool:
        """更新字典项"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return False
            
            type_id = type_info["id"]
            
            updates = {"value": new_value}
            if new_sort_order is not None:
                updates["sort_order"] = new_sort_order
            
            affected = self.db_interface.update(
                table="sys_dict_data",
                set=updates,
                where={"type_id": {"=": type_id}, "key": {"=": key}}
            )
            
            return affected > 0
        except Exception as e:
            raise Exception(f"更新字典项失败: {str(e)}")

    def delete_dict_item(self, type_code: str, key: str) -> bool:
        """删除字典项"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return False
            
            type_id = type_info["id"]
            
            affected = self.db_interface.delete(
                table="sys_dict_data",
                where={
                    "AND": [
                        {"type_id": {"=": type_id}},
                        {"key": {"=": key}}
                    ]
                }
            )
            
            return affected > 0
        except Exception as e:
            raise Exception(f"删除字典项失败: {str(e)}")

    def clear_dict_items(self, type_code: str) -> int:
        """清空指定字典类型的所有字典项"""
        try:
            # 获取字典类型ID
            type_info = self.get_dict_type_by_code(type_code)
            if not type_info:
                return 0
            
            type_id = type_info["id"]
            
            affected = self.db_interface.delete(
                table="sys_dict_data",
                where={"type_id": {"=": type_id}}
            )
            
            return affected
        except Exception as e:
            raise Exception(f"清空字典项失败: {str(e)}")

    # 高级查询操作
    def get_dict_as_mapping(self, type_code: str) -> Dict[str, str]:
        """将字典类型的所有项转换为字典映射"""
        items = self.get_dict_items(type_code)
        return {item["key"]: item["value"] for item in items}

    def get_dict_lookup(self, type_code: str) -> Dict[str, str]:
        """获取反向字典（值到键的映射）"""
        items = self.get_dict_items(type_code)
        return {item["value"]: item["key"] for item in items}

    def search_dict_types(self, keyword: str) -> List[Dict]:
        """搜索字典类型（支持模糊匹配）"""
        try:
            like_pattern = f"%{keyword}%"
            
            # 使用OR条件进行模糊搜索
            conditions = {
                "OR": [
                    {"name": {"LIKE": like_pattern}},
                    {"code": {"LIKE": like_pattern}},
                    {"description": {"LIKE": like_pattern}}
                ]
            }
            
            result = self.db_interface.query(
                table="sys_dict_type",
                where=conditions,
                order_by="id ASC"
            )
            
            # HttpSQLiteDatabase返回列表格式
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            raise Exception(f"搜索字典类型失败: {str(e)}")

    def get_dict_stats(self) -> Dict[str, int]:
        """获取字典统计信息"""
        try:
            # 统计字典类型数量
            type_result = self.db_interface.query(
                table="sys_dict_type",
                fields=["COUNT(*) as count"]
            )
            type_count = type_result[0]["count"] if type_result else 0
            
            # 统计字典项数量
            item_result = self.db_interface.query(
                table="sys_dict_data",
                fields=["COUNT(*) as count"]
            )
            item_count = item_result[0]["count"] if item_result else 0
            
            # 统计每个类型的字典项数量
            stats_sql = """
            SELECT t.code, t.name, COUNT(d.id) as item_count
            FROM sys_dict_type t
            LEFT JOIN sys_dict_data d ON t.id = d.type_id
            GROUP BY t.id, t.code, t.name
            ORDER BY item_count DESC
            """
            
            type_stats = self.db_interface.execute_custom_sql(stats_sql)
            type_details = [
                {"code": row["code"], "name": row["name"], "count": row["item_count"]}
                for row in type_stats
            ]
            
            return {
                "total_types": type_count,
                "total_items": item_count,
                "type_details": type_details
            }
        except Exception as e:
            raise Exception(f"获取字典统计信息失败: {str(e)}")

    # 新增的接口兼容函数
    def close(self) -> None:
        """关闭数据库连接"""
        self.db_interface.close()

    def is_custom_sql_supported(self) -> bool:
        """检查是否支持自定义SQL"""
        return isinstance(self.db_interface, CustomSQLInterface)

    def execute_custom_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义查询SQL"""
        if not self.is_custom_sql_supported():
            raise NotImplementedError("当前数据库接口不支持自定义SQL")
        return self.db_interface.execute_custom_sql(sql, params or ())

    def execute_custom_update(self, sql: str, params: tuple = None) -> int:
        """执行自定义更新SQL"""
        if not self.is_custom_sql_supported():
            raise NotImplementedError("当前数据库接口不支持自定义SQL")
        return self.db_interface.execute_custom_update(sql, params or ())
        