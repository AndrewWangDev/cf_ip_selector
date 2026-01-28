import customtkinter as ctk

class ResultRow(ctk.CTkFrame):
    def __init__(self, master, rank, ip, latency, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        
        self.rank_label = ctk.CTkLabel(self, text=f"#{rank}", width=40, font=("Segoe UI", 12, "bold"))
        self.rank_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.ip_label = ctk.CTkLabel(self, text=ip, font=("Segoe UI", 12))
        self.ip_label.grid(row=0, column=1, sticky="w", padx=10)
        
        self.latency_label = ctk.CTkLabel(self, text=f"{latency:.1f} ms", font=("Segoe UI", 12))
        self.latency_label.grid(row=0, column=2, padx=10)
        
        # Color coding
        color = "#4CAF50" if latency < 100 else "#FF9800" if latency < 200 else "#F44336"
        self.latency_label.configure(text_color=color)

class ResultList(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
    def update_results(self, top_results):
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()
            
        for i, res in enumerate(top_results):
            # Alternating colors not strictly needed if we use cards, but we use frames.
            # Let's clean up layout.
            row = ResultRow(self, rank=i+1, ip=res['ip'], latency=res['latency'], 
                            fg_color=("gray90", "gray20"), corner_radius=10)
            row.pack(fill="x", pady=5, padx=5)
