"""
增强版数据库语言模块
集成AST模块功能，支持复杂条件表达式和逻辑操作符
"""

from typing import Dict, List, Any, Tuple, Optional, Union
from abc import ABC, abstractmethod
import sys
import os

# 添加父目录到路径，确保可以导入ast模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xianbao.core.ast import DMLGenerator, QueryBuilder


class DDLInterface(ABC):
    """数据库定义语言(DDL)接口"""
    
    @abstractmethod
    def create_table(self, table_name: str, columns: Dict[str, str], indexes: List[str] = None) -> str:
        """创建表"""
        pass
    
    @abstractmethod
    def create_index(self, table_name: str, column_name: str, index_name: str = None) -> str:
        """创建索引"""
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> str:
        """删除表"""
        pass

    @abstractmethod
    def alter_table(self, table_name: str, action: str, **kwargs) -> str:
        """修改表结构"""
        pass


class DMLInterface(ABC):
    """数据库操作语言(DML)接口 - 增强版"""
    
    @abstractmethod
    def select(self, table_name: str, fields: List[str] = None, conditions: Dict[str, Any] = None, 
              order_by: str = None, limit: int = None, offset: int = None, 
              group_by: str = None, having: Dict[str, Any] = None) -> Tuple[str, List[Any]]:
        """查询数据 - 支持复杂条件"""
        pass
    
    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any], on_conflict: str = None) -> Tuple[str, List[Any]]:
        """插入数据 - 支持冲突处理"""
        pass
    
    @abstractmethod
    def update(self, table_name: str, conditions: Dict[str, Any], updates: Dict[str, Any], 
              limit: int = None) -> Tuple[str, List[Any]]:
        """更新数据 - 支持复杂条件和限制"""
        pass
    
    @abstractmethod
    def delete(self, table_name: str, conditions: Dict[str, Any], limit: int = None) -> Tuple[str, List[Any]]:
        """删除数据 - 支持复杂条件和限制"""
        pass
    
    @abstractmethod
    def count(self, table_name: str, conditions: Dict[str, Any] = None, distinct: str = None) -> Tuple[str, List[Any]]:
        """计数 - 支持去重和复杂条件"""
        pass
    
    @abstractmethod
    def select_join(self, tables: Dict[str, str], fields: List[str] = None, 
                   conditions: Dict[str, Any] = None, join_type: str = "INNER", 
                   on_conditions: Dict[str, str] = None, **kwargs) -> Tuple[str, List[Any]]:
        """连接查询 - 支持多表连接"""
        pass


class EnhancedSqlDDL(DDLInterface):
    """增强版DDL实现"""
    
    def create_table(self, table_name: str, columns: Dict[str, str], indexes: List[str] = None) -> str:
        """创建表实现"""
        columns_sql = ", ".join([f"{name} {type_}" for name, type_ in columns.items()])
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
    
    def create_index(self, table_name: str, column_name: str, index_name: str = None) -> str:
        """创建索引实现"""
        if not index_name:
            index_name = f"idx_{table_name}_{column_name}"
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
    
    def drop_table(self, table_name: str) -> str:
        """删除表实现"""
        return f"DROP TABLE IF EXISTS {table_name}"
    
    def alter_table(self, table_name: str, action: str, **kwargs) -> str:
        """修改表结构"""
        if action.upper() == "ADD_COLUMN":
            column_name = kwargs.get('column_name')
            column_type = kwargs.get('column_type')
            return f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        elif action.upper() == "DROP_COLUMN":
            column_name = kwargs.get('column_name')
            return f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        elif action.upper() == "RENAME_COLUMN":
            old_name = kwargs.get('old_name')
            new_name = kwargs.get('new_name')
            return f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
        else:
            raise ValueError(f"Unsupported alter action: {action}")


