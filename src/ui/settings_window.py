import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from PIL import Image, ImageTk
from src.ui.tooltip import ToolTip
import src.config as config
import src.sqlite_store as store
import webbrowser

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, start_page="General"):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.theme = config.get_theme()
        self.nav_buttons = {}

        self.title(f"{config.APP_VENDOR} {config.APP_NAME} v{config.APP_VERSION} - Settings")

        width = 800
        height = 520

        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.center_window(parent, width, height)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        if hasattr(parent, "window_icon_path") and parent.window_icon_path.exists():
            self.iconbitmap(parent.window_icon_path)

        self.current_page = None
        self.page_save_commands = {}
        self.page_restore_keys = {}
        self.page_ignore_buttons = set()
        self.restore_state = None

        self.page_ignore_buttons = {
            "About",
            "Reminders",
            "Work Hours",
            "Integrations",
            "AI Settings",
        }

        self.apply_theme()
        self.build_layout()
        self.select_page(start_page)
        self.deiconify()
        self.lift()

    def build_layout(self):
        self.nav_frame = tk.Frame(self, bg=self.theme["panel"], width=180)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)

        self.logo_row = tk.Frame(self.nav_frame, bg=self.theme["panel"])
        self.logo_row.pack(fill="x", pady=(15, 10))

        self.logo_container = tk.Frame(self.logo_row, bg=self.theme["panel"])
        self.logo_container.pack(anchor="center")

        settings_icon = Path(__file__).resolve().parents[2] / "assets" / "icons" / "Settings.png"

        if settings_icon.exists():
            image = Image.open(settings_icon)
            image.thumbnail((89, 86), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(image)

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

        self.page_frame = tk.Frame(self.content_frame, bg=self.theme["bg"])
        self.page_frame.pack(fill="both", expand=True)

        self.footer_frame = ttk.Frame(self.content_frame)
        self.footer_frame.pack(fill="x", pady=12)

        self.build_footer_buttons()

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

    def center_window(self, parent=None, width=800, height=520):
        self.update_idletasks()

        if parent and parent.winfo_exists() and parent.winfo_viewable():
            x = parent.winfo_x() + (parent.winfo_width() - width) // 2
            y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        else:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def rebuild_window(self, page_name="General"):
        for widget in self.winfo_children():
            widget.destroy()

        self.theme = config.get_theme()
        self.nav_buttons = {}

        self.apply_theme()
        self.build_layout()
        self.select_page(page_name)

    def build_footer_buttons(self):
        self.footer_button_frame = ttk.Frame(self.footer_frame)
        self.footer_button_frame.pack()
        self.save_button = ttk.Button(self.footer_button_frame, text="Save", command=self.save_current_page)
        self.save_button.pack(side="left", padx=4)
        self.restore_button = ttk.Button(self.footer_button_frame, text="Restore Defaults", command=self.prompt_restore_current)
        self.restore_button.pack(side="left", padx=4)
        self.restore_all_button = ttk.Button(self.footer_button_frame, text="Restore All Defaults", command=self.prompt_restore_all)
        self.restore_all_button.pack(side="left", padx=4)
        self.confirm_label = ttk.Label(self.footer_button_frame, text="Confirm?", width=12, anchor="center")

    def prompt_restore_current(self):
        self.restore_state = "page"
        self.save_button.pack_forget()
        self.confirm_label.pack(side=tk.LEFT, padx=4, before=self.restore_button)
        self.restore_button.config(text="Cancel", width=16, command=self.reset_restore_prompt)
        self.restore_all_button.config(text="Restore", width=16, command=self.restore_current_page)

    def prompt_restore_all(self):
        self.restore_state = "all"
        self.save_button.pack_forget()
        self.confirm_label.pack(side=tk.LEFT, padx=4, before=self.restore_button)
        self.restore_button.config(text="Restore All", width=16, command=self.restore_all_defaults)
        self.restore_all_button.config(text="Cancel", width=16, command=self.reset_restore_prompt)

    def reset_restore_prompt(self):
        self.restore_state = None
        self.confirm_label.pack_forget()

        if not self.save_button.winfo_ismapped():
            self.save_button.pack(side=tk.LEFT, padx=4, before=self.restore_button)

        self.restore_button.config(text="Restore Defaults", width=16, command=self.prompt_restore_current)
        self.restore_all_button.config(text="Restore All Defaults", width=16, command=self.prompt_restore_all)

    def update_footer_buttons(self):
        hidden = self.current_page in self.page_ignore_buttons

        if hidden: self.footer_frame.pack_forget()
        else:
            if not self.footer_frame.winfo_manager():
                self.footer_frame.pack(fill="x", pady=12)

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
        self.current_page = page_name
        self.update_footer_buttons()
        self.pages[page_name]()

    def clear_content(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def make_scrollable_content(self):
        canvas = tk.Canvas(self.page_frame, bg=self.theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.page_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scroll_frame

    def page_title(self, title, subtitle=None, url=None):
        tk.Label(
            self.page_frame,
            text=title,
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 18, "bold"),
            justify="left",
        ).pack(anchor="w", padx=24, pady=(24, 0))

        if subtitle:
            tk.Label(
                self.page_frame,
                text=subtitle,
                bg=self.theme["bg"],
                fg=self.theme["muted"],
                font=("Segoe UI", 10),
                wraplength=580,
                justify="left",
            ).pack(anchor="w", padx=24, pady=(0, 0))

        if url:
            import webbrowser

            url_label = tk.Label(
                self.page_frame,
                text="SUDOMG.com/GhostNote",
                bg=self.theme["bg"],
                fg="#4da6ff",
                cursor="hand2",
                font=("Segoe UI", 10, "underline"),
            )
            url_label.pack(anchor="w", padx=24, pady=(0, 0))

            url_label.bind("<Button-1>", lambda e: webbrowser.open(url))
            url_label.bind("<Enter>", lambda e: url_label.configure(fg="#80c1ff"))
            url_label.bind("<Leave>", lambda e: url_label.configure(fg="#4da6ff"))

    def save_current_page(self):
        command = self.page_save_commands.get(self.current_page)
        if command:
            command()
            self.rebuild_window(self.current_page)

    def restore_current_page(self):
        keys = self.page_restore_keys.get(self.current_page)
        if keys:
            store.restore_default_settings(keys)
            self.restore_state = None
            self.rebuild_window(self.current_page)

    def restore_all_defaults(self):
        store.restore_default_settings()
        self.restore_state = None
        self.rebuild_window(self.current_page)

    def show_general_page(self):
        self.clear_content()
        self.page_title("General", "Basic app settings for GhostNote.")

        app_folder_var = tk.StringVar(value=store.get_setting("general_appfolder", ""))
        db_file_var = tk.StringVar(value=config.load_settings().get("db_file", str(config.DB_FILE)))
        theme_var = tk.StringVar(value=store.get_setting("general_theme", "dark"))

        form = ttk.Frame(self.page_frame, padding=(24, 8, 24, 8))
        form.columnconfigure(1, weight=1)
        form.pack(fill=tk.BOTH, expand=True, anchor="nw")

        def browse_db_file():
            path = filedialog.askopenfilename(
                initialdir=app_folder_var.get(),
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )
            if path:
                db_file_var.set(path)

        def copy_app_folder():
            self.clipboard_clear()
            self.clipboard_append(app_folder_var.get())

            copy_button.config(text="✅")
            self.after(1500, lambda: copy_button.config(text="Copy Path"))

        ttk.Label(form, text="Configuration Directory:").grid(row=0, column=0, sticky="e", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=app_folder_var, width=60, state="disabled").grid(row=0, column=1, sticky="w", pady=6)
        copy_button = ttk.Button(form, text="Copy Path", command=copy_app_folder)
        copy_button.grid(row=0, column=2, padx=(8, 0), pady=6)

        ttk.Label(form, text="Database Location:").grid(row=1, column=0, sticky="e", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=db_file_var, width=60, state="readonly").grid(row=1, column=1, sticky="w", pady=6)
        ttk.Button(form, text="Browse", command=browse_db_file).grid(row=1, column=2, padx=(8, 0), pady=6)

        show_welcome_var = tk.BooleanVar(value=store.get_setting("general_show_welcome_on_launch", "true") == "true")
        ttk.Label(form, text="Welcome Screen:").grid(row=2, column=0, sticky="e", padx=(0, 12), pady=6)
        welcome_toggle = tk.Button(form, width=10, relief="flat", bd=1, bg=self.theme["button_bg"], fg=self.theme["button_fg"], activeforeground=self.theme["button_fg"], activebackground=self.theme["button_hover"],)
        welcome_toggle.grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Theme:").grid(row=3, column=0, sticky="e", padx=(0, 12), pady=6)
        theme_button_frame = ttk.Frame(form)
        theme_button_frame.grid(row=3, column=1, sticky="w", pady=6)
        ttk.Radiobutton(theme_button_frame, text="Light", variable=theme_var, value="light").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(theme_button_frame, text="Dark", variable=theme_var, value="dark").pack(side=tk.LEFT)

        def update_welcome_state():
            enabled = show_welcome_var.get()
            welcome_toggle.config(
                text="Enabled" if enabled else "Disabled",
                bg=self.theme["button_bg"] if enabled else "#a62828",
                activebackground=self.theme["button_hover"] if enabled else "#c03030",
            )

        def toggle_welcome():
            show_welcome_var.set(not show_welcome_var.get())
            update_welcome_state()

        welcome_toggle.config(command=toggle_welcome)
        update_welcome_state()

        def save_general():
            db_file = db_file_var.get().strip()
            theme = theme_var.get()

            # SQLite copy = visual/display/settings UI value
            store.set_setting("general_appfolder", str(config.DEFAULT_APP_FOLDER))
            store.set_setting("general_theme", theme)
            store.set_setting("general_show_welcome_on_launch", "true" if show_welcome_var.get() else "false")

            # config.json copy = real source of truth for DB location
            settings = config.load_settings()
            settings["db_file"] = db_file
            config.save_settings(settings)

            config.SETTINGS = config.load_settings()
            config.APP_FOLDER = config.DEFAULT_APP_FOLDER
            config.DB_FILE = Path(config.SETTINGS["db_file"])
            config.THEME = theme

            if hasattr(self.parent, "apply_theme"):
                self.parent.apply_theme()

        self.page_save_commands["General"] = save_general
        self.page_restore_keys["General"] = [
            "general_appfolder",
            "general_theme",
            "general_show_welcome_on_launch",
        ]

    def show_customize_popup_page(self):
        self.clear_content()
        self.page_title("Customize Popup", "Customize the Add GhostNote popup behavior and appearance.")

        customize_frame = ttk.Frame(self.page_frame, padding=12)
        customize_frame.columnconfigure(1, weight=1)
        customize_frame.pack(fill=tk.BOTH, expand=True)

        prompt_var = tk.StringVar(value=store.get_setting("popup_prompt", "What are you working on?"))
        categories_var = tk.StringVar(value=store.get_setting("popup_categories", ""))
        categories_enabled_var = tk.BooleanVar(value=store.get_setting("popup_categories_enabled", "false") == "true")
        info_character = " \U0001F6C8"

        ttk.Label(customize_frame, text="Prompt question:").grid(row=0, column=0, sticky="e", padx=(0, 12), pady=1)
        ttk.Entry(customize_frame, textvariable=prompt_var, width=40).grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=6)

        ttk.Label(customize_frame, text="Categories:").grid(row=1, column=0, sticky="e", padx=(0, 12), pady=6)

        categories_row = ttk.Frame(customize_frame)
        categories_row.grid(row=1, column=1, sticky="ew", pady=6)
        categories_row.columnconfigure(1, weight=1)

        categories_toggle = tk.Button(categories_row, width=10, relief="flat", bd=1, bg=self.theme["button_bg"], fg=self.theme["button_fg"], activeforeground=self.theme["button_fg"], activebackground=self.theme["button_hover"])
        categories_toggle.grid(row=0, column=0, sticky="w", padx=(0, 8))

        categories_entry = ttk.Entry(categories_row, textvariable=categories_var, width=40)
        categories_entry.grid(row=0, column=1, sticky="ew")

        info_label = ttk.Label(categories_row, text=info_character, font=("Segoe UI", 14))
        info_label.grid(row=0, column=2, sticky="e", padx=(8, 0))
        ToolTip(info_label, "Comma-separated categories\nExample: Automation, Training, Firefighting\nLeaving Blank removes Category Dropdown")

        def update_category_state():
            enabled = categories_enabled_var.get()
            categories_toggle.config(text="Enabled" if enabled else "Disabled", bg=self.theme["button_bg"] if enabled else "#a62828", activebackground=self.theme["button_hover"] if enabled else "#c03030")
            categories_entry.config(state="normal" if enabled else "disabled")
            info_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])

        def toggle_categories():
            categories_enabled_var.set(not categories_enabled_var.get())
            update_category_state()

        categories_toggle.config(command=toggle_categories)
        update_category_state()

        def save_customize():
            store.set_setting("popup_prompt", prompt_var.get().strip() or "What are you working on?")
            store.set_setting("popup_categories_enabled", "true" if categories_enabled_var.get() else "false")
            store.set_setting("popup_categories", categories_var.get().strip())

        self.page_save_commands["Customize Popup"] = save_customize
        self.page_restore_keys["Customize Popup"] = ["popup_prompt", "popup_categories", "popup_categories_enabled"]


    def show_reminders_page(self):
        self.clear_content()
        self.page_title("Reminders", "Coming Soon: configure time-based and idle reminders.")

        reminder_frame = ttk.Frame(self.page_frame, padding=12)
        reminder_frame.columnconfigure(1, weight=1)
        reminder_frame.pack(fill=tk.BOTH, expand=True)
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "teasers" / "Reminders.png"
        if icon_path.exists():
            reminder_icon = Image.open(icon_path)
            reminder_icon = reminder_icon.resize((435, 324), Image.LANCZOS)
            self.reminder_icon = ImageTk.PhotoImage(reminder_icon)
            ttk.Label(reminder_frame, image=self.reminder_icon).pack(side=tk.LEFT, padx=(0, 0), expand=True)

    def show_work_hours_page(self):
        self.clear_content()
        self.page_title("Work Hours", "Coming Soon: define when GhostNote should prompt you.")

        workHours_frame = ttk.Frame(self.page_frame, padding=12)
        workHours_frame.columnconfigure(1, weight=1)
        workHours_frame.pack(fill=tk.BOTH, expand=True)
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "teasers" / "WorkHours.png"
        if icon_path.exists():
            workHours_icon = Image.open(icon_path)
            workHours_icon = workHours_icon.resize((435, 324), Image.LANCZOS)
            self.workHours_icon = ImageTk.PhotoImage(workHours_icon)
            ttk.Label(workHours_frame, image=self.workHours_icon).pack(side=tk.LEFT, padx=(0, 0), expand=True)

    def show_integrations_page(self):
        self.clear_content()
        self.page_title("Integrations", "Coming Soon: connect future local integrations.")

        integrations_frame = ttk.Frame(self.page_frame, padding=12)
        integrations_frame.columnconfigure(1, weight=1)
        integrations_frame.pack(fill=tk.BOTH, expand=True)
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "teasers" / "Integrations.png"
        if icon_path.exists():
            integrations_icon = Image.open(icon_path)
            integrations_icon = integrations_icon.resize((435, 324), Image.LANCZOS)
            self.integrations_icon = ImageTk.PhotoImage(integrations_icon)
            ttk.Label(integrations_frame, image=self.integrations_icon).pack(side=tk.LEFT, padx=(0, 0), expand=True)

    def show_ai_settings_page(self):
        self.clear_content()
        self.page_title("AI Settings", "Coming Soon: configure future Echoes and Signals features.")

        ai_frame = ttk.Frame(self.page_frame, padding=12)
        ai_frame.columnconfigure(1, weight=1)
        ai_frame.pack(fill=tk.BOTH, expand=True)
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "teasers" / "AiSettings.png"
        if icon_path.exists():
            ai_icon = Image.open(icon_path)
            ai_icon = ai_icon.resize((435, 324), Image.LANCZOS)
            self.ai_icon = ImageTk.PhotoImage(ai_icon)
            ttk.Label(ai_frame, image=self.ai_icon).pack(side=tk.LEFT, padx=(0, 0), expand=True)

    def show_about_page(self):
        self.clear_content()
        #about_Versiontext = (
        #    f"{config.APP_NAME} by {config.APP_VENDOR}\n"
        #    f"Version: v{config.APP_VERSION}\n"
        #    f"URL: {config.APP_URL}"
        #)

        about_text = (
            f"{config.APP_VENDOR} {config.APP_NAME}\n"
            f"Version: v{config.APP_VERSION}"
        )

        self.page_title(
            about_text,
            #about_text,
            url=config.APP_URL
        )
        #self.page_title("About GhostNote/SUDOMG!", about_Versiontext)

        about_frame = self.make_scrollable_content()
        about_frame.columnconfigure(0, weight=1)

        brand_frame = ttk.Frame(about_frame)
        brand_frame.grid(row=0, column=0, pady=(0, 20))

        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icons" / "ghostnote.png"

        if icon_path.exists():
            about_icon = Image.open(icon_path)
            about_icon = about_icon.resize((32, 32), Image.LANCZOS)

            self.about_icon = ImageTk.PhotoImage(about_icon)
            ttk.Label(brand_frame, image=self.about_icon).pack(side=tk.LEFT, padx=(0, 0))

        text_frame = ttk.Frame(brand_frame)
        text_frame.pack(side=tk.LEFT)

        tk.Label(text_frame, text=config.APP_VENDOR, font=("Segoe UI", 7, "bold"), bg=self.theme["bg"], fg=self.theme["muted"]).pack(anchor="w")

        title_frame = tk.Frame(text_frame, bg=self.theme["bg"])
        title_frame.pack(anchor="w")

        title_canvas = tk.Canvas(title_frame, bg=self.theme["bg"], highlightthickness=0, bd=0, width=185, height=28)
        title_canvas.pack(anchor="w")

        font = ("Segoe UI", 22, "bold")

        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 0), (1, 1)]:
            title_canvas.create_text(0 + dx, 12 + dy, text="Ghost", font=font, fill=self.theme["title_outline"], anchor="w")
            title_canvas.create_text(80 + dx, 12 + dy, text="Note", font=font, fill=self.theme["title_outline"], anchor="w")

        title_canvas.create_text(0, 12, text="Ghost", font=font, fill=self.theme["title_ghost"], anchor="w")
        title_canvas.create_text(80, 12, text="Note", font=font, fill=self.theme["title_note"], anchor="w")
        ttk.Label(text_frame, text="Helping track your hidden work", font=("Segoe UI", 9)).pack(anchor="w")

        about_GNtext = (
            "The most important work often leaves no evidence.\n\n"
            "Sysadmins solve dozens of problems every day that never become tickets,\n"
            "projects, or reports. The quick fixes, troubleshooting, automation, interruptions,\n"
            "and discoveries that keep systems running quietly disappear by the end of the day.\n\n"
            "GhostNote helps you capture that hidden work as it happens. Not as a time tracker,productivity monitor,\n"
            "or journal—but as operational visibility for the work that would otherwise be forgotten.\n\n"
            "Built by IT professionals who spent more time solving problems than documenting them, GhostNote helps ensure your impact doesn't vanish simply because you were too busy doing the work."
        )

        ttk.Label(about_frame,text=about_GNtext,justify="center",wraplength=550).grid(row=1,column=0,padx=20,pady=(0, 20),sticky="ew")




        ttk.Separator(about_frame, orient="horizontal").grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        ttk.Label(about_frame, text="The creators of GhostNote: SUDOMG!", font=("Segoe UI", 16, "bold")).grid(row=3, column=0, pady=(0, 15))

        icon_root = Path(__file__).resolve().parents[2] / "assets" / "icons"
        bg_path = icon_root / "founders.png"

        image_label = tk.Label(about_frame, bg=self.theme["bg"], borderwidth=0, highlightthickness=0)
        image_label.grid(row=4, column=0, sticky="ew", pady=(0, 20))

        def resize_about_image(event=None):
            if not bg_path.exists(): return

            available_width = min(image_label.winfo_width(), 450)
            if available_width <= 1: return

            original = Image.open(bg_path)
            ratio = available_width / original.width
            new_height = int(original.height * ratio)

            resized = original.resize((available_width, new_height), Image.LANCZOS)

            about_frame.bg_photo = ImageTk.PhotoImage(resized)
            image_label.configure(image=about_frame.bg_photo)

        image_label.bind("<Configure>", resize_about_image)

        about_text = (
            "Built by admins. Powered by frustration.\n\n"
            "SUDOMG! started when two IT admins got tired of wrestling "
            "with the same problems day after day. Rather than complaining "
            "about them, we built solutions.\n\n"
            "Every app we create comes from real experience in the trenches "
            "of IT—automating repetitive work, simplifying complex tasks, "
            "and eliminating unnecessary headaches.\n\n"
            "If our tools save you time, reduce your stress, or make you "
            "wonder how you ever lived without them, we've done our job.\n\n"
            "SUDOMG! — Tools so useful they'll make you say "
            "'SUDO-M-GEE!'"
        )

        ttk.Label(about_frame, text=about_text, justify="center", wraplength=550).grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew" )

        url = config.VENDOR_URL
        url_label = tk.Label(about_frame, text="Visit SUDOMG.com", fg="#4da6ff", cursor="hand2", bg=self.theme["bg"], font=("Segoe UI", 9, "underline"))
        url_label.grid(row=6, column=0, pady=(0, 20), sticky="ew")

        url_label.bind("<Button-1>", lambda e: webbrowser.open(url))
        url_label.bind("<Enter>", lambda e: url_label.configure(fg="#80c1ff"))
        url_label.bind("<Leave>", lambda e: url_label.configure(fg="#4da6ff"))

        resize_about_image()

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