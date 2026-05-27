import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

from pathlib import Path
import tkinter as tk
import src.config as config
from PIL import Image, ImageTk

class PromptWindow:
    def __init__(self, on_submit):
        self.on_submit = on_submit

        self.root = tk.Tk()
        theme = config.get_theme()

        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "GhostNote.png"

        if icon_path.exists():
            # Window icon
            self.window_icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, self.window_icon)

            # Resize display image
            image = Image.open(icon_path)
            image = image.resize((69, 49), Image.LANCZOS)

            self.icon = ImageTk.PhotoImage(image)

        self.root.title("Add GhostNote")
        self.root.configure(bg=theme["bg"])

        # Small utility-style popup
        window_width = 500
        window_height = 100

        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()

        offset_x = 10
        offset_y = -20

        self.root.geometry(f"{window_width}x{window_height}+{mouse_x + offset_x}+{mouse_y + offset_y}")
        self.root.resizable(False, False)

        # Keep window on top
        self.root.attributes("-topmost", True)

        # Main content frame
        frame = tk.Frame(self.root, padx=10, pady=10, bg=theme["bg"])
        frame.pack(fill="both", expand=True)

        # Left side - icon
        icon_frame = tk.Frame(frame, bg=theme["bg"])
        icon_frame.pack(side="left", padx=(0, 10), anchor="n")

        # Show icon inside window
        if icon_path.exists():
            image_label = tk.Label(icon_frame, image=self.icon, bg=theme["bg"])
            image_label.pack(anchor="n", pady=(2, 0))

        # Right side - text content
        content_frame = tk.Frame(frame, bg=theme["bg"])
        content_frame.pack(side="left", fill="both", expand=True)

        # Label
        label = tk.Label(content_frame, text="What are you working on?", bg=theme["bg"], fg=theme["text"], font=("TkDefaultFont", 10, "bold"))
        label.pack(anchor="w")

        # Text entry
        entry_border = tk.Frame(content_frame, bg=theme["border"])
        entry_border.pack(fill="x", pady=(5, 0))

        entry_wrap = tk.Frame(entry_border, bg=theme["entry_bg"])
        entry_wrap.pack(fill="x", padx=1, pady=1)

        self.entry = tk.Entry(entry_wrap, font=("Segoe UI", 12), bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["text"], relief="flat", bd=0)
        self.entry.pack(fill="x", padx=8, pady=4)

        # Auto-focus typing cursor
        self.root.after(100, self.entry.focus_force)

        # Fade in effect
        self.root.attributes("-alpha", 0.0)
        self.root.after(10, self.fade_in)

        # Press Enter to submit
        self.entry.bind("<Return>", self.submit)
        self.root.bind("<Return>", self.submit)

        # ESC to close without submitting
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def submit(self, event=None):
        note_text = self.entry.get().strip()
        self.root.destroy()

        try:
            if note_text:
                self.on_submit(note_text)



        except Exception as e:
            print(f"GhostNote save failed: {e}")

    def run(self):
        self.root.mainloop()

    def fade_in(self, alpha=0.0):
        alpha += 0.10
        if alpha >= 1.0:
            self.root.attributes("-alpha", 1.0)
            return

        self.root.attributes("-alpha", alpha)
        self.root.after(12, lambda: self.fade_in(alpha))