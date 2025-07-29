import sqlite3
from xianbao.core.DatabaseLanguageEnhanced import AdvancedDatabaseLanguageFactory
from typing import Dict, List, Any
from xianbao.core.DatabaseInterface import DatabaseInterface
from xianbao.core.CustomSQLInterface import CustomSQLInterface
from xianbao.core.ast import DMLGenerator


class SQLiteDatabase(DatabaseInterface, CustomSQLInterface):
    """SQLite数据库操作实现"""
    
    def __init__(self, db_name: str = 'rpa_ztdb.db'):
        """初始化SQLite数据库连接
        
        Args:
            db_name: 数据库文件名
        """
        self.db_path = db_name
        self.connection = None
        self.cursor = None
        _, self.dml = AdvancedDatabaseLanguageFactory.create()
        self.dml_generator = DMLGenerator()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_COLNAMES)
            self.connection.row_factory = sqlite3.Row  # 允许以字典方式访问结果
        return self.connection

    def query(self, **kwargs) -> List[Dict]:
        """执行查询操作

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                fields: ["字段列表"]
                where: {条件表达式}
                order_by: "排序字段"
                limit: 数量
                offset: 偏移量
                joins: [联表配置]
                group_by: [分组字段]
                having: {分组条件}

        Returns:
            查询结果列表
        """
        if 'table' not in kwargs:
            raise ValueError("table参数不能为空")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST格式参数
            sql, params = self.dml_generator.dict_to_select(kwargs)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # 将结果转换为字典形式
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def update(self, **kwargs) -> int:
        """执行更新操作

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                set: {要更新的字段和值字典}
                where: {条件表达式}

        Returns:
            受影响的行数
        """
        if 'table' not in kwargs:
            raise ValueError("table参数不能为空")
        
        if 'set' not in kwargs:
            raise ValueError("set参数不能为空")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST生成SQL和参数
            sql, params = self.dml_generator.dict_to_update(kwargs)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
    
    def insert(self, **data) -> Any:
        """执行插入操作

        Args:
            **data: 要插入的字段和值，包含：
                table: "表名"
                其他字段: 值

        Returns:
            最后插入的行ID
        """
        if 'table' not in data:
            raise ValueError("table参数不能为空")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST格式参数
            sql, params = self.dml_generator.dict_to_insert(data)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
    
    def begin_transaction(self) -> None:
        """开始事务"""
        self._get_connection().execute("BEGIN")
    
    def commit_transaction(self) -> None:
        """提交事务"""
        if self.connection:
            self.connection.commit()
    
    def rollback_transaction(self) -> None:
        """回滚事务"""
        if self.connection:
            self.connection.rollback()
    
    def delete(self, **kwargs) -> int:
        """执行删除操作

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {条件表达式}

        Returns:
            删除的行数
        """
        if 'table' not in kwargs:
            raise ValueError("table参数不能为空")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST生成SQL和参数
            sql, params = self.dml_generator.dict_to_delete(kwargs)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
    
    def count(self, **kwargs) -> int:
        """执行计数操作

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {条件表达式}

        Returns:
            符合条件的记录数
        """
        if 'table' not in kwargs:
            raise ValueError("table参数不能为空")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST生成SQL
            sql, params = self.dml_generator.dict_to_count(kwargs)
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接
        
        执行完整的数据库连接测试，包括文件访问权限和基本查询测试。
        
        Returns:
            包含连接测试结果的详细信息：
            - success: 是否连接成功
            - message: 测试结果描述
            - response_time: 响应时间（毫秒）
            - file_path: 数据库文件路径
            - file_exists: 数据库文件是否存在
            - file_size: 数据库文件大小（字节）
            - error: 错误信息（如果失败）
        """
        import time
        import os
        
        start_time = time.time()
        result = {
            'success': False,
            'message': '',
            'response_time': 0,
            'file_path': self.db_path,
            'file_exists': False,
            'file_size': 0,
            'error': None
        }
        
        try:
            # 检查数据库文件是否存在
            result['file_exists'] = os.path.exists(self.db_path)
            
            if result['file_exists']:
                result['file_size'] = os.path.getsize(self.db_path)
            
            # 测试数据库连接
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 测试基本查询
            cursor.execute("SELECT 1 as test")
            test_result = cursor.fetchone()
            
            if test_result and test_result[0] == 1:
                response_time = int((time.time() - start_time) * 1000)
                result['response_time'] = response_time
                result['success'] = True
                
                if result['file_exists']:
                    result['message'] = f'连接成功，数据库文件正常 ({result["file_size"]} 字节)'
                else:
                    result['message'] = '连接成功，已创建新的数据库文件'
            else:
                result['message'] = '连接失败，查询测试未返回预期结果'
                result['error'] = '查询测试失败'
                
        except sqlite3.Error as e:
            result['message'] = '数据库连接失败'
            result['error'] = f"SQLite错误: {str(e)}"
        except Exception as e:
            result['message'] = '未知错误'
            result['error'] = str(e)
            
        return result
    
    def execute_custom_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义SQL查询语句（DML）

        Args:
            sql: 要执行的SQL语句
            params: SQL参数元组，用于参数化查询

        Returns:
            查询结果列表，每个元素是一个字典，键为列名，值为对应的数据
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            rows = cursor.fetchall()

            # 将结果转换为字典形式
            if cursor.description:  # 检查是否有结果集
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            else:
                return []
    
    def execute_custom_update(self, sql: str, params: tuple = None) -> int:
        """执行自定义更新语句（DML/DDL）

        Args:
            sql: 要执行的SQL语句（UPDATE, INSERT, DELETE, DDL等）
            params: SQL参数元组，用于参数化查询

        Returns:
            受影响的行数（对于DML语句）或0（对于DDL语句）
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                # 对于DDL语句，rowcount可能为-1，此时返回0
                affected_rows = max(0, cursor.rowcount)

                # 自动提交事务
                conn.commit()
                return affected_rows

            except Exception as e:
                # 发生错误时回滚事务
                conn.rollback()
                raise e
    
    def query_with_pagination(self, **kwargs) -> List[Dict]:
        """分页查询方法

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                fields: ["字段列表"]
                where: {条件表达式}
                order_by: "排序字段"
                limit: 数量
                offset: 偏移量
                ascending: 排序方向（True升序，False降序）

        Returns:
            查询结果列表
        """
        if 'table' not in kwargs:
            raise ValueError("table参数不能为空")

        # 处理排序方向
        ascending = kwargs.pop('ascending', True)
        order_by = kwargs.get('order_by')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST格式参数
            sql, params = self.dml_generator.dict_to_select(kwargs)
            
            # 处理排序方向
            if order_by and not ascending:
                sql = sql.replace(f"ORDER BY {order_by}", f"ORDER BY {order_by} DESC")

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # 将结果转换为字典形式
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def query_with_sorting(self, **kwargs) -> List[Dict]:
        """排序查询方法

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {条件表达式}
                order_by: "排序字段"
                ascending: 排序方向（True升序，False降序）

        Returns:
            查询结果列表
        """
        return self.query_with_pagination(**kwargs)
    
    def batch_insert(self, **kwargs) -> List[Any]:
        """批量插入方法

        Args:
            **kwargs: 参数包含：
                table: "表名"
                data_list: [要插入的数据字典列表]

        Returns:
            插入的行ID列表
        """
        # 从kwargs中获取table和data_list参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")
        
        data_list = kwargs.pop('data_list', None)
        if not data_list:
            return []
        
        inserted_ids = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                conn.execute("BEGIN")
                
                for data in data_list:
                    sql, params = self.dml_generator.dict_to_insert(table, data)
                    cursor.execute(sql, params)
                    inserted_ids.append(cursor.lastrowid)
                
                conn.commit()
                return inserted_ids
                
            except Exception as e:
                conn.rollback()
                raise Exception(f"Batch insert failed: {str(e)}")
    
    def batch_update(self, **kwargs) -> int:
        """批量更新方法

        Args:
            **kwargs: 参数包含：
                table: "表名"
                conditions_list: [条件字典列表]
                updates_list: [更新字典列表]

        Returns:
            受影响的行数
        """
        # 从kwargs中获取table参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")
        
        conditions_list = kwargs.pop('conditions_list', None)
        updates_list = kwargs.pop('updates_list', None)
        
        if not conditions_list or not updates_list or len(conditions_list) != len(updates_list):
            return 0
        
        total_affected = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                conn.execute("BEGIN")
                
                for conditions, updates in zip(conditions_list, updates_list):
                    update_params = {'set': updates}
                    if conditions:
                        update_params['where'] = conditions
                    sql, params = self.dml_generator.dict_to_update(table, update_params)
                    cursor.execute(sql, params)
                    total_affected += cursor.rowcount
                
                conn.commit()
                return total_affected
                
            except Exception as e:
                conn.rollback()
                raise Exception(f"Batch update failed: {str(e)}")
    
    def batch_delete(self, **kwargs) -> int:
        """批量删除方法

        Args:
            **kwargs: 参数包含：
                table: "表名"
                conditions_list: [条件字典列表]

        Returns:
            受影响的行数
        """
        # 从kwargs中获取table参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")
        
        conditions_list = kwargs.pop('conditions_list', None)
        
        if not conditions_list:
            return 0
        
        total_affected = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                conn.execute("BEGIN")
                
                for conditions in conditions_list:
                    delete_params = {}
                    if conditions:
                        delete_params['where'] = conditions
                    sql, params = self.dml_generator.dict_to_delete(table, delete_params)
                    cursor.execute(sql, params)
                    total_affected += cursor.rowcount
                
                conn.commit()
                return total_affected
                
            except Exception as e:
                conn.rollback()
                raise Exception(f"Batch delete failed: {str(e)}")
    
    def exists(self, **kwargs) -> bool:
        """检查记录是否存在

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {条件表达式}

        Returns:
            记录是否存在
        """
        # 从kwargs中获取table参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")

        # 构建查询参数字典
        query_params = {'fields': ["1"]}
        if 'where' in kwargs:
            query_params['where'] = kwargs['where']

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST生成SQL
            sql, params = self.dml_generator.dict_to_select(table, query_params)
            sql = sql.replace("SELECT 1", "SELECT COUNT(*) as count")
            
            cursor.execute(sql, params)
            return cursor.fetchone()[0] > 0
    
    def get_field_values(self, **kwargs) -> List[Any]:
        """获取指定字段的值列表

        Args:
            **kwargs: 参数包含：
                table: "表名"
                field: "字段名"
                where: {条件表达式}
                distinct: 是否去重（默认False）

        Returns:
            字段值列表
        """
        # 从kwargs中获取table和field参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")
        
        field = kwargs.pop('field', None)
        if not field:
            raise ValueError("field参数不能为空")

        # 构建查询参数字典
        query_params = {}
        if 'where' in kwargs:
            query_params['where'] = kwargs['where']

        # 处理distinct和字段
        distinct = kwargs.pop('distinct', False)
        query_field = f"DISTINCT {field}" if distinct else field
        query_params['fields'] = [query_field]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 使用AST生成SQL
            sql, params = self.dml_generator.dict_to_select(table, query_params)
            
            cursor.execute(sql, params)
            return [row[0] for row in cursor.fetchall()]
            