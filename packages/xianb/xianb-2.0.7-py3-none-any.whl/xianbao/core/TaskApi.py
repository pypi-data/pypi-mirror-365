import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from xianbao.core.DatabaseInterface import DatabaseInterface


class TaskApi:
    """RPA任务数据库API - 基于DatabaseLanguageEnhanced优化实现
    
    注意：所有where条件语法遵循AST模块的最佳实践，使用明确的运算符格式
    例如：{"id": {"=": 123}} 而不是简写的 {"id": 123}
    """

    # 允许的排序字段白名单
    ALLOWED_ORDER_FIELDS = {"id", "status", "created_time", "updated_time", "business_type", "sort_order"}

    def __init__(self, table_name: str, db_language: tuple, db_interface: DatabaseInterface = None):
        """初始化任务管理API
        
        Args:
            table_name: 任务表名，默认为"tasks"
            db_language: 数据库语言元组，包含DDL和DML语句
            db_interface: 数据库接口实现，如果提供则直接使用
        """
        if db_interface is None:
            raise ValueError("db_interface must be provided")
        
        self.TABLE_NAME = table_name
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.db_interface = db_interface
        self.ddl, self.dml = db_language
        self.initialize_db()

    def _validate_order_field(self, field: str) -> str:
        """验证排序字段是否在白名单中，防止SQL注入"""
        if field not in self.ALLOWED_ORDER_FIELDS:
            raise ValueError(f"Invalid order field: {field}")
        return field

    def initialize_db(self) -> None:
        """初始化数据库和表结构"""
        try:
            # 检查表是否已存在
            existing_tables = self.db_interface.query(
                table="sqlite_master",
                where={
                    "AND": [
                        {"type": {"=": "table"}},
                        {"name": {"=": self.TABLE_NAME}}
                    ]
                }
            )
            
            if not existing_tables:
                # 表不存在，创建表和索引
                self.db_interface.begin_transaction()
                try:
                    # 创建表
                    columns = {
                        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "status": "TEXT NOT NULL",
                        "meta": "TEXT",
                        "created_time": "TEXT NOT NULL",
                        "updated_time": "TEXT NOT NULL",
                        "business_type": "TEXT",
                        "log": "TEXT",
                        "sort_order": "INTEGER"
                    }
                    
                    # 使用自定义SQL创建表和索引
                    create_table_sql = self.ddl.create_table(self.TABLE_NAME, columns)
                    self.db_interface.execute_custom_update(create_table_sql)
                    
                    # 创建索引
                    index_sql1 = self.ddl.create_index(self.TABLE_NAME, "status", "idx_status")
                    index_sql2 = self.ddl.create_index(self.TABLE_NAME, "business_type", "idx_business_type")
                    index_sql3 = self.ddl.create_index(self.TABLE_NAME, "created_time", "idx_created_time")
                    index_sql4 = self.ddl.create_index(self.TABLE_NAME, "sort_order", "idx_sort_order")
                    
                    self.db_interface.execute_custom_update(index_sql1)
                    self.db_interface.execute_custom_update(index_sql2)
                    self.db_interface.execute_custom_update(index_sql3)
                    self.db_interface.execute_custom_update(index_sql4)
                    
                    self.db_interface.commit_transaction()
                except Exception as e:
                    self.db_interface.rollback_transaction()
                    raise e
        except Exception as e:
            raise Exception(f"Failed to initialize database: {str(e)}")

    def add_task(self, meta: Dict, business_type: str, status: int = 0) -> int:
        """添加新任务"""
        now = datetime.now().strftime(self.TIME_FORMAT)
        meta_json = json.dumps(meta)

        try:
            self.db_interface.begin_transaction()
            task_id = self.db_interface.insert(
                table=self.TABLE_NAME,
                data={
                    "status": status,
                    "meta": meta_json,
                    "created_time": now,
                    "updated_time": now,
                    "business_type": business_type
                }
            )
            self.db_interface.commit_transaction()
            return task_id
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"Failed to add task: {str(e)}")

    def update_status(self, task_id: int, new_status: int) -> bool:
        """更新任务状态"""
        now = datetime.now().strftime(self.TIME_FORMAT)

        try:
            self.db_interface.begin_transaction()
            affected = self.db_interface.update(
                table=self.TABLE_NAME,
                set={
                    "status": new_status,
                    "updated_time": now
                },
                where={"id": {"=": task_id}}
            )
            self.db_interface.commit_transaction()
            return affected > 0
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"Failed to update task status: {str(e)}")

    def update_status_and_meta(self, task_id: int, new_status: int, new_meta: Dict) -> bool:
        """同时更新任务状态和meta字段"""
        now = datetime.now().strftime(self.TIME_FORMAT)
        meta_json = json.dumps(new_meta)

        try:
            self.db_interface.begin_transaction()
            affected = self.db_interface.update(
                table=self.TABLE_NAME,
                set={
                    "status": new_status,
                    "meta": meta_json,
                    "updated_time": now
                },
                where={"id": {"=": task_id}}
            )
            self.db_interface.commit_transaction()
            return affected > 0
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"Failed to update task status and meta: {str(e)}")

    def add_task_with_sort(self, meta: Dict, status: int = 0, business_type: str = None) -> int:
        """添加任务并自动设置排序值"""
        try:
            self.db_interface.begin_transaction()
            
            # 获取当前最大排序值
            max_sort_result = self.db_interface.execute_custom_sql(
                sql="SELECT MAX(sort_order) as max_sort FROM " + self.TABLE_NAME
            )
            max_sort = max_sort_result[0]["max_sort"] if max_sort_result and max_sort_result[0]["max_sort"] is not None else 0
            
            # 插入新任务
            task_id = self.db_interface.insert(
                table=self.TABLE_NAME,
                data={
                    "status": status,
                    "meta": json.dumps(meta),
                    "created_time": datetime.now().strftime(self.TIME_FORMAT),
                    "updated_time": datetime.now().strftime(self.TIME_FORMAT),
                    "business_type": business_type,
                    "sort_order": max_sort + 1
                }
            )
            
            self.db_interface.commit_transaction()
            return task_id
            
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"Failed to add task with sort: {str(e)}")

    def update_log(self, task_id: int, log: str) -> bool:
        """更新任务日志"""
        try:
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                where={"id": {"=": task_id}}
            )
            
            if not result:
                return False
                
            task = result[0]
            meta = json.loads(task["meta"])
            if "logs" not in meta:
                meta["logs"] = []
            meta["logs"].append({
                "time": datetime.now().strftime(self.TIME_FORMAT),
                "content": log
            })
            
            affected = self.db_interface.update(
                table=self.TABLE_NAME,
                set={
                    "meta": json.dumps(meta),
                    "updated_time": datetime.now().strftime(self.TIME_FORMAT)
                },
                where={"id": {"=": task_id}}
            )
            
            return affected > 0
            
        except Exception as e:
            raise Exception(f"Failed to update task log: {str(e)}")

    def update_sort_order(self, task_id: int, sort_order: int) -> bool:
        """更新任务的排序值"""
        now = datetime.now().strftime(self.TIME_FORMAT)

        try:
            affected = self.db_interface.update(
                table=self.TABLE_NAME,
                set={
                    "sort_order": sort_order,
                    "updated_time": now
                },
                where={"id": {"=": task_id}}
            )
            return affected > 0
        except Exception as e:
            raise Exception(f"Failed to update task sort order: {str(e)}")

    def get_tasks_by_status(self, status: int) -> List[Dict]:
        """根据状态获取任务列表"""
        try:
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                where={"status": {"=": status}}
            )
            
            return [self._row_to_dict(row) for row in result]
            
        except Exception as e:
            raise Exception(f"Failed to get tasks by status: {str(e)}")

    def list_tasks_by_status(
            self,
            status: int,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """根据状态分页查询任务"""
        order_by = self._validate_order_field(order_by)
        offset = (page - 1) * per_page
        
        try:
            # 使用增强的DML进行分页查询
            order_direction = "ASC" if ascending else "DESC"
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                where={"status": {"=": status}},
                order_by=f"{order_by} {order_direction}",
                limit=per_page,
                offset=offset
            )
            
            return [self._row_to_dict(row) for row in result]
        except Exception as e:
            raise Exception(f"Failed to list tasks by status: {str(e)}")

    def count_by_status(self, status: int) -> int:
        """获取指定状态的记录数量"""
        try:
            result = self.db_interface.execute_custom_sql(
                sql="SELECT COUNT(*) as count FROM " + self.TABLE_NAME + " WHERE status = ?",
                params=[status]
            )
            return result[0]["count"] if result else 0
        except Exception as e:
            raise Exception(f"Failed to count tasks by status: {str(e)}")

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """根据ID获取任务"""
        try:
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                where={"id": {"=": task_id}}
            )
            
            if result:
                task = result[0]
                return {
                    "id": task["id"],
                    "status": task["status"],
                    "meta": json.loads(task["meta"]),
                    "created_time": task["created_time"],
                    "updated_time": task["updated_time"],
                    "business_type": task["business_type"],
                    "sort_order": task["sort_order"]
                }
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get task by ID: {str(e)}")

    def batch_update_status(self, task_ids: List[int], new_status: int) -> int:
        """批量更新任务状态"""
        if not task_ids:
            return 0

        now = datetime.now().strftime(self.TIME_FORMAT)

        try:
            affected = 0
            self.db_interface.begin_transaction()
            
            for task_id in task_ids:
                affected += self.db_interface.update(
                table=self.TABLE_NAME,
                set={
                    "status": new_status,
                    "updated_time": now
                },
                where={"id": {"=": task_id}}
            )
            
            self.db_interface.commit_transaction()
            return affected
        except Exception as e:
            self.db_interface.rollback_transaction()
            raise Exception(f"Failed to batch update task status: {str(e)}")

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        try:
            affected = self.db_interface.delete(
                table=self.TABLE_NAME,
                where={"id": {"=": task_id}}
            )
            return affected > 0
        except Exception as e:
            raise Exception(f"Failed to delete task: {str(e)}")

    def health_check(self) -> Tuple[bool, str]:
        """检查数据库连接状态"""
        try:
            self.db_interface.execute_custom_sql(
                sql=f"SELECT COUNT(*) FROM {self.TABLE_NAME}",
                params=[]
            )
            return True, "Database is healthy"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def list_all_tasks(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """分页查询所有任务"""
        order_by = self._validate_order_field(order_by)
        offset = (page - 1) * per_page
        
        try:
            # 使用增强的DML进行分页查询
            order_direction = "ASC" if ascending else "DESC"
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                order_by=f"{order_by} {order_direction}",
                limit=per_page,
                offset=offset
            )
            
            return [self._row_to_dict(row) for row in result]
        except Exception as e:
            raise Exception(f"Failed to list all tasks: {str(e)}")

    def count_all_tasks(self) -> int:
        """获取整个表格的总记录数"""
        try:
            result = self.db_interface.execute_custom_sql(
                sql=f"SELECT COUNT(*) as count FROM {self.TABLE_NAME}",
                params=[]
            )
            return result[0]["count"] if result else 0
        except Exception as e:
            raise Exception(f"Failed to count all tasks: {str(e)}")

    def advanced_search(
            self,
            status: Optional[int] = None,
            created_start: Optional[str] = None,
            created_end: Optional[str] = None,
            business_type: Optional[str] = None,
            meta_contains: Optional[Dict] = None,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> Tuple[List[Dict], int]:
        """高级分页搜索"""
        order_by = self._validate_order_field(order_by)
        try:
            conditions = {}
            
            # 状态条件
            if status is not None:
                conditions["status"] = {"=": status}
            
            # 业务类型条件
            if business_type is not None:
                conditions["business_type"] = {"=": business_type}
            
            # 创建时间条件
            if created_start or created_end:
                time_conditions = []
                if created_start:
                    time_conditions.append({"created_time": {">=": created_start + " 00:00:00"}})
                if created_end:
                    time_conditions.append({"created_time": {"<=": created_end + " 23:59:59"}})
                
                if len(time_conditions) > 1:
                    conditions["AND"] = time_conditions
                elif len(time_conditions) == 1:
                    conditions.update(time_conditions[0])
            
            # 获取总数
            total_tasks = self.db_interface.query(
                table=self.TABLE_NAME,
                where=conditions
            )
            
            # 应用meta_contains过滤
            filtered_tasks = []
            for task in total_tasks:
                task_dict = self._row_to_dict(task)
                
                # 应用meta_contains过滤
                if meta_contains:
                    match = True
                    for key, value in meta_contains.items():
                        if task_dict["meta"].get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_tasks.append(task_dict)
                else:
                    filtered_tasks.append(task_dict)
            
            # 排序
            reverse = not ascending
            filtered_tasks.sort(key=lambda x: x[order_by], reverse=reverse)
            
            # 分页处理
            total_count = len(filtered_tasks)
            offset = (page - 1) * per_page
            result = filtered_tasks[offset:offset + per_page]
            
            return result, total_count
        except Exception as e:
            raise Exception(f"Failed to perform advanced search: {str(e)}")

    def parse_datetime(self, dt_str: str) -> datetime:
        """将数据库时间字符串解析为datetime对象"""
        return datetime.strptime(dt_str, self.TIME_FORMAT)

    def format_datetime(self, dt: datetime) -> str:
        """将datetime对象格式化为数据库字符串"""
        return dt.strftime(self.TIME_FORMAT)

    def list_tasks_created_between(
            self,
            start_time: str,
            end_time: str,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """获取指定时间段内创建的任务"""
        order_by = self._validate_order_field(order_by)
        offset = (page - 1) * per_page
        
        try:
            order_direction = "ASC" if ascending else "DESC"
            result = self.db_interface.query(
                table=self.TABLE_NAME,
                where={
                    "AND": [
                        {"created_time": {">=": start_time}},
                        {"created_time": {"<=": end_time}}
                    ]
                },
                order_by=f"{order_by} {order_direction}",
                limit=per_page,
                offset=offset
            )
            
            return [self._row_to_dict(row) for row in result]
        except Exception as e:
            raise Exception(f"Failed to list tasks created between: {str(e)}")

    def list_tasks_by_business_type(self, business_type: str, 
                                 order_by: str = "created_time", limit: int = None, 
                                 offset: int = None) -> List[Dict]:
        """按业务类型查询任务"""
        order_by = self._validate_order_field(order_by)
        
        try:
            conditions = {"business_type": {"=": business_type}}
            
            tasks = self.db_interface.query(
                table=self.TABLE_NAME,
                where=conditions,
                order_by=f"{order_by} ASC",
                limit=limit,
                offset=offset
            )
            
            return [self._row_to_dict(task) for task in tasks]
        except Exception as e:
            raise Exception(f"Failed to list tasks by business type: {str(e)}")

    def count_tasks_by_business_type(self, business_type: str) -> int:
        """统计指定业务类型的任务数量"""
        try:
            result = self.db_interface.execute_custom_sql(
                sql="SELECT COUNT(*) as count FROM " + self.TABLE_NAME + " WHERE business_type = ?",
                params=[business_type]
            )
            return result[0]["count"] if result else 0
        except Exception as e:
            raise Exception(f"Failed to count tasks by business type: {str(e)}")

    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典格式"""
        return {
            "id": row["id"],
            "status": int(row["status"]),
            "meta": json.loads(row["meta"]),
            "created_time": row["created_time"],
            "updated_time": row["updated_time"],
            "business_type": row["business_type"],
            "sort_order": row["sort_order"]
        }

    def close(self) -> None:
        """关闭数据库连接"""
        self.db_interface.close()
    
    def is_custom_sql_supported(self) -> bool:
        """检查当前数据库实现是否支持自定义SQL执行
        
        Returns:
            如果支持自定义SQL执行返回True，否则返回False
        """
        from xianbao.core.CustomSQLInterface import CustomSQLInterface
        return isinstance(self.db_interface, CustomSQLInterface)
    
    def execute_custom_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义SQL查询语句（DML）
        
        Args:
            sql: 要执行的SQL语句
            params: SQL参数元组，用于参数化查询
            
        Returns:
            查询结果列表，每个元素是一个字典，键为列名，值为对应的数据
            
        Raises:
            NotImplementedError: 当数据库实现不支持自定义SQL执行时
            Exception: 当SQL执行失败时
        """
        if not self.is_custom_sql_supported():
            raise NotImplementedError("当前数据库实现不支持自定义SQL执行")
        
        return self.db_interface.execute_custom_sql(sql, params)
    
    def execute_custom_update(self, sql: str, params: tuple = None) -> int:
        """执行自定义更新语句（DML/DDL）
        
        Args:
            sql: 要执行的SQL语句（UPDATE, INSERT, DELETE, DDL等）
            params: SQL参数元组，用于参数化查询
            
        Returns:
            受影响的行数（对于DML语句）或0（对于DDL语句）
            
        Raises:
            NotImplementedError: 当数据库实现不支持自定义SQL执行时
            Exception: 当SQL执行失败时
        """
        if not self.is_custom_sql_supported():
            raise NotImplementedError("当前数据库实现不支持自定义SQL执行")
        
        return self.db_interface.execute_custom_update(sql, params)
        