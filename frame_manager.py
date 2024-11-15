import os
import subprocess
from PIL import Image
import time
import psutil
import shutil
import glob
import pyautogui

class FrameManager:
    def __init__(self, dimensions, file_format):
        self.dimensions = dimensions
        self.file_format = file_format
        self.current_process = None
        
        # Create movie directory if it doesn't exist
        self.movie_dir = os.path.join(os.getcwd(), "movie")
        if not os.path.exists(self.movie_dir):
            os.makedirs(self.movie_dir)
        
    def get_frame_path(self, frame_num, variation):
        filename = f"{frame_num}-{variation:03d}{self.file_format}"
        return os.path.join(self.movie_dir, filename)
        
    def create_empty_frame(self, path):
        img = Image.new('RGB', self.dimensions, 'white')
        img.save(path)
        
    def save_current_frame(self):
        if self.current_process:
            try:
                # Find and focus MS Paint window
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == 'mspaint.exe':
                        # Focus MS Paint window
                        import win32gui
                        import win32con
                        
                        def window_enum_handler(hwnd, windows):
                            if win32gui.IsWindowVisible(hwnd):
                                if 'paint' in win32gui.GetWindowText(hwnd).lower():
                                    windows.append(hwnd)
                        
                        windows = []
                        win32gui.EnumWindows(window_enum_handler, windows)
                        
                        if windows:
                            win32gui.SetForegroundWindow(windows[0])
                            time.sleep(0.2)  # Wait for window to focus
                            
                            # Send Ctrl+S to save
                            pyautogui.hotkey('ctrl', 's')
                            time.sleep(0.5)  # Wait for save operation
                            
                            # Close MS Paint
                            try:
                                proc.kill()
                            except:
                                pass
                            time.sleep(0.5)
            
            except Exception as e:
                print(f"Error saving frame: {e}")
        
    def open_frame(self, frame_num, variation, auto_new_layer=False):
        path = self.get_frame_path(frame_num, variation)
        
        # Create frame if it doesn't exist
        if not os.path.exists(path):
            self.create_empty_frame(path)
            
        # Ensure MS Paint is closed before opening new file
        self.save_current_frame()
        time.sleep(0.2)  # Additional safety delay
            
        # Open frame in MS Paint
        self.current_process = subprocess.Popen(['mspaint', path])
        time.sleep(0.5)  # Wait for MS Paint to open
        
        # Focus MS Paint window and handle shortcuts
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'mspaint.exe':
                import win32gui
                
                def window_enum_handler(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        if 'paint' in win32gui.GetWindowText(hwnd).lower():
                            windows.append(hwnd)
                
                windows = []
                win32gui.EnumWindows(window_enum_handler, windows)
                
                if windows:
                    win32gui.SetForegroundWindow(windows[0])
                    time.sleep(0.2)  # Wait for window to focus
                    
                    # Always open layer panel first
                    pyautogui.press('alt')
                    time.sleep(0.2)  # Increased delay to ensure alt is released
                    pyautogui.press('l')
                    time.sleep(0.3)  # Wait for panel to open
                    
                    # Create new layer only if checkbox is checked
                    if auto_new_layer:
                        time.sleep(0.2)  # Additional delay before new layer shortcut
                        pyautogui.hotkey('ctrl', 'shift', 'n')
        
    def copy_frame_as_next(self, current_frame, current_variation, next_frame, next_variation):
        """Copy current frame as the next frame"""
        current_path = self.get_frame_path(current_frame, current_variation)
        next_path = self.get_frame_path(next_frame, next_variation)
        
        # Only copy if current frame exists and next frame doesn't
        if os.path.exists(current_path) and not os.path.exists(next_path):
            shutil.copy2(current_path, next_path)
        
    def get_next_frame_info(self, current_frame, current_variation):
        """Find the next frame or in-between frame"""
        # Get all files matching the current frame number
        pattern = os.path.join(self.movie_dir, f"{current_frame}-*{self.file_format}")
        current_frame_files = sorted(glob.glob(pattern))
        
        # Get all files matching the next frame number
        next_frame = current_frame + 1
        next_pattern = os.path.join(self.movie_dir, f"{next_frame}-*{self.file_format}")
        next_frame_files = glob.glob(next_pattern)
        
        # If there are more variations of current frame
        if current_frame_files:
            current_variations = [int(os.path.basename(f).split('-')[1].split('.')[0]) 
                                for f in current_frame_files]
            for variation in sorted(current_variations):
                if variation > current_variation:
                    return current_frame, variation
        
        # If no more variations, go to next frame number
        if next_frame_files:
            return next_frame, 0
        
        # If no existing next frame, create one
        return next_frame, 0
        
    def get_previous_frame_info(self, current_frame, current_variation):
        """Find the previous frame or in-between frame"""
        # Get all files matching the current frame number
        pattern = os.path.join(self.movie_dir, f"{current_frame}-*{self.file_format}")
        current_frame_files = sorted(glob.glob(pattern))
        
        # Get all files matching the previous frame number
        prev_frame = current_frame - 1
        prev_pattern = os.path.join(self.movie_dir, f"{prev_frame}-*{self.file_format}")
        prev_frame_files = glob.glob(prev_pattern)
        
        # If there are variations of current frame
        if current_frame_files:
            current_variations = [int(os.path.basename(f).split('-')[1].split('.')[0]) 
                                for f in current_frame_files]
            for variation in sorted(current_variations, reverse=True):
                if variation < current_variation:
                    return current_frame, variation
        
        # If no previous variations, go to previous frame number
        if prev_frame_files:
            prev_variations = [int(os.path.basename(f).split('-')[1].split('.')[0]) 
                             for f in prev_frame_files]
            return prev_frame, max(prev_variations)
        
        # If no previous frame, stay at current
        return prev_frame if prev_frame > 0 else current_frame, 0
        
    def get_previous_variation_info(self):
        """Get the highest variation number for the previous frame"""
        prev_frame = self.current_frame - 1
        pattern = os.path.join(self.movie_dir, f"{prev_frame}-*{self.file_format}")
        prev_frame_files = glob.glob(pattern)
        
        if prev_frame_files:
            variations = [int(os.path.basename(f).split('-')[1].split('.')[0]) 
                         for f in prev_frame_files]
            if variations:
                return prev_frame, max(variations)
        return prev_frame, 0  # Return 0 instead of -1 for initial variation

    def delete_current_frame(self, frame_num, variation):
        """Delete the current frame file and close MS Paint"""
        path = self.get_frame_path(frame_num, variation)
        
        # Close MS Paint
        self.save_current_frame()
        
        # Delete the file if it exists
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting frame: {e}")

    def get_next_available_variation(self, frame_num):
        """Find the next available variation number for a given frame"""
        # Start from 999 and work backwards
        for variation in range(999, -1, -1):
            path = self.get_frame_path(frame_num, variation)
            if not os.path.exists(path):
                return variation
            
        # If somehow all variations are taken (shouldn't happen with 1000 possibilities)
        return 0

    def get_next_available_variation_in_range(self, frame_num, current_variation):
        """Find the next available variation number that's greater than the current one"""
        # Get all existing variations for this frame
        pattern = os.path.join(self.movie_dir, f"{frame_num}-*{self.file_format}")
        existing_files = glob.glob(pattern)
        
        if existing_files:
            variations = [int(os.path.basename(f).split('-')[1].split('.')[0]) 
                         for f in existing_files]
            # Find the next available number after current_variation
            for var in range(current_variation + 1, 1000):
                if var not in variations:
                    return var
        else:
            # If no files exist, start with variation after current
            return current_variation + 1
        
        # If somehow all variations are taken (shouldn't happen)
        return current_variation + 1