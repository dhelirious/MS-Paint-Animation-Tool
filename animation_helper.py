import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import glob
from PIL import Image
import subprocess
from initial_dialog import InitialDialog
from frame_manager import FrameManager

class AnimationHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Animation Helper")
        self.root.attributes('-topmost', True)
        
        # Initialize with default values
        self.current_frame = 1
        self.variation = 0
        self.file_format = '.png'
        self.dimensions = (800, 600)
        
        # Show initial dialog
        self.show_initial_dialog()
        
        # Setup main GUI
        self.setup_gui()
        
    def show_initial_dialog(self):
        dialog = InitialDialog(self.root)
        if dialog.result is None:
            self.root.quit()
            return
            
        # Set the properties from dialog
        self.dimensions = (dialog.width, dialog.height)
        self.file_format = dialog.format
        
        # Create frame manager before trying to use it
        self.frame_manager = FrameManager(
            self.dimensions,
            self.file_format
        )
        
        # Handle both new project and existing file cases
        if dialog.result == "existing" and dialog.starting_frame:
            self.current_frame = dialog.starting_frame
        else:  # New project or dialog cancelled
            self.current_frame = 1
            self.variation = 0
        
        try:
            # Open the frame in MS Paint
            self.frame_manager.open_frame(self.current_frame, self.variation)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create/open frame: {str(e)}")
            self.root.quit()
            return
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # First row: Basic navigation
        ttk.Button(main_frame, text="Back", command=self.back).grid(row=0, column=0, padx=2)
        ttk.Button(main_frame, text="Next", command=self.next).grid(row=0, column=1, padx=2)
        
        # Second row: With reference
        ttk.Button(main_frame, text="Bck w/Reference", 
                  command=self.back_with_reference).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(main_frame, text="Nxt w/Reference", 
                  command=self.next_with_reference).grid(row=1, column=1, padx=2, pady=2)
        
        # Third row: In-between with reference
        ttk.Button(main_frame, text="Next inBtween w Reference", 
                  command=self.next_inbetween_with_reference).grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        
        # Frame info label
        self.info_label = ttk.Label(main_frame, text=self.get_frame_info())
        self.info_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Fourth row: Delete and Open buttons
        ttk.Button(main_frame, text="Delete Frame", 
                  command=self.delete_current_frame).grid(row=4, column=0, padx=2, pady=2)
        ttk.Button(main_frame, text="Open", 
                  command=self.open_frame).grid(row=4, column=1, padx=2, pady=2)
        
        # Fifth row: Sprite Sheet and Auto Layer
        ttk.Button(main_frame, text="SpriteSheet", 
                  command=self.create_spritesheet).grid(row=5, column=0, padx=2, pady=2)
        self.auto_layer = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Auto New Layer", 
                       variable=self.auto_layer).grid(row=5, column=1, pady=5)
        
    def get_frame_info(self):
        return f"Frame: {self.current_frame}-{self.variation:03d}{self.file_format}"
        
    def update_info_label(self):
        self.info_label.config(text=self.get_frame_info())
        
    def next(self):
        self.frame_manager.save_current_frame()
        
        # Get next frame info (considering in-betweens)
        next_frame, next_variation = self.frame_manager.get_next_frame_info(
            self.current_frame, 
            self.variation
        )
        
        self.current_frame = next_frame
        self.variation = next_variation
        self.frame_manager.open_frame(
            self.current_frame, 
            self.variation, 
            auto_new_layer=self.auto_layer.get()
        )
        self.update_info_label()
        
    def back(self):
        if self.current_frame > 1 or self.variation > 0:
            self.frame_manager.save_current_frame()
            
            # Get previous frame info (considering in-betweens)
            prev_frame, prev_variation = self.frame_manager.get_previous_frame_info(
                self.current_frame, 
                self.variation
            )
            
            self.current_frame = prev_frame
            self.variation = prev_variation
            self.frame_manager.open_frame(
                self.current_frame, 
                self.variation,
                auto_new_layer=self.auto_layer.get()
            )
            self.update_info_label()
        else:
            messagebox.showwarning("Warning", "Already at first frame!")
            
    def add_inbetween(self):
        self.frame_manager.save_current_frame()
        self.variation += 1
        self.frame_manager.open_frame(
            self.current_frame, 
            self.variation,
            auto_new_layer=self.auto_layer.get()
        )
        self.update_info_label()
        
    def next_with_reference(self):
        """Move to next frame while copying current frame as reference"""
        self.frame_manager.save_current_frame()
        
        next_frame = self.current_frame + 1
        self.frame_manager.copy_frame_as_next(
            self.current_frame, 
            self.variation,
            next_frame,
            0
        )
        
        self.current_frame = next_frame
        self.variation = 0
        self.frame_manager.open_frame(
            self.current_frame, 
            self.variation,
            auto_new_layer=self.auto_layer.get()
        )
        self.update_info_label()
        
    def back_with_reference(self):
        """Move to previous frame while copying current frame as reference"""
        if self.current_frame > 1:
            self.frame_manager.save_current_frame()
            prev_frame, prev_variation = self.frame_manager.get_previous_frame_info(
                self.current_frame, 
                self.variation
            )
            self.frame_manager.copy_frame_as_next(
                self.current_frame,
                self.variation,
                prev_frame,
                prev_variation
            )
            self.current_frame = prev_frame
            self.variation = prev_variation
            self.frame_manager.open_frame(
                self.current_frame, 
                self.variation,
                auto_new_layer=self.auto_layer.get()
            )
            self.update_info_label()
        else:
            messagebox.showwarning("Warning", "Already at first frame!")

    def next_inbetween_with_reference(self):
        """Add an in-between frame after current frame with reference"""
        self.frame_manager.save_current_frame()
        next_variation = self.variation + 1
        self.frame_manager.copy_frame_as_next(
            self.current_frame,
            self.variation,
            self.current_frame,
            next_variation
        )
        self.variation = next_variation
        self.frame_manager.open_frame(
            self.current_frame, 
            self.variation,
            auto_new_layer=self.auto_layer.get()
        )
        self.update_info_label()
        
    def delete_current_frame(self):
        """Delete current frame and close MS Paint"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete frame {self.current_frame}-{self.variation:03d}?"):
            self.frame_manager.delete_current_frame(self.current_frame, self.variation)
            # Move to previous frame if possible
            if self.current_frame > 1 or self.variation > 0:
                prev_frame, prev_variation = self.frame_manager.get_previous_frame_info(
                    self.current_frame, 
                    self.variation
                )
                self.current_frame = prev_frame
                self.variation = prev_variation
                self.frame_manager.open_frame(self.current_frame, self.variation)
            self.update_info_label()
        
    def open_frame(self):
        """Open a specific frame from file explorer"""
        filetypes = [
            ("Image files", "*.png;*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg")
        ]
        
        # Use the movie directory as initial directory
        filename = filedialog.askopenfilename(
            title="Select a frame",
            filetypes=filetypes,
            initialdir=self.frame_manager.movie_dir
        )
        
        if filename:
            # Save and close current frame
            self.frame_manager.save_current_frame()
            
            # Extract frame number and variation from filename
            basename = os.path.basename(filename)
            frame_parts = os.path.splitext(basename)[0].split('-')
            
            try:
                new_frame = int(frame_parts[0])
                new_variation = int(frame_parts[1])
                
                # Update current frame and variation
                self.current_frame = new_frame
                self.variation = new_variation
                
                # Open the selected frame
                self.frame_manager.open_frame(
                    self.current_frame,
                    self.variation,
                    auto_new_layer=self.auto_layer.get()
                )
                self.update_info_label()
                
            except (ValueError, IndexError):
                messagebox.showerror("Error", 
                                   "Invalid frame filename format. Expected format: number-variation.ext")
        
    def run(self):
        self.root.mainloop()

    def create_spritesheet(self):
        """Create a sprite sheet from all frames"""
        # Ask user for number of columns
        dialog = tk.Toplevel(self.root)
        dialog.title("Sprite Sheet Settings")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Number of columns:").grid(row=0, column=0, padx=5, pady=5)
        columns_var = tk.StringVar(value="5")
        ttk.Entry(dialog, textvariable=columns_var).grid(row=0, column=1, padx=5, pady=5)
        
        def on_ok():
            try:
                columns = int(columns_var.get())
                if columns <= 0:
                    raise ValueError("Columns must be positive")
                dialog.destroy()
                self._generate_spritesheet(columns)
            except ValueError as e:
                messagebox.showerror("Error", "Please enter a valid positive number")
                
        ttk.Button(dialog, text="OK", command=on_ok).grid(row=1, column=0, columnspan=2, pady=10)
        
    def _generate_spritesheet(self, columns):
        """Generate the actual sprite sheet"""
        # Get all frame files sorted
        files = sorted(glob.glob(os.path.join(self.frame_manager.movie_dir, f"*{self.file_format}")),
                      key=lambda x: tuple(map(int, os.path.splitext(os.path.basename(x))[0].split('-'))))
        
        if not files:
            messagebox.showerror("Error", "No frames found!")
            return
            
        # Get dimensions from first frame
        with Image.open(files[0]) as first_frame:
            sprite_width, sprite_height = first_frame.size
            
        # Calculate sprite sheet dimensions
        num_sprites = len(files)
        rows = (num_sprites + columns - 1) // columns  # Ceiling division
        sheet_width = columns * sprite_width
        sheet_height = rows * sprite_height
        
        # Create new image
        spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # Place sprites
        for i, file in enumerate(files):
            row = i // columns
            col = i % columns
            x = col * sprite_width
            y = row * sprite_height
            
            with Image.open(file) as sprite:
                spritesheet.paste(sprite, (x, y))
        
        # Save sprite sheet with unique name
        base_name = "spritesheet"
        counter = 0
        while os.path.exists(os.path.join(self.frame_manager.movie_dir, f"{base_name}{counter if counter else ''}.png")):
            counter += 1
        
        output_path = os.path.join(self.frame_manager.movie_dir, f"{base_name}{counter if counter else ''}.png")
        spritesheet.save(output_path)
        messagebox.showinfo("Success", f"Sprite sheet created: {os.path.basename(output_path)}")

if __name__ == "__main__":
    app = AnimationHelper()
    app.run() 