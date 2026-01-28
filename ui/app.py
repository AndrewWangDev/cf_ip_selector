import customtkinter as ctk
from core.controller import SpeedTestController
from .components import ResultList

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Cloudflare Speedtest")
        self.geometry("450x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.controller = SpeedTestController(
            update_callback=self.on_update,
            finish_callback=self.on_finish
        )
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=20, padx=20)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Cloudflare Speedtest", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(side="left")
        
        self.status_label = ctk.CTkLabel(self.header_frame, text="Ready", text_color="gray", font=("Segoe UI", 12))
        self.status_label.pack(side="right")
        
        # Result Area
        self.result_container = ctk.CTkFrame(self, fg_color="transparent")
        self.result_container.grid(row=1, column=0, sticky="nsew", padx=20)
        
        self.result_label = ctk.CTkLabel(self.result_container, text="Top Results", font=("Segoe UI", 14, "bold"))
        self.result_label.pack(anchor="w", pady=(0, 10))
        
        self.result_list = ResultList(self.result_container, fg_color="transparent")
        self.result_list.pack(fill="both", expand=True)
        
        # Progress Section
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.progress_text = ctk.CTkLabel(self.progress_frame, text="0/0 IPs", font=("Segoe UI", 10))
        self.progress_text.pack(anchor="e")
        
        # Control Bar
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        
        self.start_btn = ctk.CTkButton(self.control_frame, text="Start Test", command=self.start_test, corner_radius=20, height=40)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.pause_btn = ctk.CTkButton(self.control_frame, text="Pause", command=self.pause_test, corner_radius=20, height=40, 
                                       fg_color="transparent", border_width=2, text_color=("gray10", "gray90"))
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.pause_btn.configure(state="disabled")

        self.stop_btn = ctk.CTkButton(self.control_frame, text="Stop", command=self.stop_test, corner_radius=20, height=40,
                                      fg_color="#ef5350", hover_color="#d32f2f")
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.stop_btn.configure(state="disabled")

    def start_test(self):
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Testing...", text_color="#FFA726") # Orange
        self.progress_bar.set(0)
        self.result_list.update_results([]) # Clear list
        
        self.controller.start_test()

    def pause_test(self):
        is_paused = self.controller.pause_test()
        if is_paused:
            self.pause_btn.configure(text="Resume")
            self.status_label.configure(text="Paused")
        else:
            self.pause_btn.configure(text="Pause")
            self.status_label.configure(text="Testing...", text_color="#FFA726")

    def stop_test(self):
        self.controller.stop_test()
        # Finish callback will handle the rest
        self.status_label.configure(text="Stopping...", text_color="red")

    def reset_controls(self):
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="Pause")
        self.stop_btn.configure(state="disabled")

    def on_update(self, stats):
        self.after(0, self._update_ui_thread_safe, stats)

    def _update_ui_thread_safe(self, stats):
        total = stats['total']
        tested = stats['tested']
        top = stats['top_results']
        
        if total > 0:
            progress = tested / total
            self.progress_bar.set(progress)
            self.progress_text.configure(text=f"{tested}/{total} IPs")
            
        self.result_list.update_results(top)

    def on_finish(self, error=None):
        self.after(0, self._finish_ui_thread_safe, error)

    def _finish_ui_thread_safe(self, error):
        self.reset_controls()
        if error:
            self.status_label.configure(text=f"Error: {error}", text_color="red")
        else:
            if not self.controller.results:
                self.status_label.configure(text="No valid IPs found", text_color="#FFA726")
            else:
                self.status_label.configure(text="Complete", text_color="#66BB6A")
            self.progress_bar.set(1)
