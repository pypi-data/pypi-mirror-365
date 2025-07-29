import json
import tkinter as tk
import threading
import datetime
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from xianbao.core.context import global_context
from xianbao.service.rpa_backfilling_recong import ExcelWriter
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler


class ReconciliationTab(ttk.Frame):
    """
    对账回填功能的主界面类
    
    Args:
        parent: 父窗口组件
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.task_manager = global_context.get('task_manager')
        self.dict_manager = None
        self.is_running = False
        self.scheduler = BackgroundScheduler()
        self.create_widgets()
        self.load_config()
        
    def _init_dict_manager(self):
        """初始化DictManager单例"""
        if self.dict_manager is None:
            self.dict_manager = global_context.get('dict_manager')
        
    def load_config(self):
        """从字典加载保存的配置"""
        self._init_dict_manager()
        
        # 从JSON加载所有配置参数
        config_json = self.dict_manager.get_dict_value("sys_recon", "对账配置")
        if config_json:
            try:
                config_dict = json.loads(config_json)
                self.cron_entry.delete(0, tk.END)
                self.cron_entry.insert(0, config_dict.get("cron_expr", ""))
                
                recon_file = config_dict.get("recon_file", "")
                self.recon_file_label.config(text=recon_file)
                    
                trans_file = config_dict.get("trans_file", "")
                self.trans_file_label.config(text=trans_file)
            except json.JSONDecodeError:
                # 配置解析失败时全部置空
                self.cron_entry.delete(0, tk.END)
                self.recon_file_label.config(text="")
                self.trans_file_label.config(text="")
    
    def create_widgets(self):
        """创建对账回填界面组件"""
        # 第一行：Cron表达式
        ttk.Label(self, text="Cron表达式:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cron_entry = ttk.Entry(self, width=30)
        self.cron_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.cron_entry.insert(0, "0 9 * * *")
        
        # 第二行：对账文件选择
        ttk.Button(self, text="选择对账文件", command=lambda: self.select_file("对账文件")).grid(row=1, column=0, padx=5, pady=5)
        self.recon_file_label = ttk.Label(self, text="未选择文件")
        self.recon_file_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 第三行：流水文件选择
        ttk.Button(self, text="选择流水文件", command=lambda: self.select_file("流水文件")).grid(row=2, column=0, padx=5, pady=5)
        self.trans_file_label = ttk.Label(self, text="未选择文件")
        self.trans_file_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # 第四行：按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        
        # 开始对账按钮(仅验证Cron)
        self.sync_btn = ttk.Button(btn_frame, text="开始对账(Cron)", command=self.start_reconciliation_by_cron)
        self.sync_btn.pack(side="left", expand=True, fill="x")
        
        # 直接开始对账按钮
        self.direct_sync_btn = ttk.Button(btn_frame, text="直接开始对账", command=self.start_reconciliation_directly)
        self.direct_sync_btn.pack(side="left", expand=True, fill="x")
        
        # 保存配置按钮
        self.save_btn = ttk.Button(btn_frame, text="保存配置", command=self.save_config)
        self.save_btn.pack(side="left", expand=True, fill="x")
        
        # 第五行：状态标签
        self.status_label = ttk.Label(self, text="运行状态: 空闲")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # 定时任务状态标签
        self.scheduler_status_label = ttk.Label(self, text="定时任务: 已关闭")
        self.scheduler_status_label.grid(row=4, column=1, columnspan=1, padx=5, pady=5, sticky="e")
        
        # 第六行：日志框
        self.log_text = ScrolledText(self, height=15, state="disabled")
        self.log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)
    
    def select_file(self, file_type):
        """选择对账或流水文件"""
        file_path = self._get_file_path()
        if file_path:
            self._update_file_label(file_type, file_path)
            
    def _get_file_path(self):
        """获取文件路径"""
        return filedialog.askopenfilename(
            filetypes=[("Excel文件", ".xlsx .xlsm")]
        )
        
    def _update_file_label(self, file_type, file_path):
        """更新文件标签"""
        if file_type == "对账文件":
            self.recon_file_label.config(text=file_path)
        else:
            self.trans_file_label.config(text=file_path)
    
    def start_reconciliation_by_cron(self):
        """通过Cron表达式验证后执行对账"""
        if self.is_running:
            return
            
        # 如果定时任务已开启，则关闭它
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.remove_job('rpa_reconciliation_job')
            self.scheduler.shutdown()
            self.scheduler_status_label.config(text="定时任务: 已关闭")
            # messagebox.showinfo("成功", "定时任务已关闭")
            return
            
        cron_expr = self.cron_entry.get()
        try:
            # croniter.croniter(cron_expr)
            
            # 检查是否已有定时任务，有则先移除
            if hasattr(self, 'scheduler') and self.scheduler.get_jobs():
                self.scheduler.remove_all_jobs()
                
            params = self.parse_cron_expr(cron_expr)

            # 创建定时任务
            self.scheduler.add_job(
                self._execute_reconciliation,
                trigger=CronTrigger(
                    second=params['second'],
                    minute=params['minute'],
                    hour=params['hour'],
                    day=params['day'],
                    month=params['month'],
                    day_of_week=params['day_of_week']
                ),
                id='rpa_reconciliation_job'
            )
            self.scheduler.start()
            self.scheduler_status_label.config(text="定时任务: 已开启")
            
            messagebox.showinfo("成功", f"已创建定时任务: {cron_expr}")
        except Exception as e:
            messagebox.showerror("错误", f"无效的Cron表达式: {e}")
    

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


    def save_config(self):
        """保存配置到字典"""
        config_data = self._get_config_data()
        self._save_to_dict(config_data)
        messagebox.showinfo("成功", "配置已保存")
        
    def _get_config_data(self):
        """获取配置数据"""
        return {
            "cron_expr": self.cron_entry.get(),
            "recon_file": self.recon_file_label.cget("text"),
            "trans_file": self.trans_file_label.cget("text")
        }
        
    def _save_to_dict(self, config_data):
        """保存配置到字典"""
        dict_manager = global_context.get('dict_manager')
        
        # 添加字典类型(如果不存在)
        if not dict_manager.get_dict_type_by_code("sys_recon"):
            dict_manager.add_dict_type("对账配置", "sys_recon")
            
        # 保存所有配置为字典并持久化为JSON
        import json
        config_dict = {
            "cron_expr": config_data["cron_expr"],
            "recon_file": config_data["recon_file"],
            "trans_file": config_data["trans_file"]
        }
        
        # 检查字典项是否存在，不存在则新增
        if not dict_manager.get_dict_value("sys_recon", "对账配置"):
            dict_manager.add_dict_item("sys_recon", "对账配置", json.dumps(config_dict, ensure_ascii=False))
        else:
            dict_manager.update_dict_item("sys_recon", "对账配置", json.dumps(config_dict, ensure_ascii=False))
    
    def start_reconciliation_directly(self):
        """直接开始对账任务"""
        if self.is_running:
            messagebox.showwarning("提示", "当前已有对账任务运行中")
            return
            
        # 启动对账
        self._execute_reconciliation()
        
    def _execute_reconciliation(self):
        """执行对账任务"""
        # 更新UI状态
        self._update_ui_state(running=True)
        
        # 启动后台线程
        thread = threading.Thread(
            target=self.run_reconciliation, 
            args=(self.recon_file_label.cget("text"), self.trans_file_label.cget("text"))
        )
        thread.daemon = True
        thread.start()
        
    def _update_ui_state(self, running):
        """更新UI状态"""
        self.is_running = running
        state = "disabled" if running else "!disabled"
        self.sync_btn.config(state=state)
        self.direct_sync_btn.config(state=state)
        self.save_btn.config(state=state)
        self.status_label.config(text=f"运行状态: {'运行中' if running else '空闲'}")
        state_text = "运行中" if running else "空闲"
        button_state = "disabled" if running else "normal"
        
        self.status_label.config(text=f"运行状态: {state_text}")
        self.scheduler_status_label.config(text=f"定时任务: {'已开启' if self.scheduler.running else '已关闭'}")
        self.sync_btn.config(state=button_state)
        self.direct_sync_btn.config(state=button_state)
        self.save_btn.config(state=button_state)
        
        if running:
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
    
    def run_reconciliation(self, recon_path, trans_path):
        """执行对账任务"""
        handler = ExcelWriter(recon_path, trans_path)
        page = 1
        per_page = 1000
        
        while True:
            tasks = self.rpa_backfilling(page, per_page)
            if not tasks:
                break
                
            for task in tasks:
                try:
                    f = handler.write_to_excel(task)
                    if f:
                        self.update_log(f"处理任务 {task['id']} 成功")
                    else:
                        self.update_log(f"处理任务 {task['id']} 失败")
                except Exception as e:
                    self.update_log(f"处理任务 {task['id']} 失败: {str(e)}")
            
            page += 1
        
        handler.close()
        
        # 恢复界面状态
        self._update_ui_state(running=False)
        self.update_log("所有对账任务处理完成")
    
    def rpa_backfilling(self, page=1, per_page=1000):
        """分页获取任务列表"""
        offset = (page - 1) * per_page
        sql = f"""
            SELECT * FROM tasks 
            ORDER BY created_time DESC 
            LIMIT {per_page} OFFSET {offset}
        """
        tasks = self.task_manager.execute_custom_sql(sql)

        # 反序列化meta字段
        for task in tasks:
            if 'meta' in task and task['meta']:
                task['meta'] = json.loads(task['meta'])

        return tasks
    
    def update_log(self, message):
        """更新日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert("end", log_message)
        self.log_text.see("end")
        self.log_text.config(state="disabled")