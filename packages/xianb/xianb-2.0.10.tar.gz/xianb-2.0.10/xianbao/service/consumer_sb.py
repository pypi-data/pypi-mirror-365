import json
import re
import pandas as pd
import os
import shutil
from xianbao import TaskManager, FileScanner, DictManager, QueueFactory, DatabaseFactory, AdvancedDatabaseLanguageFactory


def __init__(_host: str, _order_file: str, _commondity_store: str, _work_path: str):
    db_config = { 'base_url': _host, 'use_lock': False }
    commondity_cache = _commondity_store
    database = DatabaseFactory.create_database('http_sqlite', db_config)
    # 创建数据库语言元组 (DDL, DML)
    db_language = AdvancedDatabaseLanguageFactory.create('http_sqlite')
    # 初始化资源
    task_manager = TaskManager(db_interface=database, db_language=db_language)

     # 创建队列实例    
    queue_config = { 'base_url': _host, 'use_lock': True, 'table_name': 'discen_queue' }
    
    queue = QueueFactory.create_queue('http_lock', **queue_config)

    dict_manager = DictManager(db_interface=database, db_language=db_language)

    order_df = pd.read_excel(order_path, dtype=str)
    file_list = FileScanner.catalog_deep_list(commondity_store, 5)
    commondity_cache = classify_files(file_list)

    return {
        'task_manager': task_manager,
        'queue': queue,
        'dict_manager': dict_manager,
        'order_df': order_df,
        'file_list': file_list,
        'commondity_cache': commondity_cache
    }
    