import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path
from screeninfo import get_monitors
import src.config as config


class GhostnoteApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.attributes("-alpha", 0.0)
        self.title("GhostNote")

        window_width = 900
        window_height = 650

        mouse_x = self.winfo_pointerx()
        mouse_y = self.winfo_pointery()

        target_monitor = None

        for monitor in get_monitors():
            if (
                    monitor.x <= mouse_x < monitor.x + monitor.width
                    and monitor.y <= mouse_y < monitor.y + monitor.height
            ):
                target_monitor = monitor
                break

        # Fallback to primary monitor
        if target_monitor is None:
            target_monitor = get_monitors()[0]

        # Center on monitor
        x = target_monitor.x + (target_monitor.width - window_width) // 2
        y = target_monitor.y + (target_monitor.height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.minsize(700, 450)

        self.load_icon()
        self.build_header()
        self.build_viewer()
        self.apply_theme()
        self.after(10, self.fade_in)

    def apply_theme(self):
        theme = config.get_theme()

        self.configure(bg=theme["bg"])

        style = ttk.Style()
        style.theme_use("clam")

        if hasattr(self, "title_frame"):
            self.title_frame.configure(bg=theme["bg"])

        if hasattr(self, "title_canvas"):
            self.title_canvas.configure(bg=theme["bg"])

        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["text"])
        style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"], padding=(10, 6), borderwidth=0)
        style.map("TButton", background=[("active", theme["button_hover"]), ("pressed", theme["button_pressed"]), ("disabled", theme["button_disabled"])], foreground=[("active", theme["button_fg"]), ("pressed", theme["button_fg"]), ("disabled", theme["button_disabled_fg"])])
        style.configure("TRadiobutton", background=theme["bg"], foreground=theme["text"])
        style.map("TRadiobutton", background=[("active", theme["bg"])], foreground=[("active", theme["text"])])
        style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"])
        style.map("TEntry", fieldbackground=[("!disabled", theme["entry_bg"])])
        style.configure("Vertical.TScrollbar", background=theme["panel"], troughcolor=theme["bg"], arrowcolor=theme["text"])
        style.map("Vertical.TScrollbar", background=[("active", theme["entry_bg"])])

        self.markdown_view.configure(bg=theme["panel"], fg=theme["text"], insertbackground=theme["text"])
        self.markdown_view.tag_configure("h1", foreground=theme["text"])
        self.markdown_view.tag_configure("h2", foreground=theme["text"])
        self.markdown_view.tag_configure("h3", foreground=theme["text"])
        self.markdown_view.tag_configure("body", foreground=theme["text"])
        self.markdown_view.tag_configure("bullet", foreground=theme["text"])

    def fade_in(self, alpha=0.0):
        alpha += 0.05

        if alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            return

        self.attributes("-alpha", alpha)
        self.after(12, lambda: self.fade_in(alpha))

    def build_header(self):
        theme = config.get_theme()
        header = ttk.Frame(self, padding=(12, 10, 12, 6))
        header.pack(fill=tk.X)

        # Left brand area
        brand_frame = ttk.Frame(header)
        brand_frame.pack(side=tk.LEFT)

        if self.icon:
            icon_label = ttk.Label(brand_frame, image=self.icon)
            icon_label.pack(side=tk.LEFT, padx=(0, 4))

        text_frame = ttk.Frame(brand_frame)
        text_frame.pack(side=tk.LEFT)

        self.title_frame = tk.Frame(text_frame, bg=theme["bg"])
        self.title_frame.pack(anchor="w")

        self.title_canvas = tk.Canvas(self.title_frame, bg=theme["bg"], highlightthickness=0, bd=0, width=185, height=42)
        self.title_canvas.pack(anchor="w")

        font = ("Segoe UI", 22, "bold")
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 0), (1, 1)]:
            self.title_canvas.create_text(0 + dx, 25 + dy, text="Ghost", font=font, fill=theme["title_outline"], anchor="w")
            self.title_canvas.create_text(80 + dx, 25 + dy, text="Note", font=font, fill=theme["title_outline"], anchor="w")

        self.title_canvas.create_text(0, 25, text="Ghost", font=font, fill=theme["title_ghost"], anchor="w")
        self.title_canvas.create_text(80, 25, text="Note", font=font, fill=theme["title_note"], anchor="w")
        ttk.Label(text_frame, text="Helping track your hidden work", font=("Segoe UI", 9)).pack(anchor="w")

        # Right button area
        button_frame = ttk.Frame(header)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="🔍 Search").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="⏷ Filter", command=self.open_filter_modal).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="✦ Analyze", command=self.open_ai_modal).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="⚙ Settings", command=self.open_settings_modal).pack(side=tk.LEFT, padx=4)

    def load_icon(self):
        icon_root = Path(__file__).resolve().parents[1] / "assets" / "icons"

        self.window_icon_path = icon_root / "GhostNote.ico"
        header_icon_path = icon_root / "GhostNote.png"

        if self.window_icon_path.exists():
            self.iconbitmap(self.window_icon_path)

        if header_icon_path.exists():
            image = Image.open(header_icon_path)
            image.thumbnail((69, 49), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(image)
        else:
            self.icon = None

    def build_viewer(self):
        container = ttk.Frame(self, padding=(12, 4, 12, 12))
        container.pack(fill=tk.BOTH, expand=True)

        self.markdown_view = tk.Text(container, wrap=tk.WORD, font=("Consolas", 11), padx=12, pady=12)
        self.markdown_view.tag_configure("h1", font=("Segoe UI", 22, "bold"), spacing1=12, spacing3=8)
        self.markdown_view.tag_configure("h2", font=("Segoe UI", 18, "bold"), spacing1=10, spacing3=6)
        self.markdown_view.tag_configure("h3", font=("Segoe UI", 14, "bold"), spacing1=8, spacing3=4)
        self.markdown_view.tag_configure("body", font=("Segoe UI", 11), lmargin1=10, lmargin2=30)
        self.markdown_view.tag_configure("bullet", lmargin1=25, lmargin2=115, font=("Segoe UI", 11))
        self.markdown_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.markdown_view.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.markdown_view.configure(yscrollcommand=scrollbar.set)

        self.load_markdown_file()

    def load_markdown_file(self):
        try:
            from src.config import LOG_FILE

            if LOG_FILE.exists():
                content = LOG_FILE.read_text(encoding="utf-8")

                self.markdown_view.delete("1.0", tk.END)
                self.render_markdown(content)
                self.after(10, lambda: self.markdown_view.see(tk.END))

            else:
                self.markdown_view.delete("1.0", tk.END)
                self.markdown_view.insert(tk.END, f"Markdown file not found:\n\n{LOG_FILE}")

        except Exception as e:
            self.markdown_view.delete("1.0", tk.END)
            self.markdown_view.insert(tk.END, f"Error loading markdown file:\n\n{e}")

    def render_markdown(self, content):
        self.markdown_view.delete("1.0", tk.END)
        self.markdown_view.configure(tabs=("3c",))

        lines = content.splitlines()

        for line in lines:

            if " - " in line:
                line = line.replace(" - ", ":\t", 1)

            stripped = line.strip()

            if stripped.startswith("### "):
                text = stripped[4:] + "\n"
                self.markdown_view.insert(tk.END, text, "h3")
            elif stripped.startswith("## "):
                text = stripped[3:] + "\n"
                self.markdown_view.insert(tk.END, text, "h2")
            elif stripped.startswith("# "):
                text = stripped[2:] + "\n"
                self.markdown_view.insert(tk.END, text, "h1")
            elif stripped.startswith("- "):
                text = "• " + stripped[2:] + "\n"
                self.markdown_view.insert(tk.END, text, "bullet")
            else:
                self.markdown_view.insert(tk.END, line + "\n", "body")

    def open_settings_modal(self):
        modal = tk.Toplevel(self)
        modal.withdraw()

        theme = config.get_theme()
        modal.configure(bg=theme["bg"])
        modal.title("Settings")
        modal_width = 600
        modal_height = 300
        modal.iconbitmap(self.window_icon_path)

        parent_x = self.winfo_x()
        parent_y = self.winfo_y()

        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        modal.geometry(f"{modal_width}x{modal_height}+{x}+{y}")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text="Settings", font=("Segoe UI", 40, "bold")).pack(pady=(20, 10))

        settings_frame = ttk.Frame(modal, padding=12)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        settings = config.load_settings()

        app_folder_var = tk.StringVar(value=settings["app_folder"])
        log_file_var = tk.StringVar(value=settings["log_file"])
        theme_var = tk.StringVar(value=settings["theme"])

        # APP FOLDER
        ttk.Label(settings_frame, text="APP_FOLDER", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(settings_frame, textvariable=app_folder_var, width=50).grid(row=0, column=1, sticky="ew", pady=4)

        # LOG FILE
        ttk.Label(settings_frame, text="LOG_FILE", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(settings_frame, textvariable=log_file_var, width=50).grid(row=1, column=1, sticky="ew", pady=4)

        # THEME
        ttk.Label(settings_frame, text="THEME", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 12), pady=4)
        theme_button_frame = ttk.Frame(settings_frame)
        theme_button_frame.grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(theme_button_frame, text="Light", variable=theme_var, value="light").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(theme_button_frame, text="Dark", variable=theme_var, value="dark").pack(side=tk.LEFT)

        settings_frame.columnconfigure(1, weight=1)

        def save_and_close():
            settings["app_folder"] = app_folder_var.get().strip()
            settings["log_file"] = log_file_var.get().strip()
            settings["theme"] = theme_var.get()

            config.save_settings(settings)
            config.SETTINGS = config.load_settings()
            config.APP_FOLDER = Path(config.SETTINGS["app_folder"])
            config.LOG_FILE = Path(config.SETTINGS["log_file"])
            config.THEME = config.SETTINGS["theme"]

            self.apply_theme()
            modal.destroy()

        settings_frame.columnconfigure(2, weight=1)

        ttk.Button(modal, text="Save", command=save_and_close).pack(pady=20)
        modal.deiconify()

    def open_ai_modal(self):
        modal = tk.Toplevel(self)
        theme = config.get_theme()
        modal.configure(bg=theme["bg"])
        modal.title("Ai Analyze")
        modal_width = 400
        modal_height = 300

        parent_x = self.winfo_x()
        parent_y = self.winfo_y()

        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        modal.geometry(f"{modal_width}x{modal_height}+{x}+{y}")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text="Ai Analyze", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        ttk.Label(modal, text="Ai controls will go here.").pack(pady=10)
        ttk.Button(modal, text="Close", command=modal.destroy).pack(pady=20)

    def open_filter_modal(self):
        modal = tk.Toplevel(self)
        theme = config.get_theme()
        modal.configure(bg=theme["bg"])
        modal.title("Filter GhostNote")
        modal_width = 400
        modal_height = 300

        parent_x = self.winfo_x()
        parent_y = self.winfo_y()

        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        modal.geometry(f"{modal_width}x{modal_height}+{x}+{y}")
        modal.transient(self)
        modal.grab_set()

        ttk.Label(modal, text="Filter GhostNote", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        ttk.Label(modal, text="Filter will go here.").pack(pady=10)
        ttk.Button(modal, text="Close", command=modal.destroy).pack(pady=20)

if __name__ == "__main__":
    app = GhostnoteApp()
    app.mainloop()
