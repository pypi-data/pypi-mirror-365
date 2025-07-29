import tkinter as tk
import threading
import datetime
import json
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from xianbao.core.context import global_context
from xianbao.service.rpa_backfilling_qk import ExcelWriter
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler


class BackfillTab(ttk.Frame):
    """
    数据回填功能的主界面类，继承自ttk.Frame
    
    Args:
        parent: 父窗口组件
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.task_manager = global_context.get('task_manager')  # 任务管理器实例
        if self.task_manager is None:
            raise Exception("任务管理器未初始化")
        self.is_running = False  # 任务运行状态标志
        self.create_widgets()  # 创建界面组件
        self.load_params()  # 加载保存的参数
        
    def load_params(self):
        """
        从字典中加载保存的参数
        """
        dict_manager = global_context['dict_manager']
        
        # 获取保存的参数
        params = dict_manager.get_dict_items("backfill_params")
        if params:
            try:
                param_dict = json.loads(params[0]["value"])
                self.cron_entry.delete(0, tk.END)
                self.cron_entry.insert(0, param_dict.get("cron_expr", "0 9 * * *"))
                self.file_label.config(text=param_dict.get("excel_path", "未选择文件"))
            except Exception as e:
                print(f"加载参数失败: {e}")
        
    def create_widgets(self):
        """
        创建并布局所有界面组件
        """
        # Cron表达式输入
        ttk.Label(self, text="Cron表达式:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cron_entry = ttk.Entry(self, width=30)
        self.cron_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.cron_entry.insert(0, "0 9 * * *")  # 默认每天9点执行
        
        # Excel文件选择
        ttk.Button(self, text="选择RPA回填文件", command=self.select_file).grid(row=1, column=0, padx=5, pady=5)
        self.file_label = ttk.Label(self, text="未选择文件")
        self.file_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 按钮容器框架
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=3, sticky="we")
        
        # 保存配置按钮
        self.save_btn = ttk.Button(self.btn_frame, text="保存配置", command=self.save_params, width=12)
        self.save_btn.pack(side="left", expand=False, padx=3)
        
        # 同步按钮
        self.sync_btn = ttk.Button(self.btn_frame, text="同步数据", command=self.start_backfill, width=12)
        self.sync_btn.pack(side="left", expand=False, padx=3)
        
        # 定时任务生效按钮
        self.schedule_btn = ttk.Button(self.btn_frame, text="定时任务", command=self.toggle_schedule, width=12)
        self.schedule_btn.pack(side="left", expand=False, padx=3)
        
        # 定时任务状态标识
        self.schedule_status = ttk.Label(self, text="定时任务状态: 未生效", padding=(5, 5))
        self.schedule_status.grid(row=3, column=1, columnspan=5, padx=5, pady=5, sticky="we")
        
        # 添加空行分隔
        ttk.Label(self).grid(row=3)
        
        # 状态标签
        self.status_label = ttk.Label(self, text="状态: 空闲")
        self.status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # 日志框
        self.log_text = ScrolledText(self, height=15, state="disabled")
        self.log_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)
    
    def select_file(self):
        """
        打开文件选择对话框，选择Excel数据源文件
        """
        # 确保在主线程中处理文件对话框
        self.after(100, lambda: self._process_file_selection())
        
    def _process_file_selection(self):
        """
        实际处理文件选择的内部方法
        """
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel文件", ".xlsx .xlsm")],
                title="选择Excel文件"
            )
            if file_path:
                self.file_label.config(text=file_path)  # 更新文件路径显示
        except Exception as e:
            messagebox.showerror("错误", f"文件选择失败: {str(e)}")
    
    def save_params(self):
        """
        保存当前配置参数到字典
        """
        # 验证Cron表达式
        cron_expr = self.cron_entry.get()
        # 验证Excel文件路径
        excel_path = self.file_label.cget("text")
        if not excel_path or excel_path == "未选择文件":
            messagebox.showerror("错误", "请先选择Excel文件")
            return
            
        # 保存参数到字典
        dict_manager = global_context['dict_manager']
        
        # 检查是否已存在相同配置
        # 确保字典类型存在
        if not dict_manager.get_dict_type_by_code("backfill_params"):
            dict_manager.add_dict_type("回填参数", "backfill_params", "RPA回填任务参数")
            
        existing_data = dict_manager.get_dict_items("backfill_params")
        params = {
            "cron_expr": cron_expr,
            "excel_path": excel_path
        }
        
        if existing_data:
            # 更新现有配置
            dict_manager.update_dict_item("backfill_params", existing_data[0]["key"], json.dumps(params))
        else:
            # 创建新配置
            dict_manager.add_dict_item("backfill_params", "default", json.dumps(params))
        
        messagebox.showinfo("成功", "参数已保存")
        
    def toggle_schedule(self):
        """
        切换定时任务状态
        """
        if not hasattr(self, 'scheduler'):
            self.scheduler = BackgroundScheduler()
            self.scheduler.start()
            self.is_scheduled = False
        
        if self.is_scheduled:
            # 取消定时任务
            self.scheduler.remove_job('rpa_backfill_job')
            self.is_scheduled = False
            self.schedule_status.config(text="定时任务: 未生效")
            return
        
        # 设置定时任务
        cron_expr = self.cron_entry.get()
        try:
            # 验证Cron表达式
            # croniter.croniter(cron_expr)
            print(f"尝试添加定时任务，Cron表达式: {cron_expr}")
            params = self.parse_cron_expr(cron_expr)
            # 添加定时任务
            self.scheduler.add_job(
                self.start_backfill,
                trigger=CronTrigger(
                    second=params['second'],
                    minute=params['minute'],
                    hour=params['hour'],
                    day=params['day'],
                    month=params['month'],
                    day_of_week=params['day_of_week']
                ),
                id='rpa_backfill_job'
            )
            print("定时任务添加成功")
            self.is_scheduled = True
            self.schedule_status.config(text="定时任务: 已生效")
        except Exception as e:
            messagebox.showerror("错误", f"定时任务设置失败: {str(e)}")
            print(f"定时任务设置失败: {str(e)}")
            
    def parse_cron_expr(self, cron_expr):
        """
        解析Cron表达式为APScheduler参数
        """
        parts = cron_expr.split()
        
        # 确保有6个部分
        if len(parts) != 6:
            raise ValueError("Cron表达式必须包含6个部分")
            
        # 处理特殊字符*，转换为None
        params = {} 
        params['second'] = parts[0]
        params['minute'] = parts[1]
        params['hour'] = parts[2]
        params['day'] = parts[3]
        params['month'] = parts[4]
        params['day_of_week'] = parts[5]
        return params
    
    def start_backfill(self):
        """
        启动数据回填任务
        
        验证输入参数后，创建后台线程执行回填任务
        """
        if self.is_running:
            return  # 防止重复启动
            
        # 验证Excel文件路径
        excel_path = self.file_label.cget("text")
        if not excel_path or excel_path == "未选择文件":
            messagebox.showerror("错误", "请先选择Excel文件")
            return
        
            
        # 更新状态并禁用按钮
        self.is_running = True
        self.status_label.config(text="状态: 运行中")
        self.sync_btn.config(state="disabled")
        
        # 创建并启动后台线程
        thread = threading.Thread(target=self.run_backfill, args=(excel_path,))
        thread.daemon = True  # 设置为守护线程
        thread.start()
    
    def run_backfill(self, excel_path):
        """
        执行数据回填任务的核心方法
        
        Args:
            excel_path: Excel数据源文件路径
        """
        excel_writer = ExcelWriter(xlsx_path=excel_path, db_path=self.db_path)  # 创建处理器实例
        page = 1
        per_page = 1000  # 每页处理1000条任务
        
        # 分页处理所有任务
        while True:
            tasks = self.rpa_backfilling(page, per_page)  # 获取任务列表
            if not tasks:
                break  # 没有更多任务时退出循环
                
            # 处理当前页的所有任务
            for task in tasks:
                try:
                    excel_writer.write_to_excel(task)  # 执行单个任务
                    self.update_log(f"处理任务成功，任务ID: {str(task['id'])}")
                except Exception as e:
                    self.update_log(f"处理任务失败: {str(e)}，任务ID: {str(task['id'])}")
            
            page += 1  # 处理下一页

        excel_writer.close()

        # 任务完成后恢复界面状态
        self.is_running = False
        self.status_label.config(text="状态: 空闲")
        self.sync_btn.config(state="normal")
        self.update_log("所有任务处理完成")

    def rpa_backfilling(self, page=1, per_page=1000):
        """
        分页获取任务列表
        
        Args:
            page: 当前页码
            per_page: 每页记录数
            
        Returns:
            当前页的任务列表
        """
        offset = (page - 1) * per_page
        query = "SELECT * FROM tasks ORDER BY created_time DESC LIMIT ? OFFSET ?"
        params = (per_page, offset)
        
        tasks = self.task_manager.execute_custom_sql(query, params)
        
        # 反序列化meta字段
        for task in tasks:
            if 'meta' in task and task['meta']:
                task['meta'] = json.loads(task['meta'])
                
        return tasks
    
    def update_log(self, message):
        """
        更新日志显示区域
        
        Args:
            message: 要显示的日志消息
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # 更新日志文本框内容
        self.log_text.config(state="normal")
        self.log_text.insert("end", log_message)
        self.log_text.see("end")  # 自动滚动到底部
        self.log_text.config(state="disabled")
        