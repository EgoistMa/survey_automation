"""
Main GUI window for the Starbucks Survey Automation tool
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from core.worker import excel_mode, agent_mode
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        self.apply_styling()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Starbucks Survey Automation - Optimized")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.agent_tab = ttk.Frame(self.notebook)
        self.excel_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.agent_tab, text='Agent Mode')
        self.notebook.add(self.excel_tab, text='Excel Mode')
        
        # Create tab content
        self.create_agent_tab()
        self.create_excel_tab()
    
    def create_agent_tab(self):
        """Create agent tab content"""
        ttk.Label(self.agent_tab, text="Agent Mode Settings", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Number of runs
        ttk.Label(self.agent_tab, text="Number of Runs:").grid(
            row=1, column=0, sticky="w", padx=20, pady=10
        )
        self.num_runs_var = tk.IntVar(value=1)
        num_runs_spin = ttk.Spinbox(
            self.agent_tab, from_=1, to=100, textvariable=self.num_runs_var, width=10
        )
        num_runs_spin.grid(row=1, column=1, sticky="w", padx=5, pady=10)
        
        # Number of threads
        ttk.Label(self.agent_tab, text="Number of Threads:").grid(
            row=2, column=0, sticky="w", padx=20, pady=10
        )
        self.num_threads_var = tk.IntVar(value=3)
        num_threads_spin = ttk.Spinbox(
            self.agent_tab, from_=1, to=10, textvariable=self.num_threads_var, width=10
        )
        num_threads_spin.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        
        #TODO Create a location dropdown selector 
        self.location_var = tk.StringVar(value="Manly")
        ttk.Label(self.agent_tab, text="Location:").grid(
            row=3, column=0, sticky="w", padx=20, pady=10
        )
        location_combobox = ttk.Combobox(
            self.agent_tab, textvariable=self.location_var, 
            values=["Chatswood", "Manly"], state="readonly"
        )
        location_combobox.grid(row=3, column=1, sticky="ew", padx=5, pady=10)
        location_combobox.current(1)

        # Submit option
        self.submit_var = tk.BooleanVar(value=False)
        submit_check = ttk.Checkbutton(
            self.agent_tab, text="Actually Submit Forms", variable=self.submit_var
        )
        submit_check.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        
        # Warning
        warning_label = ttk.Label(
            self.agent_tab, 
            text="⚠️ Enabling submission will send actual data to the server", 
            foreground="red"
        )
        warning_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.agent_tab, variable=self.progress_var, maximum=100)
        self.progress.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.agent_tab, textvariable=self.status_var)
        status_label.grid(row=8, column=0, columnspan=2, sticky="w", padx=20, pady=5)

        # Start button
        self.start_btn = ttk.Button(
            self.agent_tab, text="Start Agent Mode", command=self.start_agent_mode
        )
        self.start_btn.grid(row=9, column=0, columnspan=2, pady=20)
    
    def create_excel_tab(self):
        """Create excel tab content"""
        ttk.Label(self.excel_tab, text="Excel Mode Settings", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=10
        )
        
        # Excel file selection
        ttk.Label(self.excel_tab, text="Excel File:").grid(
            row=1, column=0, sticky="w", padx=20, pady=10
        )
        self.excel_path_var = tk.StringVar()
        excel_entry = ttk.Entry(self.excel_tab, textvariable=self.excel_path_var, width=30)
        excel_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        
        browse_btn = ttk.Button(self.excel_tab, text="Browse...", command=self.browse_excel)
        browse_btn.grid(row=1, column=2, padx=5, pady=10)
        
        # Number of threads
        ttk.Label(self.excel_tab, text="Number of Threads:").grid(
            row=2, column=0, sticky="w", padx=20, pady=10
        )
        self.excel_threads_var = tk.IntVar(value=1)
        excel_threads_spin = ttk.Spinbox(
            self.excel_tab, from_=1, to=10, textvariable=self.excel_threads_var, width=10
        )
        excel_threads_spin.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        
        # Submit option
        self.excel_submit_var = tk.BooleanVar(value=True)
        excel_submit_check = ttk.Checkbutton(
            self.excel_tab, text="Actually Submit Forms", variable=self.excel_submit_var
        )
        excel_submit_check.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        
        # Warning
        excel_warning_label = ttk.Label(
            self.excel_tab, 
            text="⚠️ Enabling submission will send actual data to the server", 
            foreground="red"
        )
        excel_warning_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=20, pady=5)

        # Progress bar
        self.excel_progress_var = tk.DoubleVar()
        self.excel_progress = ttk.Progressbar(
            self.excel_tab, variable=self.excel_progress_var, maximum=100
        )
        self.excel_progress.grid(row=5, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        
        # Status label
        self.excel_status_var = tk.StringVar(value="Ready")
        excel_status_label = ttk.Label(self.excel_tab, textvariable=self.excel_status_var)
        excel_status_label.grid(row=6, column=0, columnspan=3, sticky="w", padx=20, pady=5)
        
        # Start button
        self.excel_start_btn = ttk.Button(
            self.excel_tab, text="Start Excel Mode", command=self.start_excel_mode
        )
        self.excel_start_btn.grid(row=7, column=0, columnspan=3, pady=20)
    
    def browse_excel(self):
        """Browse for Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=(("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*"))
        )
        if filename:
            self.excel_path_var.set(filename)
    
    def start_agent_mode(self):
        """Start agent mode execution"""
        runs = self.num_runs_var.get()
        threads = self.num_threads_var.get()
        submit = self.submit_var.get()
        location = self.location_var.get()
        
        if runs < 1 or threads < 1:
            messagebox.showerror("Invalid Input", "Number of runs and threads must be at least 1")
            return
            
        if submit and not messagebox.askyesno("Confirmation", 
                                            "You are about to submit actual forms. Continue?"):
            return
        
        self.start_btn.configure(state="disabled")
        self.status_var.set("Running...")
        self.progress_var.set(0)

        def update_progress(progress_val, completed, total):
            self.root.after(0, lambda: self.progress_var.set(progress_val))
            self.root.after(0, lambda: self.status_var.set(f"Completed: {completed}/{total}"))
        
        def run_agent():
            try:
                successes, failures = agent_mode(
                    num_runs=runs,
                    num_threads=threads,
                    submit_form=submit,
                    location=location,
                    progress_callback=update_progress
                )
                
                self.root.after(0, lambda: self.status_var.set(f"Completed! Success: {successes}, Failures: {failures}"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.start_btn.configure(state="normal"))
            
                message = f"Completed {runs} runs with {successes} successes and {failures} failures."
                self.root.after(0, lambda: messagebox.showinfo("Task Complete", message))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.start_btn.configure(state="normal"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                logger.error(f"GUI error in agent mode: {e}", exc_info=True)
        
        threading.Thread(target=run_agent, daemon=True).start()
    
    def start_excel_mode(self):
        """Start excel mode execution"""
        excel_path = self.excel_path_var.get()
        threads = self.excel_threads_var.get()
        submit = self.excel_submit_var.get()

        
        if not excel_path:
            messagebox.showerror("Invalid Input", "Please select an Excel file")
            return
            
        if not os.path.exists(excel_path):
            messagebox.showerror("File Error", "The selected Excel file does not exist")
            return
            
        if threads < 1:
            messagebox.showerror("Invalid Input", "Number of threads must be at least 1")
            return
            
        if submit and not messagebox.askyesno("Confirmation", 
                                            "You are about to submit actual forms. Continue?"):
            return
        
        self.excel_start_btn.configure(state="disabled")
        self.excel_status_var.set("Running...")
        self.excel_progress_var.set(0)

        def update_excel_progress(progress_val, completed, total):
            self.root.after(0, lambda: self.excel_progress_var.set(progress_val))
            self.root.after(0, lambda: self.excel_status_var.set(f"Completed: {completed}/{total}"))
        
        def run_excel():
            try:
                successes, failures = excel_mode(
                    excel_file_path=excel_path,
                    num_threads=threads,
                    submit_form=submit,
                    progress_callback=update_excel_progress
                )

                self.root.after(0, lambda: self.excel_status_var.set(f"Completed! Success: {successes}, Failures: {failures}"))
                self.root.after(0, lambda: self.excel_progress_var.set(100))
                self.root.after(0, lambda: self.excel_start_btn.configure(state="normal"))

                message = f"Completed with {successes} successes and {failures} failures."
                self.root.after(0, lambda: messagebox.showinfo("Task Complete", message))

            except Exception as e:
                self.root.after(0, lambda: self.excel_status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.excel_start_btn.configure(state="normal"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                logger.error(f"GUI error in Excel mode: {e}", exc_info=True)
        
        threading.Thread(target=run_excel, daemon=True).start()
    
    def apply_styling(self):
        """Apply styling to the GUI"""
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 11))
        style.configure('TLabel', font=('Arial', 11))
        style.configure('TCheckbutton', font=('Arial', 11))


def create_gui():
    """Create and run the main GUI"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()