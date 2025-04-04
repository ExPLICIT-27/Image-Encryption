import ctypes
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Load the shared library
if os.name == "nt":
    try:
        lib = ctypes.CDLL(r"image_encryptor.dll")
    except OSError as e:
        print(f"Error loading DLL: {e}")
        exit(1)
else:
    lib = ctypes.CDLL("./libimage_encryptor.so")

# Set function signatures
lib.scramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.unscramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]

def select_file():
    path = filedialog.askopenfilename(filetypes=[("PPM Images", "*.ppm")])
    entry_input.delete(0, tk.END)
    entry_input.insert(0, path)

def scramble_image():
    input_path = entry_input.get()
    output_path = input_path.replace(".ppm", "_scrambled.ppm")
    iterations = int(entry_iterations.get())

    lib.scramble(input_path.encode(), output_path.encode(), iterations)
    messagebox.showinfo("Success", f"Scrambled image saved to:\n{output_path}")

def unscramble_image():
    input_path = entry_input.get()
    output_path = input_path.replace(".ppm", "_unscrambled.ppm")
    iterations = int(entry_iterations.get())

    lib.unscramble(input_path.encode(), output_path.encode(), iterations)
    messagebox.showinfo("Success", f"Unscrambled image saved to:\n{output_path}")

# GUI setup
root = tk.Tk()
root.title("Image Encryptor (Arnold's Cat Map)")
root.geometry("500x200")

tk.Label(root, text="Select PPM Image:").pack()
entry_input = tk.Entry(root, width=50)
entry_input.pack()
tk.Button(root, text="Browse", command=select_file).pack()

tk.Label(root, text="Iterations:").pack()
entry_iterations = tk.Entry(root)
entry_iterations.insert(0, "3")
entry_iterations.pack()

tk.Button(root, text="Scramble", command=scramble_image, bg="lightblue").pack(pady=5)
tk.Button(root, text="Unscramble", command=unscramble_image, bg="lightgreen").pack(pady=5)

root.mainloop()
