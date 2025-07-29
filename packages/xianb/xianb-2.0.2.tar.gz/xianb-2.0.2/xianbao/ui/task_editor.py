from .meta_form import MetaFormDialog

class TaskEditor:
    """任务编辑器"""
    
    def __init__(self, task_table):
        self.task_table = task_table
        self.tree = task_table.tree
        
    def edit(self):
        """编辑任务"""
        selected = self.tree.selection()
        if selected:
            task_item = self.tree.item(selected[0])
            task_id = task_item["values"][0]
            meta_data = task_item["values"][-1] if len(task_item["values"]) > 5 else "{}"
            MetaFormDialog.show(self.task_table.master, meta_data, task_id=task_id)
            # 等待对话框关闭后刷新表格
            self.task_table.master.after(100, self.task_table.load_tasks)