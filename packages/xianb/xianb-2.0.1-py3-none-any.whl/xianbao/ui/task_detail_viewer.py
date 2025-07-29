from .meta_form import MetaFormDialog

class TaskDetailViewer:
    """任务详情查看器"""
    
    def __init__(self, task_table):
        self.task_table = task_table
        self.tree = task_table.tree
        
    def show(self):
        """显示任务详情"""
        selected = self.tree.selection()
        if selected:
            task_data = self.tree.item(selected[0])
            if 'values' in task_data and len(task_data['values']) > 0:
                MetaFormDialog.show(self.task_table.master, task_data['values'][-1])