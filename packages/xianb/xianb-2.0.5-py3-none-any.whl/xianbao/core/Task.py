
from xianbao.core.TaskApi import TaskApi
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from xianbao.core.DatabaseInterface import DatabaseInterface


class TaskManager:
    """任务管理器 - 基于TaskApi实现"""

    def __init__(self, db_interface: DatabaseInterface, db_language: tuple, table_name: str = "tasks") -> None:
        """初始化任务管理器"""
        self.task_api = TaskApi(table_name=table_name, db_language=db_language, db_interface=db_interface)
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def close(self) -> None:
        """关闭数据库连接"""
        self.task_api.close()



    def add_task(self, meta: Dict, business_type: str, status: int = 0) -> int:
        """添加新任务"""
        return self.task_api.add_task(meta, business_type, status)

    def update_status(self, task_id: int, new_status: int) -> bool:
        """更新任务状态"""
        return self.task_api.update_status(task_id, new_status)

    def update_status_and_meta(self, task_id: int, new_status: int, new_meta: Dict) -> bool:
        """同时更新任务状态和meta字段"""
        return self.task_api.update_status_and_meta(task_id, new_status, new_meta)

    def add_task_with_sort(self, meta: Dict, status: int = 0, business_type: str = None) -> int:
        """添加任务并自动设置排序值"""
        return self.task_api.add_task_with_sort(meta, status, business_type)

    def update_log(self, task_id: int, log: str) -> bool:
        """更新任务日志"""
        return self.task_api.update_log(task_id, log)

    def update_sort_order(self, task_id: int, sort_order: int) -> bool:
        """更新任务的排序值"""
        return self.task_api.update_sort_order(task_id, sort_order)

    def list_tasks_by_status(
            self,
            status: int,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """根据状态分页查询任务"""
        return self.task_api.list_tasks_by_status(status, page, per_page, order_by, ascending)

    def count_by_status(self, status: int) -> int:
        """获取指定状态的记录数量"""
        return self.task_api.count_by_status(status)

    def get_task(self, task_id: int) -> Optional[Dict]:
        """根据ID获取单个任务详情"""
        return self.task_api.get_task(task_id)

    def batch_update_status(self, task_ids: List[int], new_status: int) -> int:
        """批量更新任务状态"""
        return self.task_api.batch_update_status(task_ids, new_status)

    def delete_task(self, task_id: int) -> bool:
        """删除指定任务"""
        return self.task_api.delete_task(task_id)

    def health_check(self) -> Tuple[bool, str]:
        """检查数据库连接状态"""
        return self.task_api.health_check()

    def list_all_tasks(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """分页查询所有任务"""
        return self.task_api.list_all_tasks(page, per_page, order_by, ascending)

    def count_all_tasks(self) -> int:
        """获取整个表格的总记录数"""
        return self.task_api.count_all_tasks()

    def advanced_search(
            self,
            status: Optional[int] = None,
            created_start: Optional[str] = None,
            created_end: Optional[str] = None,
            meta_contains: Optional[Dict] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Tuple[List[Dict], int]:
        """高级分页搜索"""
        return self.task_api.advanced_search(status, created_start, created_end, meta_contains, page, per_page)

    def parse_datetime(self, dt_str: str) -> datetime:
        """解析时间字符串为datetime对象"""
        return datetime.strptime(dt_str, self.TIME_FORMAT)

    def format_datetime(self, dt: datetime) -> str:
        """格式化datetime对象为字符串"""
        return dt.strftime(self.TIME_FORMAT)

    def list_tasks_created_between(self, start_time: datetime, end_time: datetime, 
                                order_by: str = "created_time", limit: int = None, 
                                offset: int = None) -> List[Dict]:
        """查询时间段内创建的任务"""
        return self.task_api.list_tasks_created_between(start_time, end_time, order_by, limit, offset)

    def list_tasks_by_business_type(self, business_type: str, 
                                 order_by: str = "created_time", limit: int = None, 
                                 offset: int = None) -> List[Dict]:
        """按业务类型查询任务"""
        return self.task_api.list_tasks_by_business_type(business_type, order_by, limit, offset)

    def count_tasks_by_business_type(self, business_type: str) -> int:
        """统计业务类型任务数量"""
        return self.task_api.count_tasks_by_business_type(business_type)

    def execute_custom_sql(self, sql: str, params: tuple = ()) -> List[Dict]:
        """执行自定义SQL查询（注意SQL注入风险）"""
        return self.task_api.execute_custom_sql(sql, params)

    def execute_custom_update(self, sql: str, params: tuple = ()) -> int:
        """执行自定义SQL更新（注意SQL注入风险）"""
        return self.task_api.execute_custom_update(sql, params)
