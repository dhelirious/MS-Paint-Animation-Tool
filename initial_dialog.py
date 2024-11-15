import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path

class InitialDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Animation Settings")
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        
        self.result = None
        self.width = 800
        self.height = 600
        self.format = '.png'
        self.starting_frame = None
        
        self.setup_gui()
        
        # Make dialog modal
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        parent.wait_window(self.dialog)
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dimensions
        ttk.Label(main_frame, text="Width:").grid(row=0, column=0, sticky=tk.W)
        self.width_var = tk.StringVar(value="800")
        ttk.Entry(main_frame, textvariable=self.width_var).grid(row=0, column=1, padx=5)
        
        ttk.Label(main_frame, text="Height:").grid(row=1, column=0, sticky=tk.W)
        self.height_var = tk.StringVar(value="600")
        ttk.Entry(main_frame, textvariable=self.height_var).grid(row=1, column=1, padx=5)
        
        # Format selection
        ttk.Label(main_frame, text="Format:").grid(row=2, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value=".png")
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Radiobutton(format_frame, text="PNG", variable=self.format_var, 
                       value=".png").grid(row=0, column=0)
        ttk.Radiobutton(format_frame, text="JPG", variable=self.format_var, 
                       value=".jpg").grid(row=0, column=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Start New", 
                  command=self.start_new).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Open Existing", 
                  command=self.open_existing).grid(row=0, column=1, padx=5)
        
    def start_new(self):
        try:
            self.width = int(self.width_var.get())
            self.height = int(self.height_var.get())
            self.format = self.format_var.get()
            self.result = "new"
            self.starting_frame = None
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Width and height must be valid numbers!")
            
    def open_existing(self):
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg")
        ]
        
        # Use the movie subdirectory
        initial_dir = os.path.join(os.getcwd(), "movie")
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)
        
        filename = filedialog.askopenfilename(
            title="Select a frame",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if filename:
            # Extract frame number from filename
            basename = os.path.basename(filename)
            frame_num = int(basename.split('-')[0])
            self.starting_frame = frame_num
            self.format = os.path.splitext(filename)[1]
            self.result = "existing"
            self.dialog.destroy()

    def on_close(self):
        """Handle window close button"""
        self.result = None
        self.dialog.destroy()
        