
import json
import os
from datetime import datetime
from textwrap import indent
from typing import Dict, Any, Optional
from xianbao.core.ast import QueryBuilder
from xianbao.core.Task import TaskManager
from xianbao.core.DatabaseFactory import DatabaseFactory
from xianbao.core.DatabaseLanguageEnhanced import AdvancedDatabaseLanguageFactory
from xianbao.core.QueueFactory import QueueFactory
from xianbao.core.ProcessQueueInterface import ProcessQueueInterface


def initialize_service(host: str='http://localhost:5000') -> Dict[str, Any]:
    """
    初始化服务组件，使用工厂模式创建数据库和队列实例
    
    Args:
        _db_path: 数据库路径
        db_type: 数据库类型 ('sqlite' 或 'http_sqlite')
        queue_type: 队列类型 ('sqlite', 'http', 'http_lock')
    
    Returns:
        包含服务组件的字典
    """

    # 创建数据库实例
    db_config = { 'base_url': host, 'use_lock': False }

    database = DatabaseFactory.create_database('http_sqlite', db_config)
    
    # 创建数据库语言元组 (DDL, DML)
    db_language = AdvancedDatabaseLanguageFactory.create('http_sqlite')
    
    # 创建任务管理器
    task_manager = TaskManager(
        db_interface=database,
        db_language=db_language,
        table_name='tasks'
    )
    
    # 创建队列实例    
    queue_config = { 'base_url': host, 'use_lock': True, 'table_name': 'entering_queue' }
        
    
    queue = QueueFactory.create_queue('http_lock', **queue_config)
    
    return {
        # 'db_path': db_config['db_path'],
        # 'lock_path': queue_config.get('lock_path', ''),
        'task_manager': task_manager,
        'queue': queue
        # 'database': database,
        # 'db_language': db_language
    }


def _scan_task_production(task_manager, queue):
    """
    生产待录入表单的任务。
    状态：全部图片入库成功、识别成功、未走过录入流程
    使用AST模块优化查询条件
    :return: None
    """
    
    # 使用QueryBuilder构建复杂查询
    builder = QueryBuilder('tasks')
    
    # 入库成功 + 识别成功 (status & 0b1011110110000000 = 0b1011110110000000)
    # 未录入状态 (status & 0b0000000001100000 = 0)
    # 参考号识别错误 (status & 0b0000000000010000 = 0)
    
    # 使用位运算条件
    conditions = {
        'AND': [
            {'status': {'&': int('1011110110000000', 2)}},
            {'status': {'&': int('0000000001100000', 2), '=': 0}},
            {'status': {'&': int('0000000000010000', 2), '=': 0}}
        ]
    }
    
    sql, params = builder.select('*').where(**conditions).to_sql()
    
    # 使用TaskManager的底层数据库接口执行查询
    tasks = task_manager.execute_custom_sql(sql, params)
    
    for task in tasks:
        task['meta'] = json.loads(task['meta'])
        queue.put(json.dumps(task, ensure_ascii=False, indent=2))


def _scan_task_get(queue):
    """
    获取待识别任务，并返回消费。
    :return:
    """
    return json.loads(queue.get(indent=2))


def _update_success_task(task_id: int, task_manager):
    """
    交易信息录入成功。
    使用AST模块优化状态更新
    :param task_id: 
    :return: 
    """
    from xianbao.core.ast import update
    
    # 计算要清除的标志位
    clear_flags = int('1000000', 2) | int('10000', 2)
    
    # 使用AST模块构建更新语句
    sql, params = update(**{
        'table': 'tasks',
        'set': {'status': {'&~': clear_flags}},  # 使用位清除操作
        'where': {'id': task_id}
    })
    
    # 执行更新
    task_manager.execute_custom_update(sql, params)


def _update_fail_task(task_id: int, error_msg: str, task_manager):
    """
    交易信息录入失败。
    使用AST模块优化状态更新和日志记录
    :param task_id: 
    :param error_msg: 
    :return: 
    """
    from xianbao.core.ast import update
    
    # 设置失败标志位
    fail_flag = int('100000', 2)
    
    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 使用AST模块构建更新语句
    sql, params = update(**{
        'table': 'tasks',
        'set': {
            'status': {'|': fail_flag},  # 设置失败标志
            'log': {'||': f'[{current_time}] {error_msg}'},  # 追加日志
            'updated_time': current_time
        },
        'where': {'id': task_id}
    })
    
    # 执行更新
    task_manager.execute_custom_update(sql, params)


def _update_invoice_meta(task_id: int, u_meta: dict, task_manager):
    """
    完善发票信息
    使用AST模块优化元数据更新
    :param task_id 任务Id
    :param u_meta 待修改的发票信息
    :return
    """
    from xianbao.core.ast import select, update
    
    # 首先获取当前任务的元数据
    sql, params = select(**{
        'table': 'tasks',
        'fields': ['meta'],
        'where': {'id': task_id}
    })
    
    result = task_manager.execute_custom_sql(sql, params)
    if not result:
        raise ValueError(f"任务 {task_id} 不存在")
    
    current_meta = json.loads(result[0]['meta'])
    
    # 更新发票信息
    if 'invoice_info' not in current_meta:
        current_meta['invoice_info'] = {}
    
    current_meta['invoice_info'].update({
        '发票金额': u_meta['发票金额'],
        '销售企业名称': u_meta['销售企业名称'],
        '统一社会信用代码': u_meta['统一社会信用代码']
    })
    
    # 使用AST模块构建更新语句
    sql, params = update(**{
        'table': 'tasks',
        'set': {
            'meta': json.dumps(current_meta, ensure_ascii=False),
            'updated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'where': {'id': task_id}
    })
    
    # 执行更新
    task_manager.execute_custom_update(sql, params)


def fetch_transdate(meta: dict):
    """
    从meta中获取银联小票信息。
    :param meta:
    :return:
    """
    ums_receipt = meta['ums_receipt_info']
    dt_obj = datetime.strptime(ums_receipt['日期时间'], "%Y-%m-%d %H:%M:%S")
    return dt_obj.strftime("%Y/%m/%d")


def fetch_work_folder(entering_task_meta: dict, work_folder: str):
    """
    返回客户的交易信息目录，目录里边包含待回填的所有交易进行。
    :param entering_task_meta: 待回填的消费meta
    :param work_folder: 工作空间
    :return:
    """
    return os.path.join(work_folder, entering_task_meta['relative_path'].strip('\\').strip('/'))


def fetch_area_by_delivery_info(meta: dict):
    """
    从送货单信息（delivery_info）中获取所在区域
    :param meta:
    :return: { 市, 区 }
    """
    area = meta['delivery_info']['地区']
    idx = area.find('市')
    city = area[:idx + 1]
    district = area[idx + 1:]
    return {
        'city': city,
        'district': district
    }


def queue_size(queue: ProcessQueueInterface) -> int:
    """
    获取队列大小
    :param queue: 队列实例
    :return: 队列中的任务数量
    """
    return queue.qsize()


# 向后兼容的别名
__init__ = initialize_service
