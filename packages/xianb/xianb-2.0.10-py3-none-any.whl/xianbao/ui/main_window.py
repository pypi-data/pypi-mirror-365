import tkinter as tk
from tkinter import ttk
from xianbao.core.context import global_context
from .task_table import TaskTable
from .scan_material_window import ScanMaterialWindow
from .backfill_tab import BackfillTab
from .reconciliation_tab import ReconciliationTab


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("宜家RPA任务管理系统")
        self.geometry("1000x700")
        # 创建主布局
        self.create_main_layout()
        
    def create_main_layout(self):
        """创建主界面布局"""
        # 中部 - 标签页容器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 任务管理标签页
        self.task_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_frame, text="任务管理")
        
        # 添加任务表格到任务管理标签页
        self.task_table = TaskTable(self.task_frame)
        self.task_table.pack(fill=tk.BOTH, expand=True)
        
        # 定时器管理标签页
        # self.timer_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.timer_frame, text="定时器管理")
        
        # 添加定时器管理器到定时器标签页
        # self.timer_manager = TimerManager(self.timer_frame)
        # self.timer_manager.pack(fill=tk.BOTH, expand=True)
        
        # 扫描交易材料标签页
        self.scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scan_frame, text="扫描交易材料")
        self.scan_material = ScanMaterialWindow(self.scan_frame)
        self.scan_material.pack(fill=tk.BOTH, expand=True)
        
        # 数据回填标签页
        self.backfill_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backfill_frame, text="数据回填")
        self.backfill_tab = BackfillTab(self.backfill_frame)
        self.backfill_tab.pack(fill=tk.BOTH, expand=True)
        
        # 对账回填标签页
        self.recon_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recon_frame, text="对账回填")
        self.reconciliation_tab = ReconciliationTab(self.recon_frame)
        self.reconciliation_tab.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
