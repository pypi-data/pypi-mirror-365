import tkinter as tk
from tkinter import ttk

class StatusVisualization(ttk.Frame):
    """16位状态可视化组件"""
    
    STATUS_BITS = {
        15: ("预留位p", "p", "N/A"),
        14: ("预留位o", "o", "N/A"),
        13: ("预留位n", "n", "N/A"),
        12: ("预留位m", "m", "N/A"),
        11: ("参考号识别失败", "l", "N/A"),
        10: ("回填失败", "k", "已完成"),
        9: ("回填成功", "j", "待处理"),
        8: ("送货单识别", "i", "已完成"),
        7: ("发票识别", "h", "待处理"),
        6: ("宜家小票识别", "g", "已完成"),
        5: ("银联小票识别", "f", "待处理"),
        4: ("商品图片入库", "e", "已完成"),
        3: ("送货单入库", "d", "待处理"),
        2: ("发票入库", "c", "已完成"),
        1: ("宜家小票入库", "b", "待处理"),
        0: ("银联小票入库", "a", "已完成")
    }
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(padding=5)
        self.create_widgets()
    
    def create_widgets(self):
        """创建状态灯网格"""
        self.lights = []
        
        for bit in range(16):
            label, char, _ = self.STATUS_BITS[bit]
            
            # 创建状态灯
            light = tk.Canvas(self, width=20, height=20, bg="gray", highlightthickness=0)
            light.grid(row=bit//8, column=(bit%8)*2, padx=2, pady=2)
            
            # 创建标签
            tk.Label(self, text=f"{char}: {label}").grid(row=bit//8, column=(bit%8)*2+1, sticky=tk.W)
            
            # 添加工具提示
            self.create_tooltip(light, label)
            
            self.lights.append(light)
    
    def create_tooltip(self, widget, text):
        """为组件添加工具提示"""
        tooltip = tk.Toplevel(self)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        
        label = tk.Label(tooltip, text=text, bg="lightyellow", 
                       relief="solid", borderwidth=1)
        label.pack()
        
        def enter(event):
            bbox = widget.bbox("all")
            if bbox is not None:
                x, y, _, _ = bbox
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 25
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()
            
        def leave(event):
            tooltip.withdraw()
            
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def update_status(self, status):
        """更新状态显示"""
        for bit in range(1, 17):
            color = "green" if status & (1 << (16 - bit)) else "red"
            self.lights[bit - 1].configure(bg=color)

