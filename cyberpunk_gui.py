import tkinter as tk
import os
import ctypes
from tkinter import filedialog, messagebox
import threading
import time
import random

class CyberpunkEncryptor:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("CYBERPUNK IMAGE ENCRYPTOR v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        self.root.minsize(1200, 800)
        
        # Custom fonts
        self.root.option_add('*Font', ('Courier', 10))
        
        # Load DLL
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            self.lib = ctypes.CDLL(os.path.join(self.base_dir, "image_encryptor.dll"))
            self.lib.scramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
            self.lib.unscramble.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load DLL: {str(e)}")
            exit(1)

        # Create directories
        for dir_name in ["Inputs", "Outputs", "Scrambled"]:
            os.makedirs(os.path.join(self.base_dir, dir_name), exist_ok=True)

        # Initialize variables
        self.current_file = None
        self.is_processing = False
        self.matrix_chars = "10"
        self.matrix_lines = []
        
        self.setup_gui()
        self.start_matrix_animation()

    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title with cyber effect
        title_frame = tk.Frame(main_frame, bg='#0a0a0a')
        title_frame.pack(fill=tk.X, pady=(0, 20))

        self.title_label = tk.Label(
            title_frame,
            text="QUANTUM ENCRYPTION MATRIX",
            font=('Courier', 24, 'bold'),
            fg='#00ff00',
            bg='#0a0a0a'
        )
        self.title_label.pack()
        
        # Subtitle with blinking effect
        self.subtitle = tk.Label(
            title_frame,
            text="< SECURE • ENCRYPT • PROTECT >",
            font=('Courier', 12),
            fg='#00aa00',
            bg='#0a0a0a'
        )
        self.subtitle.pack(pady=(5,0))
        self.blink_subtitle()

        # Content area
        content = tk.Frame(main_frame, bg='#0a0a0a')
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Preview
        left_panel = tk.Frame(content, bg='#0a0a0a', width=800)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Preview area with matrix effect
        self.preview = tk.Canvas(
            left_panel,
            bg='#000000',
            highlightthickness=1,
            highlightbackground='#00ff00'
        )
        self.preview.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Click to select label
        self.select_label = tk.Label(
            self.preview,
            text="[CLICK TO SELECT PPM FILE]",
            font=('Courier', 14),
            fg='#00ff00',
            bg='#000000'
        )
        self.preview.bind('<Button-1>', lambda e: self.select_file())
        
        # Right panel - Controls
        right_panel = tk.Frame(content, bg='#0a0a0a', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # File info
        self.file_info = tk.Label(
            right_panel,
            text="NO FILE SELECTED",
            font=('Courier', 10),
            fg='#00ff00',
            bg='#0a0a0a',
            justify=tk.LEFT,
            wraplength=280
        )
        self.file_info.pack(fill=tk.X, pady=(0, 20))
        
        # Iterations control
        tk.Label(
            right_panel,
            text="ENCRYPTION ITERATIONS:",
            font=('Courier', 10, 'bold'),
            fg='#00ff00',
            bg='#0a0a0a'
        ).pack(anchor=tk.W)
        
        # Custom scale widget
        scale_frame = tk.Frame(right_panel, bg='#0a0a0a')
        scale_frame.pack(fill=tk.X, pady=(5, 20))
        
        self.iter_var = tk.StringVar(value="3")
        
        for i in range(1, 11):
            btn = tk.Button(
                scale_frame,
                text=str(i),
                font=('Courier', 10),
                fg='#00ff00',
                bg='#0a0a0a',
                activebackground='#00ff00',
                activeforeground='#000000',
                bd=1,
                width=2,
                command=lambda x=i: self.iter_var.set(str(x))
            )
            btn.pack(side=tk.LEFT, padx=1)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#003300'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#0a0a0a'))
        
        # Action buttons
        self.scramble_btn = tk.Button(
            right_panel,
            text="[SCRAMBLE]",
            font=('Courier', 12, 'bold'),
            fg='#00ff00',
            bg='#0a0a0a',
            activebackground='#00ff00',
            activeforeground='#000000',
            bd=1,
            height=2,
            command=self.scramble_image
        )
        self.scramble_btn.pack(fill=tk.X, pady=(0, 10))
        
        self.unscramble_btn = tk.Button(
            right_panel,
            text="[UNSCRAMBLE]",
            font=('Courier', 12, 'bold'),
            fg='#00ff00',
            bg='#0a0a0a',
            activebackground='#00ff00',
            activeforeground='#000000',
            bd=1,
            height=2,
            command=self.unscramble_image
        )
        self.unscramble_btn.pack(fill=tk.X)
        
        # Add hover effects to buttons
        for btn in [self.scramble_btn, self.unscramble_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#003300'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg='#0a0a0a'))
        
        # Status bar
        self.status = tk.Label(
            main_frame,
            text="SYSTEM READY",
            font=('Courier', 10),
            fg='#00ff00',
            bg='#0a0a0a',
            anchor=tk.W
        )
        self.status.pack(fill=tk.X, pady=(20, 0))

        # Position the select label
        self.update_select_label()
        self.root.update()

    def update_select_label(self):
        """Update the position of the select label"""
        self.preview.delete('select_label')
        if not self.current_file:
            x = self.preview.winfo_width() // 2
            y = self.preview.winfo_height() // 2
            self.preview.create_window(x, y, window=self.select_label, tag='select_label')

    def blink_subtitle(self):
        """Create blinking effect for subtitle"""
        current_color = self.subtitle.cget('fg')
        new_color = '#00ff00' if current_color == '#00aa00' else '#00aa00'
        self.subtitle.configure(fg=new_color)
        self.root.after(1000, self.blink_subtitle)

    def start_matrix_animation(self):
        """Start the matrix rain animation"""
        def create_line():
            x = random.randint(0, self.preview.winfo_width())
            return {
                'x': x,
                'y': -20,
                'length': random.randint(5, 15),
                'chars': [random.choice(self.matrix_chars) for _ in range(20)],
                'speed': random.uniform(1, 3)
            }

        def animate():
            if not self.current_file and len(self.matrix_lines) < 50:
                if random.random() < 0.1:
                    self.matrix_lines.append(create_line())

            self.preview.delete('matrix')
            
            for line in self.matrix_lines[:]:
                for i, char in enumerate(line['chars']):
                    y = line['y'] + i * 20
                    color = f'#00{hex(int(255 * (1 - i/len(line['chars']))))[2:].zfill(2)}00'
                    self.preview.create_text(
                        line['x'], y,
                        text=char,
                        fill=color,
                        font=('Courier', 14),
                        tags='matrix'
                    )
                
                line['y'] += line['speed']
                
                if random.random() < 0.1:
                    line['chars'] = [random.choice(self.matrix_chars) for _ in range(20)]
                
                if line['y'] > self.preview.winfo_height():
                    self.matrix_lines.remove(line)

            self.preview.tag_lower('matrix')
            self.root.after(50, animate)

        animate()

    def select_file(self):
        """Open file dialog to select an image"""
        path = filedialog.askopenfilename(
            filetypes=[("PPM Images", "*.ppm")],
            title="Select PPM Image",
            initialdir=os.path.join(self.base_dir, "Inputs")
        )
        
        if path:
            self.current_file = path
            self.file_info.configure(
                text=f"SELECTED FILE:\n{os.path.basename(path)}\n\n"
                     f"SIZE: {os.path.getsize(path)/1024:.1f} KB\n"
                     f"PATH: {os.path.dirname(path)}"
            )
            self.status.configure(text="FILE LOADED • READY TO PROCESS")
            self.matrix_lines.clear()
            self.preview.delete('all')
            self.update_select_label()

    def show_processing_animation(self):
        """Show processing animation in the preview"""
        if not self.is_processing:
            return
            
        x = random.randint(0, self.preview.winfo_width())
        y = random.randint(0, self.preview.winfo_height())
        size = random.randint(2, 5)
        
        line = self.preview.create_line(
            x, y, x + random.randint(-50, 50), y + random.randint(-50, 50),
            fill='#00ff00',
            width=1,
            tags='processing'
        )
        
        def fade_line():
            if not self.is_processing:
                self.preview.delete(line)
                return
            
            self.preview.delete(line)
            
        self.root.after(100, fade_line)
        self.root.after(10, self.show_processing_animation)

    def scramble_image(self):
        """Scramble the selected image"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        self.is_processing = True
        self.scramble_btn.configure(state=tk.DISABLED)
        self.unscramble_btn.configure(state=tk.DISABLED)
        self.status.configure(text="SCRAMBLING IMAGE...")
        self.show_processing_animation()
        
        try:
            output_path = os.path.join(
                self.base_dir,
                "Scrambled",
                os.path.basename(self.current_file).replace(".ppm", "_scrambled.ppm")
            )
            
            self.lib.scramble(
                self.current_file.encode(),
                output_path.encode(),
                int(self.iter_var.get())
            )
            
            self.status.configure(text="SCRAMBLE COMPLETE")
            messagebox.showinfo("Success", "Image scrambled successfully!")
            self.current_file = output_path
            
        except Exception as e:
            self.status.configure(text="ERROR DURING SCRAMBLING")
            messagebox.showerror("Error", f"Failed to scramble image: {str(e)}")
            
        finally:
            self.is_processing = False
            self.scramble_btn.configure(state=tk.NORMAL)
            self.unscramble_btn.configure(state=tk.NORMAL)
            self.preview.delete('processing')

    def unscramble_image(self):
        """Unscramble the selected image"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        self.is_processing = True
        self.scramble_btn.configure(state=tk.DISABLED)
        self.unscramble_btn.configure(state=tk.DISABLED)
        self.status.configure(text="UNSCRAMBLING IMAGE...")
        self.show_processing_animation()
        
        try:
            output_path = os.path.join(
                self.base_dir,
                "Outputs",
                os.path.basename(self.current_file).replace(".ppm", "_unscrambled.ppm")
            )
            
            self.lib.unscramble(
                self.current_file.encode(),
                output_path.encode(),
                int(self.iter_var.get())
            )
            
            self.status.configure(text="UNSCRAMBLE COMPLETE")
            messagebox.showinfo("Success", "Image unscrambled successfully!")
            self.current_file = output_path
            
        except Exception as e:
            self.status.configure(text="ERROR DURING UNSCRAMBLING")
            messagebox.showerror("Error", f"Failed to unscramble image: {str(e)}")
            
        finally:
            self.is_processing = False
            self.scramble_btn.configure(state=tk.NORMAL)
            self.unscramble_btn.configure(state=tk.NORMAL)
            self.preview.delete('processing')

if __name__ == "__main__":
    app = CyberpunkEncryptor()
    app.root.mainloop() 