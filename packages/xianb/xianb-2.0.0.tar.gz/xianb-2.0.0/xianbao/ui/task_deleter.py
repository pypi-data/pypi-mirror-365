import tkinter as tk
from tkinter import messagebox

class TaskDeleter:
    """任务删除器"""
    
    def __init__(self, task_table):
        self.task_table = task_table
        self.tree = task_table.tree
        self.task_manager = task_table.task_manager
        
    def delete(self):
        """删除任务"""
        selected = self.tree.selection()
        if selected:
            task_item = self.tree.item(selected[0])
            task_id = task_item["values"][0]
            
            if messagebox.askyesno("确认删除", f"确定要删除任务 {task_id} 吗？"):
                self.task_manager.delete_task(task_id)
                self.task_table.load_tasks()