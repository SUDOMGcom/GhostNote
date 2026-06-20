import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from PIL import Image, ImageTk
from src.ui.tooltip import ToolTip
import src.config as config
import src.sqlite_store as store

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.theme = config.get_theme()
        self.nav_buttons = {}

        self.title("GhostNote Settings")
        self.geometry("800x420")
        self.minsize(750, 450)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        if hasattr(parent, "window_icon_path") and parent.window_icon_path.exists():
            self.iconbitmap(parent.window_icon_path)

        self.apply_theme()
        self.build_layout()
        self.select_page("General")

    def build_layout(self):
        self.nav_frame = tk.Frame(self, bg=self.theme["panel"], width=180)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)

        self.logo_row = tk.Frame(self.nav_frame, bg=self.theme["panel"])
        self.logo_row.pack(fill="x", pady=(15, 10))

        self.logo_container = tk.Frame(self.logo_row, bg=self.theme["panel"])
        self.logo_container.pack(anchor="center")

        if hasattr(self.parent, "icon") and self.parent.icon:
            self.logo_photo = self.parent.icon
            self.logo_label = tk.Label(
                self.logo_container,
                image=self.logo_photo,
                bg=self.theme["panel"],
                borderwidth=0,
                highlightthickness=0,
            )
            self.logo_label.pack(side="left")

        self.content_frame = tk.Frame(self, bg=self.theme["bg"])
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.pages = {
            "General": self.show_general_page,
            "Customize Popup": self.show_customize_popup_page,
            "Reminders": self.show_reminders_page,
            "Work Hours": self.show_work_hours_page,
            "Integrations": self.show_integrations_page,
            "AI Settings": self.show_ai_settings_page,
            "About": self.show_about_page,
        }

        for page_name in self.pages:
            button = tk.Button(
                self.nav_frame,
                text=page_name,
                anchor="w",
                relief="flat",
                bg=self.theme["panel"],
                fg=self.theme["text"],
                activebackground=self.theme["button_hover"],
                activeforeground=self.theme["button_fg"],
                command=lambda name=page_name: self.select_page(name),
                padx=12,
                pady=10,
                borderwidth=0,
                highlightthickness=0,
            )
            button.pack(fill="x")
            self.nav_buttons[page_name] = button

    def apply_theme(self):
        self.theme = config.get_theme()
        self.configure(bg=self.theme["bg"])

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.theme["bg"])
        style.configure("TLabel", background=self.theme["bg"], foreground=self.theme["text"])
        style.configure("TButton", background=self.theme["button_bg"], foreground=self.theme["button_fg"], padding=(10, 6), borderwidth=0)
        style.map(
            "TButton",
            background=[
                ("active", self.theme["button_hover"]),
                ("pressed", self.theme["button_pressed"]),
                ("disabled", self.theme["button_disabled"]),
            ],
            foreground=[
                ("active", self.theme["button_fg"]),
                ("pressed", self.theme["button_fg"]),
                ("disabled", self.theme["button_disabled_fg"]),
            ],
        )

        style.configure("TRadiobutton", background=self.theme["bg"], foreground=self.theme["text"])
        style.map("TRadiobutton", background=[("active", self.theme["bg"])], foreground=[("active", self.theme["text"])])

        style.configure("TEntry", fieldbackground=self.theme["entry_bg"], foreground=self.theme["entry_fg"])
        style.map("TEntry", fieldbackground=[("!disabled", self.theme["entry_bg"])])

    def rebuild_window(self, page_name="General"):
        for widget in self.winfo_children():
            widget.destroy()

        self.theme = config.get_theme()
        self.nav_buttons = {}

        self.apply_theme()
        self.build_layout()
        self.select_page(page_name)

    def close_window(self):
        self.destroy()
        if isinstance(self.parent, tk.Tk) and not self.parent.winfo_viewable():
            self.parent.destroy()

    def select_page(self, page_name):
        for name, button in self.nav_buttons.items():
            selected = name == page_name
            button.configure(
                bg=self.theme["button_hover"] if selected else self.theme["panel"],
                fg=self.theme["button_fg"] if selected else self.theme["text"],
                activebackground=self.theme["button_hover"],
                activeforeground=self.theme["button_fg"],
            )

        self.pages[page_name]()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def page_title(self, title, subtitle=None):
        tk.Label(
            self.content_frame,
            text=title,
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=24, pady=(24, 6))

        if subtitle:
            tk.Label(
                self.content_frame,
                text=subtitle,
                bg=self.theme["bg"],
                fg=self.theme["muted"],
                font=("Segoe UI", 10),
                wraplength=580,
                justify="left",
            ).pack(anchor="w", padx=24, pady=(0, 18))

    def show_general_page(self):
        self.clear_content()
        self.page_title("General", "Basic app settings for GhostNote.")

        settings = config.load_settings()

        app_folder_var = tk.StringVar(value=settings["app_folder"])
        db_file_var = tk.StringVar(value=settings["db_file"])
        theme_var = tk.StringVar(value=settings["theme"])

        form = ttk.Frame(self.content_frame, padding=(24, 8, 24, 8))
        form.columnconfigure(1, weight=1)
        form.pack(fill=tk.BOTH, expand=True, anchor="nw")

        def browse_app_folder():
            path = filedialog.askdirectory(initialdir=app_folder_var.get())
            if path:
                app_folder_var.set(path)

        def browse_db_file():
            path = filedialog.askopenfilename(
                initialdir=app_folder_var.get(),
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )
            if path:
                db_file_var.set(path)

        ttk.Label(form, text="Application Directory:").grid(row=0, column=0, sticky="e", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=app_folder_var, width=60, state="readonly").grid(row=0, column=1, sticky="w", pady=6)
        ttk.Button(form, text="Browse", command=browse_app_folder).grid(row=0, column=2, padx=(8, 0), pady=6)

        ttk.Label(form, text="Database Location:").grid(row=1, column=0, sticky="e", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=db_file_var, width=60, state="readonly").grid(row=1, column=1, sticky="w", pady=6)
        ttk.Button(form, text="Browse", command=browse_db_file).grid(row=1, column=2, padx=(8, 0), pady=6)

        ttk.Label(form, text="Theme:").grid(row=2, column=0, sticky="e", padx=(0, 12), pady=6)

        theme_button_frame = ttk.Frame(form)
        theme_button_frame.grid(row=2, column=1, sticky="w", pady=6)

        ttk.Radiobutton(theme_button_frame, text="Light", variable=theme_var, value="light").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(theme_button_frame, text="Dark", variable=theme_var, value="dark").pack(side=tk.LEFT)

        def save_general():
            settings["app_folder"] = app_folder_var.get().strip()
            settings["db_file"] = db_file_var.get().strip()
            settings["theme"] = theme_var.get()

            config.save_settings(settings)
            config.SETTINGS = config.load_settings()
            config.APP_FOLDER = Path(config.SETTINGS["app_folder"])
            config.DB_FILE = Path(config.SETTINGS["db_file"])
            config.THEME = config.SETTINGS["theme"]

            if hasattr(self.parent, "apply_theme"):
                self.parent.apply_theme()

            self.rebuild_window("General")

        def restore_general():
            store.reset_popup_settings()
            app_folder_var.set(store.get_setting("general_appfolder", "Default"))
            db_file_var.set(store.get_setting("general_dbfile", "")) #this will be different
            if hasattr(self.parent, "apply_theme"): self.parent.apply_theme()
            self.rebuild_window("General")

        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Save", command=save_general).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Restore Defaults", command=restore_general, state="disabled").pack(side="left", padx=4)
        ttk.Button(button_frame, text="Restore All Defaults", state="disabled").pack(side="left", padx=4)

    def show_customize_popup_page(self):
        self.clear_content()
        self.page_title("Customize Popup", "Customize the Add GhostNote popup behavior and appearance.")

        customize_frame = ttk.Frame(self.content_frame, padding=12)
        customize_frame.columnconfigure(1, weight=1)
        customize_frame.pack(fill=tk.BOTH, expand=True)

        prompt_var = tk.StringVar(value=store.get_setting("popup_prompt", "What are you working on?"))
        categories_var = tk.StringVar(value=store.get_setting("popup_categories", ""))
        info_character = " \U0001F6C8"

        ttk.Label(customize_frame, text="Prompt question:").grid(row=0, column=0, sticky="e", padx=(0, 12), pady=1)
        ttk.Entry(customize_frame, textvariable=prompt_var, width=40).grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=6)
        ttk.Label(customize_frame, text="Categories:").grid(row=1, column=0, sticky="e", padx=(0, 12), pady=1)
        ttk.Entry(customize_frame, textvariable=categories_var, width=40).grid(row=1, column=1, sticky="ew", padx=(0, 0), pady=6)
        info_label = ttk.Label(customize_frame, text=info_character, font=("Segoe UI", 14))
        info_label.grid(row=1, column=2, sticky="e", padx=(0, 12), pady=(0, 0))
        ToolTip(info_label, "Comma-separated categories\nExample: Automation, Training, Firefighting\nLeaving Blank removes Category Dropdown")

        def save_customize():
            store.set_setting("popup_prompt", prompt_var.get().strip() or "What are you working on?")
            store.set_setting("popup_categories", categories_var.get().strip())
            self.rebuild_window("Customize Popup")

        def restore_customize():
            store.reset_popup_settings()
            prompt_var.set(store.get_setting("popup_prompt", "What are you working on?"))
            categories_var.set(store.get_setting("popup_categories", ""))

        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Save", command=save_customize).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Restore Defaults", command=restore_customize).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Restore All Defaults", state="disabled").pack(side="left", padx=4)


    def show_reminders_page(self):
        self.clear_content()
        self.page_title("Reminders", "Coming Soon: configure time-based and idle reminders.")

    def show_work_hours_page(self):
        self.clear_content()
        self.page_title("Work Hours", "Coming Soon: define when GhostNote should prompt you.")

    def show_integrations_page(self):
        self.clear_content()
        self.page_title("Integrations", "Coming Soon: connect future local integrations.")

    def show_ai_settings_page(self):
        self.clear_content()
        self.page_title("AI Settings", "Coming Soon: configure future Echoes and Signals features.")

    def show_about_page(self):
        self.clear_content()
        self.page_title("About GhostNote", "Operational visibility for hidden work.")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    icon_root = Path(__file__).resolve().parents[2] / "assets" / "icons"
    root.window_icon_path = icon_root / "GhostNote.ico"

    png_path = icon_root / "Settings.png"
    if png_path.exists():
        image = Image.open(png_path)
        image.thumbnail((89, 86), Image.LANCZOS)
        root.icon = ImageTk.PhotoImage(image)
    else:
        root.icon = None

    SettingsWindow(root)
    root.mainloop()