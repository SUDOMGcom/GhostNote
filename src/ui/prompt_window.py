from pathlib import Path
import tkinter as tk
import src.config as config
from PIL import Image, ImageTk

class PromptWindow:
    def __init__(self, on_submit):
        self.on_submit = on_submit

        self.root = tk.Tk()
        theme = config.THEMES.get(
            config.THEME,
            config.THEMES["dark"]
        )

        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "GhostNote.png"

        if icon_path.exists():
            # Window icon
            window_icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, window_icon)

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

        self.root.geometry(
            f"{window_width}x{window_height}+{mouse_x + offset_x}+{mouse_y + offset_y}"
        )      
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
        label = tk.Label(content_frame, text="What did you do?", bg=theme["bg"], fg=theme["text"])
        label.pack(anchor="w")

        # Text entry
        self.entry = tk.Entry(content_frame, font=("Segoe UI", 12),bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["text"])
        self.entry.pack(fill="x", pady=(5, 0))

        # Auto-focus typing cursor
        self.entry.focus()

        # Press Enter to submit
        self.entry.bind("<Return>", self.submit)
        
        #ESC to close without submitting
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def submit(self, event=None):
        note_text = self.entry.get().strip()

        if note_text:
            self.on_submit(note_text)

        self.root.destroy()

    def run(self):
        self.root.mainloop()