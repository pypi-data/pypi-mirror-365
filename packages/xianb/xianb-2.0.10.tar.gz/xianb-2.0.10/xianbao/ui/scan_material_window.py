import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from xianbao.core.context import global_context
from xianbao.service.auto_scan import scan, scan_and_process_files
import threading


class ScanMaterialWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # 从字典加载设置
        self.dict_manager = global_context['dict_manager']
        
        # 确保扫描配置字典类型存在
        if not self.dict_manager.get_dict_type_by_code("sys_scan"):
            self.dict_manager.add_dict_type("系统扫描配置", "sys_scan", "系统扫描相关配置项")
        
        scan_settings = self.dict_manager.get_dict_as_mapping("sys_scan")
        
        self.poppler_path = scan_settings.get("poppler_path", "")
        self.default_depth = scan_settings.get("depth", "1")
        self.default_directory = scan_settings.get("directory", "")
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 目录深度
        self.depth_label = ttk.Label(self, text="目录深度:")
        self.depth_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.depth_entry = ttk.Entry(self)
        self.depth_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.depth_entry.insert(0, self.default_depth)
        
        # 目录选择
        self.dir_label = ttk.Label(self, text="选择待扫描目录:")
        self.dir_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.dir_entry = ttk.Entry(self)
        self.dir_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.dir_entry.insert(0, self.default_directory)
        self.dir_button = ttk.Button(self, text="浏览...", command=self.select_directory)
        self.dir_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Poppler路径
        self.poppler_label = ttk.Label(self, text="Poppler路径:")
        self.poppler_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.poppler_entry = ttk.Entry(self)
        self.poppler_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.poppler_entry.insert(0, self.poppler_path)
        self.poppler_button = ttk.Button(self, text="浏览...", command=self.select_poppler)
        self.poppler_button.grid(row=2, column=2, padx=5, pady=5)
        
        # 日志详情
        self.log_label = ttk.Label(self, text="日志详情:")
        self.log_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.log_text = tk.Text(self, wrap=tk.WORD)
        self.log_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        # 扫描按钮
        self.scan_button = ttk.Button(self, text="开始扫描", command=self.start_scan)
        self.scan_button.grid(row=4, column=1, padx=5, pady=5)
        
        # 配置网格权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            
    def select_poppler(self):
        """选择Poppler路径"""
        directory = filedialog.askdirectory()
        if directory:
            self.poppler_entry.delete(0, tk.END)
            self.poppler_entry.insert(0, directory)
            self.poppler_path = directory
    
    def start_scan(self):
        """开始扫描处理"""
        try:
            # 清空日志框
            self.log_text.delete(1.0, tk.END)
            
            depth = int(self.depth_entry.get())
            directory = self.dir_entry.get()
            self.poppler_path = self.poppler_entry.get()
            
            if not directory:
                messagebox.showerror("错误", "请选择目录")
                return
                
            if not self.poppler_path:
                messagebox.showerror("错误", "请选择Poppler路径")
                return
                
            # 保存设置到字典
            # 检查字典类型是否存在，不存在则创建
            if not self.dict_manager.get_dict_type_by_code("sys_scan"):
                self.dict_manager.add_dict_type("系统扫描配置", "sys_scan", "系统扫描相关配置项")
            
            settings = {
                "depth": str(depth),
                "directory": directory,
                "poppler_path": self.poppler_path
            }
            
            for key, value in settings.items():
                if self.dict_manager.get_dict_value("sys_scan", key) is not None:
                    # 已存在则更新
                    self.dict_manager.update_dict_item("sys_scan", key, value)
                else:
                    # 不存在则添加
                    self.dict_manager.add_dict_item("sys_scan", key, value)
            
            # 扫描所有目录
            self.log_text.insert(tk.END, f"开始扫描目录: {directory}\n")
            file_folder = scan(directory, depth)
            self.log_text.insert(tk.END, f"找到 {len(file_folder)} 个文件\n")
            
            # 获取文件映射
            # 确保文件映射字典类型存在
            if not self.dict_manager.get_dict_type_by_code("ikea_fm"):
                self.dict_manager.add_dict_type("IKEA文件映射", "ikea_fm", "IKEA文件路径映射配置")
            file_mapping = self.dict_manager.get_dict_as_mapping('ikea_fm')
            failed_files = []

            # 创建后台处理线程
            def process_files_thread():
                if not file_folder:
                    self.log_text.after(0, lambda: self.log_text.insert(tk.END, "没有找到可处理的文件\n"))
                    return
                
                for file_path in file_folder:
                    try:
                        self.log_text.after(0, lambda p=file_path: self.log_text.insert(tk.END, f"正在处理: {p}\n"))
                        self.log_text.after(0, self.log_text.see, tk.END)
                        
                        scan_and_process_files(
                            directory_=file_path,
                            file_mapping_=file_mapping,
                            poppler_path=self.poppler_path
                        )
                        self.log_text.after(0, lambda p=file_path: self.log_text.insert(tk.END, f"处理完成: {p}\n"))
                    except Exception as e:
                        failed_files.append(file_path)
                        self.log_text.after(0, lambda p=file_path, e=e: self.log_text.insert(tk.END, f"处理失败: {p} - {str(e)}\n"))
                
                if failed_files:
                    self.log_text.after(0, lambda: self.log_text.insert(tk.END, f"以下文件处理失败: {', '.join(failed_files)}\n"))
            
            # 启动后台线程
            threading.Thread(target=process_files_thread, daemon=True).start()
            
            self.log_text.insert(tk.END, f"处理完成!")

            if failed_files:
                self.log_text.insert(tk.END, f"以下文件处理失败: {', '.join(failed_files)}\n")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字作为目录深度")
        except Exception as e:
            messagebox.showerror("错误", f"扫描处理失败: {str(e)}")
            self.log_text.insert(tk.END, f"错误: {str(e)}\n")