class EnhancedSqlDML(DMLInterface):
    """增强版DML实现 - 集成AST模块"""
    
    def __init__(self):
        self.generator = DMLGenerator()
    
    def select(self, table_name: str, fields: List[str] = None, conditions: Dict[str, Any] = None, 
              order_by: str = None, limit: int = None, offset: int = None, 
              group_by: str = None, having: Dict[str, Any] = None) -> Tuple[str, List[Any]]:
        """查询数据 - 支持复杂条件"""
        
        query_dict = {}
        
        if fields:
            query_dict['fields'] = fields
        
        if conditions:
            query_dict['where'] = conditions
            
        if order_by:
            query_dict['order_by'] = order_by
            
        if limit is not None:
            query_dict['limit'] = limit
            
        if offset is not None:
            query_dict['offset'] = offset
            
        # 处理GROUP BY和HAVING
        if group_by or having:
            # 对于GROUP BY和HAVING，我们需要生成基础SQL后手动添加
            base_sql, params = self.generator.dict_to_select(table_name, query_dict)
            
            sql_parts = [base_sql]
            
            if group_by:
                sql_parts.insert(1, f"GROUP BY {group_by}")
                
            if having:
                having_sql, having_params = self._generate_having_clause(having)
                sql_parts.append(f"HAVING {having_sql}")
                params.extend(having_params)
                
            return " ".join(sql_parts), params
        
        return self.generator.dict_to_select(table_name, query_dict)
    
    def insert(self, table_name: str, data: Dict[str, Any], on_conflict: str = None) -> Tuple[str, List[Any]]:
        """插入数据 - 支持冲突处理"""
        insert_dict = {'data': data}
        sql, params = self.generator.dict_to_insert(table_name, insert_dict)
        
        if on_conflict:
            if on_conflict.upper() == "IGNORE":
                sql = sql.replace("INSERT INTO", "INSERT OR IGNORE INTO")
            elif on_conflict.upper() == "REPLACE":
                sql = sql.replace("INSERT INTO", "INSERT OR REPLACE INTO")
            elif on_conflict.upper() == "UPDATE":
                # SQLite UPSERT语法
                fields = list(data.keys())
                placeholders = [f"{field}=excluded.{field}" for field in fields if field != 'id']
                sql = sql + f" ON CONFLICT(id) DO UPDATE SET {', '.join(placeholders)}"
        
        return sql, params
    
    def update(self, table_name: str, conditions: Dict[str, Any], updates: Dict[str, Any], 
              limit: int = None) -> Tuple[str, List[Any]]:
        """更新数据 - 支持复杂条件和限制"""
        update_dict = {
            'set': updates,
            'where': conditions
        }
        
        if limit is not None:
            update_dict['limit'] = limit
            
        sql, params = self.generator.dict_to_update(table_name, update_dict)
        
        # SQLite不支持UPDATE ... LIMIT，需要特殊处理
        if limit is not None:
            sql = f"{sql} LIMIT {limit}"
        
        return sql, params
    
    def delete(self, table_name: str, conditions: Dict[str, Any], limit: int = None) -> Tuple[str, List[Any]]:
        """删除数据 - 支持复杂条件和限制"""
        delete_dict = {'where': conditions}
        
        if limit is not None:
            delete_dict['limit'] = limit
            
        sql, params = self.generator.dict_to_delete(table_name, delete_dict)
        
        # SQLite不支持DELETE ... LIMIT，需要特殊处理
        if limit is not None:
            sql = f"{sql} LIMIT {limit}"
        
        return sql, params
    
    def count(self, table_name: str, conditions: Dict[str, Any] = None, distinct: str = None) -> Tuple[str, List[Any]]:
        """计数 - 支持去重和复杂条件"""
        count_dict = {}
        
        if conditions:
            count_dict['where'] = conditions
            
        if distinct:
            # 使用DISTINCT计数
            query = {'fields': [f"COUNT(DISTINCT {distinct})"]}
            if conditions:
                query['where'] = conditions
            return self.generator.dict_to_select(table_name, query)
        
        return self.generator.dict_to_count(table_name, count_dict)
    
    def select_join(self, tables: Dict[str, str], fields: List[str] = None, 
                   conditions: Dict[str, Any] = None, join_type: str = "INNER", 
                   on_conditions: Dict[str, str] = None, **kwargs) -> Tuple[str, List[Any]]:
        """连接查询 - 支持多表连接"""
        
        if not tables or len(tables) < 2:
            raise ValueError("至少需要两个表进行连接查询")
        
        # 构建JOIN子句
        table_list = list(tables.items())
        main_table, main_alias = table_list[0]
        
        join_parts = [f"{main_table} AS {main_alias}"]
        
        for i in range(1, len(table_list)):
            table, alias = table_list[i]
            join_parts.append(f"{join_type} JOIN {table} AS {alias}")
            
            if on_conditions and f"{main_alias}_{alias}" in on_conditions:
                join_parts.append(f"ON {on_conditions[f'{main_alias}_{alias}']}")
        
        from_clause = " ".join(join_parts)
        
        # 构建查询
        query_dict = {}
        
        if fields:
            query_dict['fields'] = fields
            
        if conditions:
            query_dict['where'] = conditions
            
        for key in ['order_by', 'limit', 'offset']:
            if key in kwargs and kwargs[key] is not None:
                query_dict[key] = kwargs[key]
        
        # 生成基础查询后替换FROM子句
        base_sql, params = self.generator.dict_to_select("__DUMMY__", query_dict)
        sql = base_sql.replace("FROM __DUMMY__", f"FROM {from_clause}")
        
        return sql, params
    
    def _generate_having_clause(self, having: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """生成HAVING子句"""
        # 复用WHERE条件的逻辑
        having_sql, params = self.generator.dict_to_select("__DUMMY__", {'where': having})
        # 提取WHERE部分
        if "WHERE" in having_sql:
            having_part = having_sql.split("WHERE", 1)[1].strip()
            return having_part, params
        return "", []


class AdvancedDatabaseLanguageFactory:
    """增强版数据库语言工厂"""
    
    @staticmethod
    def create(db_type: str = "sqlite") -> Tuple[DDLInterface, DMLInterface]:
        """创建增强版DDL和DML实现"""
        if db_type.lower() == "sqlite" or db_type.lower() == "http_sqlite":
            return EnhancedSqlDDL(), EnhancedSqlDML()
        raise ValueError(f"Unsupported database type: {db_type}")


# 向后兼容的别名
EnhancedSqlLanguageFactory = AdvancedDatabaseLanguageFactory


# 使用示例和测试代码
if __name__ == "__main__":
    """测试增强版DatabaseLanguage"""
    
    print("=== 增强版DatabaseLanguage测试 ===")
    
    # 创建实例
    ddl, dml = AdvancedDatabaseLanguageFactory.create()
    
    # 测试DDL
    print("\n1. DDL测试:")
    create_sql = ddl.create_table('users', {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name': 'TEXT NOT NULL',
        'age': 'INTEGER',
        'email': 'TEXT UNIQUE',
        'status': 'TEXT DEFAULT active'
    })
    print(f"创建表: {create_sql}")
    
    # 测试DML - 基本查询
    print("\n2. DML基本查询:")
    sql, params = dml.select('users', 
                           fields=['id', 'name', 'email'],
                           conditions={'status': 'active', 'age': {'>=': 18}},
                           order_by='created_at DESC',
                           limit=10)
    print(f"基本查询: {sql}")
    print(f"参数: {params}")
    
    # 测试DML - 复杂条件
    print("\n3. DML复杂条件:")
    complex_conditions = {
        'OR': [
            {'name': {'LIKE': '张%'}},
            {'AND': [
                {'age': {'>=': 25}},
                {'age': {'<=': 35}},
                {'status': {'IN': ['active', 'premium']}}
            ]}
        ]
    }
    
    sql, params = dml.select('users', 
                           fields=['name', 'age', 'email'],
                           conditions=complex_conditions,
                           order_by='age ASC')
    print(f"复杂查询: {sql}")
    print(f"参数: {params}")
    
    # 测试插入
    print("\n4. DML插入:")
    sql, params = dml.insert('users', {
        'name': '张三',
        'age': 28,
        'email': 'zhangsan@example.com',
        'status': 'active'
    })
    print(f"插入: {sql}")
    print(f"参数: {params}")
    
    # 测试更新
    print("\n5. DML更新:")
    sql, params = dml.update('users',
                           conditions={'status': 'inactive'},
                           updates={'status': 'active', 'updated_at': '2024-01-01'})
    print(f"更新: {sql}")
    print(f"参数: {params}")
    
    # 测试计数
    print("\n6. DML计数:")
    sql, params = dml.count('users', 
                           conditions={'age': {'>=': 18}, 'status': 'active'})
    print(f"计数: {sql}")
    print(f"参数: {params}")
    
    # 测试连接查询
    print("\n7. 连接查询:")
    tables = {
        'users': 'u',
        'orders': 'o'
    }
    
    sql, params = dml.select_join(
        tables=tables,
        fields=['u.name', 'o.total_amount', 'o.created_at'],
        conditions={'u.status': 'active'},
        on_conditions={'u_o': 'u.id = o.user_id'},
        order_by='o.created_at DESC',
        limit=50
    )
    print(f"连接查询: {sql}")
    print(f"参数: {params}")