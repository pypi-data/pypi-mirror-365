import requests
import json
from typing import Dict, List, Any, Optional
from xianbao.core.DatabaseInterface import DatabaseInterface
from xianbao.core.CustomSQLInterface import CustomSQLInterface
from xianbao.core.ast import DMLGenerator


class HttpSQLiteDatabase(DatabaseInterface, CustomSQLInterface):
    """基于HTTP API的SQLite数据库操作实现
    
    通过HTTP API与SQLite数据库进行交互，支持所有标准数据库操作。
    使用RESTful API调用方式，支持参数化查询和事务操作。
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000', use_lock: bool = False):
        """初始化HTTP SQLite数据库客户端
        
        Args:
            base_url: API服务的基础URL，默认为 http://localhost:5000
            use_lock: 是否使用带锁的接口，默认为False
        """
        self.base_url = base_url.rstrip('/')
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
        
        # 初始化DML生成器
        self.dml_generator = DMLGenerator()
    
    def _execute_sql(self, sql: str, params: tuple = None) -> Dict[str, Any]:
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
            response = self.session.post(self.sql_endpoint, json=payload)
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
        
        sql, sql_params = self.dml_generator.dict_to_select(kwargs)
        result = self._execute_sql(sql, tuple(sql_params))

        return result.get('data', [])
    
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

        sql, sql_params = self.dml_generator.dict_to_update(kwargs)
        result = self._execute_sql(sql, tuple(sql_params))

        return result.get('affected_rows', 0)
    
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

        sql, sql_params = self.dml_generator.dict_to_insert(data)
        result = self._execute_sql(sql, tuple(sql_params))

        return result.get('last_insert_id')
    
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

        sql, sql_params = self.dml_generator.dict_to_delete(kwargs)
        result = self._execute_sql(sql, tuple(sql_params))

        return result.get('affected_rows', 0)
    
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

        sql, sql_params = self.dml_generator.dict_to_count(kwargs)
        result = self._execute_sql(sql, tuple(sql_params))

        # 从结果中提取计数值
        data = result.get('data', [])
        if data:
            return list(data[0].values())[0]
        return 0
    
    def begin_transaction(self) -> None:
        """开始事务
        
        注意：HTTP API模式下，事务控制由服务器端管理
        此方法主要用于接口兼容性
        """
        # HTTP API模式下，事务由服务器自动管理
        pass
    
    def commit_transaction(self) -> None:
        """提交事务
        
        注意：HTTP API模式下，事务控制由服务器端管理
        此方法主要用于接口兼容性
        """
        # HTTP API模式下，事务由服务器自动管理
        pass
    
    def rollback_transaction(self) -> None:
        """回滚事务
        
        注意：HTTP API模式下，事务控制由服务器端管理
        此方法主要用于接口兼容性
        """
        # HTTP API模式下，事务由服务器自动管理
        pass
    
    def close(self) -> None:
        """关闭数据库连接
        
        在HTTP模式下，关闭会话连接
        """
        if self.session:
            self.session.close()
    
    def execute_custom_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义SQL查询语句（DML）
        
        Args:
            sql: 要执行的SQL语句
            params: SQL参数元组，用于参数化查询
            
        Returns:
            查询结果列表，每个元素是一个字典，键为列名，值为对应的数据
        """
        result = self._execute_sql(sql, params)
        return result.get('data', [])
    
    def execute_custom_update(self, sql: str, params: tuple = None) -> int:
        """执行自定义更新语句（DML/DDL）
        
        Args:
            sql: 要执行的SQL语句（UPDATE, INSERT, DELETE, DDL等）
            params: SQL参数元组，用于参数化查询
            
        Returns:
            受影响的行数（对于DML语句）或0（对于DDL语句）
        """
        result = self._execute_sql(sql, params)
        return result.get('affected_rows', 0)
    
    def query_with_pagination(self, **kwargs) -> Dict:
        """分页查询

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {查询条件表达式}
                fields: ["字段1", "字段2"]  # 可选
                order_by: "排序字段"  # 可选
                ascending: true  # 可选，默认true
                limit: 10  # 限制返回记录数
                offset: 0  # 偏移量

        Returns:
            包含分页信息的字典：
            {
                'data': [],  # 当前页数据
                'total': 0,  # 总记录数
                'limit': 10,  # 返回记录数
                'offset': 0  # 偏移量
            }
        """
        # 从kwargs中获取table参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")

        limit = kwargs.get('limit', 10)
        offset = kwargs.get('offset', 0)

        # 查询数据
        data = self.query(table=table, **kwargs)

        # 查询总数
        count_kwargs = {k: v for k, v in kwargs.items() if k not in ['fields', 'limit', 'offset', 'order_by']}
        total = self.count(table=table, **count_kwargs)

        return {
            'data': data,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    def query_with_sorting(self, params: Dict) -> List[Dict]:
        """排序查询

        Args:
            params: 排序查询参数字典，格式：
                {
                    "table": "表名",
                    "ast": {查询条件表达式},
                    "order_by": "排序字段",  # 可选
                    "ascending": true,  # 可选，默认true
                    "fields": ["字段1", "字段2"]  # 可选
                }

        Returns:
            查询结果列表
        """
        table = params.get('table')
        if not table:
            raise ValueError("table参数不能为空")

        # 构建查询参数
        query_params = {
            'table': table,
            'ast': params.get('ast', {})
        }

        if params.get('fields'):
            query_params['fields'] = params['fields']

        if params.get('order_by'):
            query_params['order_by'] = params['order_by']
            query_params['ascending'] = params.get('ascending', True)

        return self.query(**query_params)
    
    def batch_insert(self, **kwargs) -> List[Any]:
        """批量插入

        Args:
            **kwargs: 批量插入参数，支持：
                table: "表名"
                data: 要插入的记录列表，每个记录是一个字典

        Returns:
            插入成功的行ID列表
        """
        # 从kwargs中获取table和data参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")

        data = kwargs.pop('data', None)
        if not data:
            raise ValueError("data参数不能为空")

        inserted_ids = []
        for record in data:
            inserted_id = self.insert(table=table, **record)
            inserted_ids.append(inserted_id)

        return inserted_ids
    
    def batch_update(self, **kwargs) -> int:
        """批量更新

        Args:
            **kwargs: 批量更新参数，支持：
                table: "表名"
                updates: 更新配置列表，每个配置是一个字典：
                    {
                        "set": {字段: 值},
                        "where": {条件表达式}
                    }

        Returns:
            受影响的行数总和
        """
        # 从kwargs中获取table和updates参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")

        updates = kwargs.pop('updates', None)
        if not updates:
            raise ValueError("updates参数不能为空")

        total_affected = 0
        for update_item in updates:
            affected = self.update(table=table, set=update_item['set'], **update_item.get('where', {}))
            total_affected += affected

        return total_affected
    
    def batch_delete(self, **kwargs) -> int:
        """批量删除

        Args:
            **kwargs: 批量删除参数，支持：
                table: "表名"
                conditions: 删除条件列表，每个条件是一个字典：
                    {条件表达式}

        Returns:
            删除的行数总和
        """
        # 从kwargs中获取table和conditions参数
        table = kwargs.pop('table', None)
        if not table:
            raise ValueError("table参数不能为空")

        conditions = kwargs.pop('conditions', None)
        if not conditions:
            raise ValueError("conditions参数不能为空")

        total_affected = 0
        for condition in conditions:
            affected = self.delete(table=table, **condition)
            total_affected += affected

        return total_affected
    
    def exists(self, **kwargs) -> bool:
        """检查记录是否存在

        Args:
            **kwargs: AST格式参数，支持：
                table: "表名"
                where: {条件表达式}

        Returns:
            是否存在符合条件的记录
        """
        count = self.count(**kwargs)
        return count > 0
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息
        
        Returns:
            数据库信息，包含表结构等
        """
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get database info: {str(e)}")
    
    def health_check(self) -> bool:
        """健康检查
        
        Returns:
            服务是否健康
        """
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            result = response.json()
            return result.get('status') == 'healthy'
        except:
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接
        
        执行完整的连接测试，包括健康检查和基本查询测试。
        
        Returns:
            包含连接测试结果的详细信息：
            - success: 是否连接成功
            - message: 测试结果描述
            - response_time: 响应时间（毫秒）
            - status_code: HTTP状态码
            - server_info: 服务器信息（如果成功）
            - error: 错误信息（如果失败）
        """
        import time
        
        start_time = time.time()
        result = {
            'success': False,
            'message': '',
            'response_time': 0,
            'status_code': None,
            'server_info': None,
            'error': None
        }
        
        try:
            # 测试健康检查端点
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            response_time = int((time.time() - start_time) * 1000)
            
            result['response_time'] = response_time
            result['status_code'] = response.status_code
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get('status') == 'healthy':
                    # 测试基本查询
                    try:
                        test_sql = "SELECT 1 as test"
                        test_response = self.session.post(
                            self.sql_endpoint,
                            json={"sql": test_sql, "params": []},
                            timeout=5
                        )
                        
                        if test_response.status_code == 200:
                            test_result = test_response.json()
                            if test_result.get('success', False):
                                result['success'] = True
                                result['message'] = '连接成功，数据库可正常访问'
                                result['server_info'] = health_data
                            else:
                                result['message'] = '健康检查通过，但查询测试失败'
                                result['error'] = test_result.get('error', '未知错误')
                        else:
                            result['message'] = '健康检查通过，但查询测试返回异常状态码'
                            result['error'] = f"查询测试返回状态码: {test_response.status_code}"
                    except Exception as e:
                        result['message'] = '健康检查通过，但查询测试失败'
                        result['error'] = str(e)
                else:
                    result['message'] = '服务健康检查未通过'
                    result['error'] = health_data.get('message', '服务状态异常')
            else:
                result['message'] = 'HTTP请求失败'
                result['error'] = f"HTTP状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            result['message'] = '连接超时'
            result['error'] = '请求超时，请检查服务器是否可达'
        except requests.exceptions.ConnectionError:
            result['message'] = '连接失败'
            result['error'] = '无法连接到服务器，请检查网络配置'
        except requests.exceptions.RequestException as e:
            result['message'] = '请求异常'
            result['error'] = str(e)
        except Exception as e:
            result['message'] = '未知错误'
            result['error'] = str(e)
            
        return result
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def get_field_values(
        self, 
        collection: str, 
        field: str, 
        conditions: Dict = None,
        distinct: bool = False
    ) -> List[Any]:
        """获取指定字段的值列表
        
        Args:
            collection: 集合/表名
            field: 字段名
            conditions: 查询条件字典
            distinct: 是否去重
            
        Returns:
            字段值列表
        """
        # 构建查询参数
        query_params = {
            'table': collection,
            'fields': [field]
        }
        
        if conditions:
            query_params['where'] = conditions
            
        # 执行查询
        results = self.query(**query_params)
        
        # 提取字段值
        values = [row.get(field) for row in results]
        
        # 去重处理（如果需要）
        if distinct:
            seen = set()
            values = [x for x in values if not (x in seen or seen.add(x))]
            
        return values

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()