import ctypes
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import platform

# Create output directories if they don't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Outputs")
scrambled_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Scrambled")

for directory in [output_dir, scrambled_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Load the shared library
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.name == "nt":
        dll_path = os.path.join(current_dir, "image_encryptor.dll")
        print(f"Looking for DLL at: {dll_path}")
        
        # Check if file exists
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Could not find image_encryptor.dll at {dll_path}")
            
        # Check file permissions
        if not os.access(dll_path, os.R_OK):
            raise PermissionError(f"No read access to DLL file at {dll_path}")
            
        # Try to load the DLL
        try:
            lib = ctypes.CDLL(dll_path)
            print("DLL loaded successfully")
        except Exception as dll_error:
            raise Exception(f"Failed to load DLL: {str(dll_error)}")
            
    else:
        so_path = os.path.join(current_dir, "libimage_encryptor.so")
        if not os.path.exists(so_path):
            raise FileNotFoundError(f"Could not find libimage_encryptor.so at {so_path}")
        lib = ctypes.CDLL(so_path)
except Exception as e:
    error_msg = f"""Failed to load required library: {str(e)}
Current directory: {os.getcwd()}
DLL path: {dll_path if 'dll_path' in locals() else 'Not set'}
File exists: {os.path.exists(dll_path) if 'dll_path' in locals() else 'Not checked'}
File size: {os.path.getsize(dll_path) if 'dll_path' in locals() and os.path.exists(dll_path) else 'Not available'}"""
    print(error_msg)
    messagebox.showerror("Error", error_msg)
    exit(1)

# Set function signatures
lib.scramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.unscramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]

def select_file():
    path = filedialog.askopenfilename(
        filetypes=[("PPM Images", "*.ppm")],
        title="Select a PPM image file"
    )
    if path:  # Only update if a file was selected
        entry_input.delete(0, tk.END)
        entry_input.insert(0, path)

def scramble_image():
    try:
        input_path = entry_input.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input image first")
            return
            
        if not input_path.lower().endswith('.ppm'):
            messagebox.showerror("Error", "Please select a PPM image file")
            return
            
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file does not exist: {input_path}")
            return
            
        # Get the base filename without path
        base_filename = os.path.basename(input_path)
        # Create output path in the Scrambled folder
        output_path = os.path.join(scrambled_dir, base_filename.replace(".ppm", "_scrambled.ppm"))
        
        try:
            iterations = int(entry_iterations.get())
            if iterations <= 0:
                raise ValueError("Iterations must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number of iterations")
            return

        lib.scramble(input_path.encode(), output_path.encode(), iterations)
        messagebox.showinfo("Success", f"Scrambled image saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to scramble image: {str(e)}")

def unscramble_image():
    try:
        input_path = entry_input.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input image first")
            return
            
        if not input_path.lower().endswith('.ppm'):
            messagebox.showerror("Error", "Please select a PPM image file")
            return
            
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file does not exist: {input_path}")
            return
            
        # Get the base filename without path
        base_filename = os.path.basename(input_path)
        # Create output path in the Outputs folder
        output_path = os.path.join(output_dir, base_filename.replace(".ppm", "_unscrambled.ppm"))
        
        try:
            iterations = int(entry_iterations.get())
            if iterations <= 0:
                raise ValueError("Iterations must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number of iterations")
            return

        lib.unscramble(input_path.encode(), output_path.encode(), iterations)
        messagebox.showinfo("Success", f"Unscrambled image saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to unscramble image: {str(e)}")

# Load icons
def load_icon(path, size=(24, 24)):
    img = Image.open(path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

# GUI setup with ttkbootstrap
root = ttk.Window(themename="superhero")
root.title("Image Encryptor")
root.geometry("650x500")

# Load icons
upload_icon = load_icon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "IconImages", "upload.png"))
file_icon = load_icon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "IconImages", "file.png"))

# Create main container
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# Title
title_frame = ttk.Frame(main_frame)
title_frame.pack(fill="x", pady=(0, 20))

ttk.Label(title_frame, 
         text="Image Encryptor", 
         font=("Helvetica", 22, "bold")).pack(anchor="w")
ttk.Label(title_frame, 
         text="Secure your images with Arnold's Cat Map algorithm", 
         font=("Helvetica", 11)).pack(anchor="w")

# Main content panel
content_panel = ttk.Frame(main_frame, style="Card.TFrame")
content_panel.pack(fill="both", expand=True)

# Input file selection
input_frame = ttk.Frame(content_panel, padding=20)
input_frame.pack(fill="x", pady=(20, 10))

ttk.Label(input_frame, 
         text="Select PPM Image", 
         font=("Helvetica", 14, "bold")).pack(anchor="w")

file_frame = ttk.Frame(input_frame)
file_frame.pack(fill="x", pady=10)

entry_input = ttk.Entry(file_frame, width=50)
entry_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

browse_button = ttk.Button(file_frame, 
                         text="Browse",
                         image=upload_icon,
                         compound="left",
                         command=select_file,
                         style="Accent.TButton")
browse_button.pack(side="right")

# Separator
ttk.Separator(content_panel).pack(fill="x", padx=20, pady=15)

# Iterations input
iterations_frame = ttk.Frame(content_panel, padding=20)
iterations_frame.pack(fill="x", pady=10)

ttk.Label(iterations_frame, 
         text="Number of Iterations", 
         font=("Helvetica", 14, "bold")).pack(anchor="w")

iterations_entry_frame = ttk.Frame(iterations_frame)
iterations_entry_frame.pack(fill="x", pady=10)

entry_iterations = ttk.Entry(iterations_entry_frame, width=10)
entry_iterations.insert(0, "3")
entry_iterations.pack(side="left", fill="x", expand=False)

# Action buttons
button_frame = ttk.Frame(content_panel, padding=20)
button_frame.pack(fill="x", pady=20)

scramble_button = ttk.Button(button_frame, 
                           text="Scramble",
                           image=file_icon,
                           compound="left",
                           command=scramble_image,
                           style="Accent.TButton",
                           width=20)
scramble_button.pack(side="left", padx=(0, 20))

unscramble_button = ttk.Button(button_frame, 
                             text="Unscramble",
                             image=file_icon,
                             compound="left",
                             command=unscramble_image,
                             style="Success.TButton",
                             width=20)
unscramble_button.pack(side="left")

# Add information about output locations
info_frame = ttk.Frame(content_panel, padding=20)
info_frame.pack(fill="x", pady=10)

info_box = ttk.Frame(info_frame, style="Info.TFrame", padding=15)
info_box.pack(fill="x")

ttk.Label(info_box, 
         text="Output Information", 
         font=("Helvetica", 11)).pack(anchor="w")

ttk.Label(info_box, 
         text=f"• Scrambled images: {scrambled_dir}\n• Unscrambled images: {output_dir}", 
         font=("Helvetica", 9),
         justify="left").pack(anchor="w", pady=(5, 0))

# Version label
ttk.Label(main_frame, 
         text="v1.0", 
         font=("Helvetica", 9)).pack(side="right", pady=(10, 0))

root.mainloop()
