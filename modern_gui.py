import ctypes
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import platform
from pathlib import Path
import time
import threading
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame
import random

class ModernImageEncryptor:
    def __init__(self):
        # Setup window
        self.root = ttk.Window(themename="darkly")
        self.root.title("Quantum Image Encryptor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Create directories
        self.setup_directories()
        
        # Load DLL
        self.load_library()
        
        # Initialize UI elements
        self.current_image = None
        self.is_processing = False
        self.setup_ui()
        
        # Start animation thread
        self.animation_thread = threading.Thread(target=self.run_background_animation, daemon=True)
        self.animation_thread.start()

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, "Outputs")
        self.scrambled_dir = os.path.join(self.base_dir, "Scrambled")
        self.inputs_dir = os.path.join(self.base_dir, "Inputs")
        
        for directory in [self.output_dir, self.scrambled_dir, self.inputs_dir]:
            os.makedirs(directory, exist_ok=True)

    def load_library(self):
        """Load the encryption library"""
        try:
            if os.name == "nt":
                dll_path = os.path.join(self.base_dir, "image_encryptor.dll")
                self.lib = ctypes.CDLL(dll_path)
            else:
                so_path = os.path.join(self.base_dir, "libimage_encryptor.so")
                self.lib = ctypes.CDLL(so_path)
                
            # Set function signatures
            self.lib.scramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
            self.lib.unscramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
            
        except Exception as e:
            Messagebox.show_error(
                f"Failed to load encryption library: {str(e)}",
                "Critical Error"
            )
            exit(1)

    def setup_ui(self):
        """Setup the modern user interface"""
        # Create main container with gradient background
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background="#1a1a1a")
        
        self.main_container = ttk.Frame(self.root, style="Custom.TFrame")
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Header
        self.create_header()
        
        # Main content
        self.content = ttk.Frame(self.main_container, style="Custom.TFrame")
        self.content.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        # Left panel - Image preview
        self.create_preview_panel()
        
        # Right panel - Controls
        self.create_control_panel()
        
        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create the header section"""
        header = ttk.Frame(self.main_container, style="Custom.TFrame")
        header.pack(fill=X, padx=20, pady=(20,0))
        
        # Title with glowing effect
        title = ttk.Label(
            header,
            text="QUANTUM IMAGE ENCRYPTOR",
            font=("Helvetica", 24, "bold"),
            foreground="#00ff00"
        )
        title.pack(side=LEFT)
        
        # Theme toggle button
        self.theme_button = ttk.Button(
            header,
            text="🌓",
            style="Outline.TButton",
            command=self.toggle_theme
        )
        self.theme_button.pack(side=RIGHT, padx=10)

    def create_preview_panel(self):
        """Create the image preview panel"""
        self.preview_frame = ttk.LabelFrame(
            self.content,
            text="Image Preview",
            padding=10
        )
        self.preview_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0,10))
        
        # Preview canvas
        self.canvas = tk.Canvas(
            self.preview_frame,
            bg="#2a2a2a",
            highlightthickness=0
        )
        self.canvas.pack(fill=BOTH, expand=YES)
        
        # Drop zone label
        self.drop_label = ttk.Label(
            self.canvas,
            text="Drag & Drop PPM Image\nor Click to Browse",
            font=("Helvetica", 12),
            foreground="#666666"
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Bind click event
        self.canvas.bind("<Button-1>", lambda e: self.select_file())

    def create_control_panel(self):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(
            self.content,
            text="Controls",
            padding=15,
            width=300
        )
        control_frame.pack(side=RIGHT, fill=Y)
        control_frame.pack_propagate(False)
        
        # Scrollable content
        scrolled = ScrolledFrame(control_frame)
        scrolled.pack(fill=BOTH, expand=YES)
        
        # File info section
        self.file_info = ttk.Label(
            scrolled,
            text="No file selected",
            wraplength=250
        )
        self.file_info.pack(fill=X, pady=(0,15))
        
        # Iterations control
        ttk.Label(
            scrolled,
            text="Encryption Iterations:",
            font=("Helvetica", 10, "bold")
        ).pack(anchor=W)
        
        self.iterations_var = tk.StringVar(value="3")
        iterations_frame = ttk.Frame(scrolled)
        iterations_frame.pack(fill=X, pady=(5,15))
        
        self.iterations_scale = ttk.Scale(
            iterations_frame,
            from_=1,
            to=10,
            variable=self.iterations_var,
            command=lambda v: self.iterations_var.set(str(int(float(v))))
        )
        self.iterations_scale.pack(side=LEFT, fill=X, expand=YES, padx=(0,10))
        
        iterations_entry = ttk.Entry(
            iterations_frame,
            textvariable=self.iterations_var,
            width=5
        )
        iterations_entry.pack(side=RIGHT)
        
        # Action buttons
        self.scramble_btn = ttk.Button(
            scrolled,
            text="Scramble Image",
            style="Accent.TButton",
            command=self.scramble_with_animation
        )
        self.scramble_btn.pack(fill=X, pady=5)
        
        self.unscramble_btn = ttk.Button(
            scrolled,
            text="Unscramble Image",
            style="Success.TButton",
            command=self.unscramble_with_animation
        )
        self.unscramble_btn.pack(fill=X, pady=5)
        
        # Recent files
        ttk.Label(
            scrolled,
            text="Recent Files",
            font=("Helvetica", 10, "bold")
        ).pack(anchor=W, pady=(20,5))
        
        self.recent_files_frame = ttk.Frame(scrolled)
        self.recent_files_frame.pack(fill=X)
        self.update_recent_files()

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(
            self.main_container,
            text="Ready",
            anchor=W,
            padding=(10, 5)
        )
        self.status_bar.pack(fill=X, side=BOTTOM)

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.style.theme_use()
        new_theme = "darkly" if current_theme == "litera" else "litera"
        self.style.theme_use(new_theme)
        
        # Show toast notification
        toast = ToastNotification(
            title="Theme Changed",
            message=f"Switched to {new_theme.title()} theme",
            duration=1000
        )
        toast.show_toast()

    def select_file(self):
        """Open file dialog to select an image"""
        path = filedialog.askopenfilename(
            filetypes=[("PPM Images", "*.ppm")],
            title="Select a PPM image file",
            initialdir=self.inputs_dir
        )
        
        if path:
            self.load_image(path)
            self.add_to_recent_files(path)

    def load_image(self, path):
        """Load and display the selected image"""
        try:
            # Load image
            image = Image.open(path)
            
            # Calculate size to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Resize image to fit canvas
            image.thumbnail((canvas_width, canvas_height))
            
            # Convert to PhotoImage
            self.current_image = ImageTk.PhotoImage(image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width//2,
                canvas_height//2,
                image=self.current_image,
                anchor=CENTER
            )
            
            # Update file info
            file_size = os.path.getsize(path) / 1024  # KB
            self.file_info.configure(
                text=f"File: {os.path.basename(path)}\nSize: {file_size:.1f} KB"
            )
            
            # Enable buttons
            self.scramble_btn.configure(state=NORMAL)
            self.unscramble_btn.configure(state=NORMAL)
            
        except Exception as e:
            Messagebox.show_error(
                f"Failed to load image: {str(e)}",
                "Error"
            )

    def add_to_recent_files(self, path):
        """Add file to recent files list"""
        for widget in self.recent_files_frame.winfo_children():
            widget.destroy()
            
        recent_file = ttk.Button(
            self.recent_files_frame,
            text=os.path.basename(path),
            style="Link.TButton",
            command=lambda: self.load_image(path)
        )
        recent_file.pack(anchor=W)

    def show_progress(self, message):
        """Show progress in status bar"""
        self.status_bar.configure(text=message)
        self.root.update()

    def run_background_animation(self):
        """Run background animation effect"""
        while True:
            if not self.is_processing:
                time.sleep(0.1)
                continue
                
            # Create particle effect
            x = random.randint(0, self.canvas.winfo_width())
            y = random.randint(0, self.canvas.winfo_height())
            size = random.randint(2, 5)
            
            particle = self.canvas.create_oval(
                x, y, x+size, y+size,
                fill="#00ff00",
                outline=""
            )
            
            # Animate particle
            for _ in range(10):
                if not self.is_processing:
                    break
                self.canvas.move(particle, 0, 5)
                time.sleep(0.05)
                self.root.update()
            
            self.canvas.delete(particle)

    def scramble_with_animation(self):
        """Scramble image with animation"""
        if not hasattr(self, "current_image"):
            Messagebox.show_warning(
                "Please select an image first",
                "No Image"
            )
            return
            
        self.is_processing = True
        self.scramble_btn.configure(state=DISABLED)
        self.unscramble_btn.configure(state=DISABLED)
        
        try:
            input_path = self.file_info.cget("text").split("\n")[0][6:]  # Extract path
            output_path = os.path.join(
                self.scrambled_dir,
                os.path.basename(input_path).replace(".ppm", "_scrambled.ppm")
            )
            
            iterations = int(self.iterations_var.get())
            
            # Show progress
            self.show_progress("Scrambling image...")
            
            # Call scramble function
            self.lib.scramble(
                input_path.encode(),
                output_path.encode(),
                iterations
            )
            
            # Show success message
            toast = ToastNotification(
                title="Success",
                message="Image scrambled successfully!",
                duration=3000
            )
            toast.show_toast()
            
            # Load scrambled image
            self.load_image(output_path)
            
        except Exception as e:
            Messagebox.show_error(
                f"Failed to scramble image: {str(e)}",
                "Error"
            )
            
        finally:
            self.is_processing = False
            self.scramble_btn.configure(state=NORMAL)
            self.unscramble_btn.configure(state=NORMAL)
            self.show_progress("Ready")

    def unscramble_with_animation(self):
        """Unscramble image with animation"""
        if not hasattr(self, "current_image"):
            Messagebox.show_warning(
                "Please select an image first",
                "No Image"
            )
            return
            
        self.is_processing = True
        self.scramble_btn.configure(state=DISABLED)
        self.unscramble_btn.configure(state=DISABLED)
        
        try:
            input_path = self.file_info.cget("text").split("\n")[0][6:]  # Extract path
            output_path = os.path.join(
                self.output_dir,
                os.path.basename(input_path).replace(".ppm", "_unscrambled.ppm")
            )
            
            iterations = int(self.iterations_var.get())
            
            # Show progress
            self.show_progress("Unscrambling image...")
            
            # Call unscramble function
            self.lib.unscramble(
                input_path.encode(),
                output_path.encode(),
                iterations
            )
            
            # Show success message
            toast = ToastNotification(
                title="Success",
                message="Image unscrambled successfully!",
                duration=3000
            )
            toast.show_toast()
            
            # Load unscrambled image
            self.load_image(output_path)
            
        except Exception as e:
            Messagebox.show_error(
                f"Failed to unscramble image: {str(e)}",
                "Error"
            )
            
        finally:
            self.is_processing = False
            self.scramble_btn.configure(state=NORMAL)
            self.unscramble_btn.configure(state=NORMAL)
            self.show_progress("Ready")

if __name__ == "__main__":
    app = ModernImageEncryptor()
    app.root.mainloop() 