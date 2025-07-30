import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from xianbao.core.context import global_context
import json


class MetaFormDialog(tk.Toplevel):
    """JSON meta数据表单对话框"""
    
    def __init__(self, master, meta_data, task_id=None, **kwargs):
        self.task_id = task_id
        self.entries = {}  # 存储所有输入框的引用
        super().__init__(master, **kwargs)
        self.title("任务详情")
        self.geometry("800x600")
        self.configure(padx=10, pady=10)
        self.meta_data = meta_data
        self.create_widgets()
    
    def create_widgets(self):
        """创建表单控件"""
        try:
            # 尝试解析JSON数据
            if isinstance(self.meta_data, (bytes, str)):
              try:
                  meta_str = self.meta_data.decode('utf-8') if isinstance(self.meta_data, bytes) else self.meta_data
                  # 替换单引号为双引号并处理转义
                  meta_str = meta_str.replace("'", '"')
                  meta_dict = json.loads(meta_str)
              except (json.JSONDecodeError, UnicodeDecodeError):
                  meta_dict = {"原始数据": str(self.meta_data)}
            elif isinstance(self.meta_data, dict):
                meta_dict = self.meta_data
            else:
                meta_dict = {"原始数据": str(self.meta_data)}
            
            # 创建主容器
            main_frame = ttk.Frame(self)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 创建标题
            ttk.Label(main_frame, text="任务元数据详情", font=('Arial', 12, 'bold')) \
                .pack(pady=(0, 10))
            
            # 创建滚动区域
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.grid_columnconfigure(1, weight=1)
            
            def update_scrollregion(_):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.yview_moveto(0)
                
            scrollable_frame.bind("<Configure>", update_scrollregion)
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 递归生成表单
            def create_form(parent, data, prefix="", row=0):
                if isinstance(data, dict):
                    for key, value in data.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            # 嵌套字典创建分组框架
                            group_frame = ttk.LabelFrame(parent, text=key)
                            group_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=3)
                            group_frame.grid_columnconfigure(1, weight=1)
                            
                            # 递归创建子表单
                            child_row = create_form(group_frame, value, full_key, 0)
                            
                            # 更新行号：当前行 + 子表单行数 + 1(当前行自身)
                            row += child_row + 1
                        else:
                            # 普通键值对
                            ttk.Label(parent, text=f"{key}:", width=20, anchor="e") \
                                .grid(row=row, column=0, sticky="e", padx=(10, 5), pady=3)
                            
                            # 对特定字段使用组合框
                            entry = ttk.Entry(parent, width=50)
                            self.entries[full_key] = entry
                            entry.insert(0, str(value) if value is not None else "")
                            entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=3)
                            
                            parent.grid_columnconfigure(1, weight=1)
                            row += 1
                        # row increment handled in group frame creation
                return row
            
            create_form(scrollable_frame, meta_dict)
            
            # 添加底部按钮
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            if self.task_id:
                ttk.Button(button_frame, text="保存", command=self.save_changes) \
                    .pack(side="left", padx=5)
            
            # 配置canvas滚动
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 绑定canvas大小变化事件
            def on_canvas_configure(event):
                canvas.itemconfig("scrollable_frame", width=event.width)
                
            canvas.bind("<Configure>", on_canvas_configure)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_frame")
            
            # 添加鼠标滚轮支持
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind("<MouseWheel>", on_mousewheel)
            
            # 初始滚动区域更新
            self.update()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(0)
            
        except json.JSONDecodeError:
            # 显示原始数据
            error_frame = ttk.Frame(self)
            error_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            ttk.Label(error_frame, text="JSON解析错误", font=('Arial', 12, 'bold')) \
                .pack(pady=(0, 10))
                
            ttk.Label(error_frame, text="原始数据:").pack(anchor="w")
            
            text = tk.Text(error_frame, wrap="word", height=20)
            text.insert("1.0", meta_str if 'meta_str' in locals() else str(self.meta_data))
            text.configure(state="disabled")
            
            scrollbar = ttk.Scrollbar(error_frame, orient="vertical", command=text.yview)
            text.configure(yscrollcommand=scrollbar.set)
            
            text.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            ttk.Button(error_frame, text="关闭", command=self.destroy) \
                .pack(side="right", pady=(10, 0))
            
    def save_changes(self):
        """保存修改后的meta数据"""
        try:
            # 收集所有修改后的值
            new_meta = {}
            for key, entry in self.entries.items():
                # 重建嵌套字典结构
                parts = key.split('.')
                current = new_meta
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = entry.get()
            
            # 调用TaskManager更新数据库
            task_manager = global_context.get('task_manager')
            if task_manager is None:
                raise Exception("任务管理器未初始化")
            # 获取当前状态
            task = task_manager.get_task(self.task_id)
            if task:
                # 将meta字典转换为JSON字符串
                # 确保JSON字符串中的单引号被替换为双引号
                meta_json = json.dumps(new_meta, ensure_ascii=False).replace("'", '"')
                print(meta_json)
                task_manager.update_status_and_meta(self.task_id, task['status'], meta_json)
                messagebox.showinfo("成功", "任务已更新")
                self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    @classmethod
    def show(cls, master, meta_data, task_id=None, db_name=None):
        """显示对话框"""
        dialog = cls(master, meta_data, task_id=task_id, db_name=db_name)
        dialog.grab_set()
        return dialog