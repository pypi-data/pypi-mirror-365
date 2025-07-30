"""
状态说明:
银联小票是否入库,宜家小票是否入库,发票是否入库,送货单是否入库,商品图片是否入库,银联小票是否识别,宜家小票是否识别,发票是否识别,送货单是否识别,预留,预留,预留,预留,预留,预留,预留
"""
import os
import json
from xianbao.core.ast import QueryBuilder
from xianbao import DatabaseFactory, QueueFactory, AdvancedDatabaseLanguageFactory, TaskManager


def scan_task_production(host: str = "http://localhost:5000") -> list:
    """
    生产待识别图片的任务。
    识别条件：银联小票、宜家小票（不需要）、发票、送货单全部入库成功，并且存在图片还未识别。
    :param host: HTTP服务地址
    :return: 任务列表
    """
    
    # 使用DatabaseFactory创建HTTP数据库实例
    db_instance = DatabaseFactory.create_database('http_sqlite', {
        'base_url': host,
        'use_lock': True
    })
    
    # 使用DatabaseLanguageEnhanced工厂类获取DDL和DML
    ddl, dml = AdvancedDatabaseLanguageFactory.create()
    
    # 创建TaskManager实例
    task_manager = TaskManager(db_interface=db_instance, db_language=(ddl, dml))
    
    # 使用QueueFactory创建HTTP进程安全队列
    queue = QueueFactory.create_queue(
        'http',
        base_url=host,
        table_name='discern_queue'
    )

    if queue.qsize() > 0:
        # 如果任务队列不为空，不需要添加
        queue.close()
        db_instance.close()
        return []

    # 使用QueryBuilder构建复杂查询
    builder = QueryBuilder('tasks')
    
    # 成功入库
    s1 = int('1011000000000000', 2)
    # 未识别
    s2 = int('0000010110000000', 2)
    # 参考号识别错误
    s3 = int('0000000000010000', 2)

    tasks = task_manager.execute_custom_sql(
        """
        SELECT
            *
        FROM tasks WHERE 
            (status & ? = ? AND status & ? != ?) OR (status & ? = ?)
        """,
        (s1, s1, s2, s2, s3, s3)
    )
    
    for task in tasks:
        task['meta'] = json.loads(task['meta'])
        queue.put(json.dumps(task).encode('utf-8'))
    
    # 清理资源
    queue.close()
    db_instance.close()
    
    return tasks
