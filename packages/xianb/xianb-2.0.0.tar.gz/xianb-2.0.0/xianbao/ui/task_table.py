import tkinter as tk
from tkinter import ttk
from xianbao.core.context import global_context
from xianbao.ui.status_visualization import StatusVisualization
from .task_detail_viewer import TaskDetailViewer
from .task_editor import TaskEditor
from .task_deleter import TaskDeleter

class TaskTable(ttk.Frame):
    """任务表格组件"""
    
    def __init__(self, master=None, business_type_combo=None, **kwargs):
        super().__init__(master, **kwargs)
        self.business_type_combo = business_type_combo
        # 初始化状态可视化组件
        self.status_viz = StatusVisualization(self)
        self.task_manager = global_context.get('task_manager')
        self.status_viz.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()
        self.load_tasks()
        
    def create_widgets(self):
        """创建表格和滚动条"""
        # 表格列定义
        columns = ["ID", "业务类型", "创建时间", "更新时间", "状态"]
        
        # 创建顶部查询和分页控件
        self.create_query_controls()
        self.create_pagination_controls()
        
        # 创建表格
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        # 设置列标题和宽度
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加垂直滚动条
        yscroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        
        # 配置网格布局
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 右键菜单
        self.create_context_menu()
        
    def create_context_menu(self):
        """创建右键菜单"""
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="查看详情", command=self.show_task_detail)
        # self.menu.add_command(label="查看JSON详情", command=self.show_json_detail)
        self.menu.add_command(label="编辑任务", command=self.edit_task)
        self.menu.add_separator()
        self.menu.add_command(label="删除任务", command=self.delete_task)
        
        # 绑定事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-1>", self.on_task_select)
        
    def on_task_select(self, event):
        """任务选择事件"""
        item = self.tree.identify_row(event.y)
        if item:
            selected_task = self.tree.item(item, "values")
            if selected_task and len(selected_task) > 4:
                # 通知主窗口更新状态可视化
                self.status_viz.update_status(int(selected_task[4]))
    
    def update_business_type_combo(self, tasks):
        """更新业务类型下拉框"""
        business_types = set(task["business_type"] for task in tasks if task["business_type"])
        if business_types:
            self.business_type_combo["values"] = list(business_types)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
        
    def create_query_controls(self):
        """创建查询控件"""
        query_frame = ttk.Frame(self)
        query_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 业务类型筛选
        ttk.Label(query_frame, text="业务类型:").pack(side=tk.LEFT)
        self.business_type_combo = ttk.Combobox(query_frame, width=15)
        self.business_type_combo.pack(side=tk.LEFT, padx=5)
        
        # 状态筛选
        ttk.Label(query_frame, text="状态:").pack(side=tk.LEFT)
        self.status_combo = ttk.Combobox(query_frame, 
                                      values=["全部", "已完成", "待处理"], 
                                      width=10)
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.set("全部")
    
    def create_pagination_controls(self):
        """创建分页控制组件"""
        pagination_frame = ttk.Frame(self)
        pagination_frame.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        
        # 页码选择
        ttk.Label(pagination_frame, text="页码:").pack(side=tk.LEFT)
        self.page_entry = ttk.Entry(pagination_frame, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        self.page_entry.insert(0, "1")
        
        # 每页数量
        ttk.Label(pagination_frame, text="每页:").pack(side=tk.LEFT)
        self.per_page_combo = ttk.Combobox(pagination_frame, 
                                         values=[10, 20, 50, 100], 
                                         width=5)
        self.per_page_combo.pack(side=tk.LEFT, padx=5)
        self.per_page_combo.set(100)
        
        # 查询按钮
        ttk.Button(pagination_frame, 
                  text="查询", 
                  command=self.load_tasks).pack(side=tk.LEFT)
    
    def load_tasks(self, page=None, per_page=None, status=None, business_type=None):
        """加载任务数据"""
        # 获取查询参数
        try:
            page = int(self.page_entry.get() or 1) if page is None else page
            per_page = int(self.per_page_combo.get()) if per_page is None else per_page
            status_filter = self.status_combo.get()
            business_type = self.business_type_combo.get() or business_type
        except ValueError:
            return
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 查询任务
        if status is not None or business_type is not None:
            tasks, _ = self.task_manager.advanced_search(
                status=status,
                business_type=business_type,
                page=page,
                per_page=per_page
            )
        else:
            tasks = self.task_manager.list_all_tasks(page=page, per_page=per_page)
        
        # 填充表格
        for task in tasks:
            self.tree.insert("", tk.END, values=(
                task["id"],
                task["business_type"],
                task["created_time"],
                task["updated_time"],
                task["status"],
                task.get("meta", "")
            ))
            
        # 更新业务类型下拉框
        self.update_business_type_combo(tasks)

        # 更新状态可视化
        if self.tree.selection():
            selected_task = self.tree.item(
                self.tree.selection()[0], "values")
            self.status_viz.update_status(int(selected_task[4]))
    
    def show_task_detail(self):
        """显示任务详情"""
        TaskDetailViewer(self).show()
            
    def edit_task(self):
        """编辑任务"""
        TaskEditor(self).edit()
            
    def delete_task(self):
        """删除任务"""
        TaskDeleter(self).delete()
        """删除任务"""
        selected = self.tree.selection()
        if selected:
            task_id = self.tree.item(selected[0], "values")[0]
            # TODO: 实现删除确认和操作
