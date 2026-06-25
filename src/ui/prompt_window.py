import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

from pathlib import Path
import tkinter as tk
import src.config as config
from src.sqlite_store import get_setting
from PIL import Image, ImageTk
from tkinter import ttk

class PromptWindow:
    def __init__(self, on_submit):
        self.on_submit = on_submit

        self.root = tk.Tk()
        theme = config.get_theme()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=theme["entry_bg"], background=theme["panel"], foreground=theme["entry_fg"], arrowcolor=theme["text"], bordercolor=theme["border"], lightcolor=theme["border"], darkcolor=theme["border"])
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"]), ("focus", theme["entry_bg"]), ("active", theme["entry_bg"]), ],
            foreground=[("readonly", theme["entry_fg"]),("focus", theme["entry_fg"]),("active", theme["entry_fg"]),],
            selectbackground=[("readonly", theme["entry_bg"]), ("focus", theme["entry_bg"]),("active", theme["entry_bg"]),],
            selectforeground=[("readonly", theme["entry_fg"]), ("focus", theme["entry_fg"]), ("active", theme["entry_fg"]),],
                  )
        self.root.option_add("*TCombobox*Listbox.background", theme["entry_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", theme["entry_fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", theme["panel"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", theme["text"])

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

        #get popup customization
        popup_prompt = get_setting("popup_prompt", "What are you working on?")
        popup_categories_enabled = get_setting("popup_categories_enabled", "false") == "true"
        popup_categories = [c.strip() for c in get_setting("popup_categories", "").split(",") if c.strip()] if popup_categories_enabled else []

        # Label
        label = tk.Label(content_frame, text=popup_prompt, bg=theme["bg"], fg=theme["text"], font=("TkDefaultFont", 10, "bold"))
        label.pack(anchor="w")

        # Text entry
        entry_row = tk.Frame(content_frame, bg=theme["bg"])
        entry_row.pack(fill="x", pady=(5, 0))

        if popup_categories:
            self.category_var = tk.StringVar(value=popup_categories[0])
            category_menu = ttk.Combobox(entry_row, textvariable=self.category_var, values=popup_categories, state="readonly", width=14, style="TCombobox")
            category_menu.pack(side="left", padx=(0, 6))
            category_menu.bind("<<ComboboxSelected>>", lambda e: e.widget.selection_clear())

        entry_border = tk.Frame(entry_row, bg=theme["border"])
        entry_border.pack(side="left", fill="x", expand=True)

        entry_wrap = tk.Frame(entry_border, bg=theme["entry_bg"])
        entry_wrap.pack(fill="x", padx=1, pady=1)

        self.entry = tk.Entry(entry_wrap, font=("Segoe UI", 12), bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"], insertwidth=2, relief="flat", bd=0)
        self.entry.pack(fill="x", padx=8, pady=4)

        # Auto-focus typing cursor
        self.root.after(100, lambda: (self.entry.focus_force(), self.entry.icursor(tk.END)))

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
        category = getattr(self, "category_var", None)
        self.root.destroy()

        try:
            if note_text:
                self.on_submit(note_text, category.get() if category else "")

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