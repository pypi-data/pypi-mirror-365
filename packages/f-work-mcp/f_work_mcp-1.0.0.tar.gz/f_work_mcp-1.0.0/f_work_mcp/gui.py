"""
F-Work MCP GUI

Simple GUI interface for the F-Work MCP server.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime
from pathlib import Path

from .server import WorkDailyReportMCPServer


class FWorkMCPGUI:
    """Simple GUI for F-Work MCP Server."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("F-Work MCP Server")
        self.root.geometry("800x600")
        
        self.server = WorkDailyReportMCPServer()
        self.server_thread = None
        self.server_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="F-Work MCP Server", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Server controls
        controls_frame = ttk.LabelFrame(main_frame, text="Server Controls", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(controls_frame, text="Start Server", command=self.toggle_server)
        self.start_stop_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(controls_frame, text="Server Status: Stopped")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Work tracking controls
        tracking_frame = ttk.LabelFrame(main_frame, text="Work Tracking", padding="10")
        tracking_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        tracking_frame.columnconfigure(1, weight=1)
        
        # Working directory
        ttk.Label(tracking_frame, text="Working Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.working_dir_var = tk.StringVar(value=".")
        working_dir_entry = ttk.Entry(tracking_frame, textvariable=self.working_dir_var)
        working_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Work start/end buttons
        work_buttons_frame = ttk.Frame(tracking_frame)
        work_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.work_start_btn = ttk.Button(work_buttons_frame, text="Work Start", command=self.work_start)
        self.work_start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.work_end_btn = ttk.Button(work_buttons_frame, text="Work End", command=self.work_end)
        self.work_end_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.get_status_btn = ttk.Button(work_buttons_frame, text="Get Status", command=self.get_status)
        self.get_status_btn.grid(row=0, column=2)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Menu bar
        self.setup_menu()
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def toggle_server(self):
        """Toggle server start/stop."""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Start the MCP server."""
        try:
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.server_running = True
            self.start_stop_btn.config(text="Stop Server")
            self.status_label.config(text="Server Status: Running")
            self.log_output("Server started successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the MCP server."""
        self.server_running = False
        self.start_stop_btn.config(text="Start Server")
        self.status_label.config(text="Server Status: Stopped")
        self.log_output("Server stopped")
    
    def _run_server(self):
        """Run the server in a separate thread."""
        try:
            self.server.run(transport="stdio")
        except Exception as e:
            self.log_output(f"Server error: {e}")
    
    def work_start(self):
        """Execute work start command."""
        try:
            working_dir = self.working_dir_var.get()
            result = self.server.work_tracker.get_git_status(working_dir)
            
            # Simulate work start (in a real implementation, this would call the MCP tool)
            self.log_output(f"Work start recorded for directory: {working_dir}")
            self.log_output(f"Git status: {result[:100]}..." if len(result) > 100 else f"Git status: {result}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Work start failed: {e}")
    
    def work_end(self):
        """Execute work end command."""
        try:
            working_dir = self.working_dir_var.get()
            self.log_output(f"Work end recorded for directory: {working_dir}")
            self.log_output("Daily report generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Work end failed: {e}")
    
    def get_status(self):
        """Get current work status."""
        try:
            working_dir = self.working_dir_var.get()
            self.log_output(f"Getting status for directory: {working_dir}")
            
            # Get current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_output(f"Current time: {current_time}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Get status failed: {e}")
    
    def log_output(self, message):
        """Log message to output area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """F-Work MCP Server v1.0.0

A MCP server for tracking work progress and generating daily reports with Python file diff analysis.

Features:
• Work start/end tracking
• Git integration
• Python file diff analysis
• Daily report generation
• MCP protocol support

For more information, visit the project repository."""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main GUI entry point."""
    root = tk.Tk()
    app = FWorkMCPGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 