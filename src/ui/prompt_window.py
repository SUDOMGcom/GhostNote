import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

class PromptWindow:
    def __init__(self, on_submit):
        self.on_submit = on_submit

        self.root = tk.Tk()

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
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Left side - icon
        icon_frame = tk.Frame(frame)
        icon_frame.pack(side="left", padx=(0, 10), anchor="n")

        # Show icon inside window
        if icon_path.exists():
            image_label = tk.Label(icon_frame, image=self.icon)
            image_label.pack(anchor="n", pady=(2, 0))

        # Right side - text content
        content_frame = tk.Frame(frame)
        content_frame.pack(side="left", fill="both", expand=True)

        # Label
        label = tk.Label(content_frame, text="What did you do?")
        label.pack(anchor="w")

        # Text entry
        self.entry = tk.Entry(content_frame, font=("Segoe UI", 12))
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