import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from PIL import Image, ImageTk
from src.ui.tooltip import ToolTip
import src.config as config
import src.sqlite_store as store
import src.task_scheduler as task_scheduler
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
        self.save_status_after_id = None

        self.page_ignore_buttons = {
            "About",
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
        self.footer_frame.pack(fill="x", pady=(0, 10))

        self.build_footer_buttons()

        self.pages = {
            "General": self.show_general_page,
            "Customize Popup": self.show_customize_popup_page,
            "Scheduling": self.show_scheduling_page,
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
        style.map("TButton",background=[("active", self.theme["button_hover"]),("pressed", self.theme["button_pressed"]),("disabled", self.theme["button_disabled"]),], foreground=[("active", self.theme["button_fg"]),("pressed", self.theme["button_fg"]),("disabled", self.theme["button_disabled_fg"]),],)

        style.configure("TRadiobutton", background=self.theme["bg"], foreground=self.theme["text"])
        style.map("TRadiobutton", background=[("active", self.theme["bg"])], foreground=[("active", self.theme["text"])])

        style.configure("TCheckbutton", background=self.theme["bg"], foreground=self.theme["text"])
        style.map("TCheckbutton", background=[("active", self.theme["bg"])], foreground=[("active", self.theme["text"])])

        style.configure("TCombobox", fieldbackground=self.theme["entry_bg"], background=self.theme["button_bg"],foreground=self.theme["entry_fg"], arrowcolor=self.theme["button_fg"])
        style.map("TCombobox", fieldbackground=[("readonly", self.theme["entry_bg"])], foreground=[("readonly", self.theme["entry_fg"])])

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
        self.status_frame = ttk.Frame(self.footer_frame)
        self.status_frame.pack()
        self.save_status = ttk.Label(self.status_frame, text="")
        self.save_status.pack(side=tk.LEFT)
        self.save_status_info = ttk.Label(self.status_frame, text=" ⓘ", foreground=self.theme["muted"], cursor="hand2")
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
                self.footer_frame.pack(fill="x", pady=(0, 10))

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
        self.save_button.config(state="normal")
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

    def page_title(self, title, subtitle=None, url=None, info=None):
        title_frame = tk.Frame(self.page_frame, bg=self.theme["bg"])
        title_frame.pack(anchor="w", padx=24, pady=(24, 0))

        tk.Label(title_frame, text=title, bg=self.theme["bg"], fg=self.theme["text"], font=("Segoe UI", 18, "bold"), justify="left", ).pack(side=tk.LEFT)

        if info:
            info_label = tk.Label(title_frame, text=" ⓘ", bg=self.theme["bg"], fg=self.theme["muted"], cursor="hand2", font=("Segoe UI", 11))
            info_label.pack(side=tk.LEFT, padx=(4, 0))
            ToolTip(info_label, info)

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
            self.save_status.config(text="")
            self.update()

            self.save_status.config(text="Saving...")
            self.update()

            result = command() or "Saved successfully."
            message, info = result if isinstance(result, tuple) else (result, None)

            self.rebuild_window(self.current_page)
            self.after_idle(lambda: self.show_save_status(message, info))

    def show_save_status(self, message, info=None):
        if self.save_status_after_id:
            self.after_cancel(self.save_status_after_id)
            self.save_status_after_id = None
        self.save_status.config(text=message, foreground="#e05252" if info else self.theme["text"], font=("Segoe UI", 9, "bold") if info else ("Segoe UI", 9))
        self.save_status_info.pack_forget()

        if info:
            self.save_status_info.config(foreground="#e05252")
            self.save_status_info.pack(side=tk.LEFT, padx=(4, 0))
            ToolTip(self.save_status_info, info)
        else:
            self.save_status_after_id = self.after(7000, self.clear_save_status)

    def clear_save_status(self):
        self.save_status_after_id = None
        self.save_status.config(text="")
        self.save_status_info.pack_forget()

    def restore_current_page(self):
        keys = self.page_restore_keys.get(self.current_page)
        if keys:
            self.save_status.config(text="Restoring Defaults...")
            self.update_idletasks()

            store.restore_default_settings(keys)

            scheduler_error = False

            if self.current_page == "Scheduling":
                try: task_scheduler.remove_task()
                except Exception: scheduler_error = True

            self.restore_state = None
            self.rebuild_window(self.current_page)

            if scheduler_error:
                scheduler_help = "Scheduling troubleshooting\n\nTry restoring defaults again. If the problem continues, make sure Windows Task Scheduler is available and allowed on this computer.\n\nThe GhostNote settings were restored, but you may need to manually remove the task from Windows Task Scheduler.\n\nTask name: GhostNote Capture Prompts"
                self.after_idle(lambda: self.show_save_status("Defaults restored, but the Windows task could not be removed. Try again.", scheduler_help))
            else:
                self.after_idle(lambda: self.show_save_status("Defaults restored successfully."))

    def restore_all_defaults(self):
        self.save_status.config(text="Restoring All Defaults...")
        self.update_idletasks()

        store.restore_default_settings()

        scheduler_error = False

        try: task_scheduler.remove_task()
        except Exception: scheduler_error = True

        self.restore_state = None
        self.rebuild_window(self.current_page)

        if scheduler_error:
            scheduler_help = "Scheduling troubleshooting\n\nTry restoring defaults again. If the problem continues, make sure Windows Task Scheduler is available and allowed on this computer.\n\nThe GhostNote settings were restored, but you may need to manually remove the task from Windows Task Scheduler.\n\nTask name: GhostNote Capture Prompts"
            self.after_idle(lambda: self.show_save_status("All defaults restored, but the Windows task could not be removed. Try again.", scheduler_help))
        else:
            self.after_idle(lambda: self.show_save_status("All defaults restored successfully."))

    def show_general_page(self):
        self.clear_content()
        self.page_title("General", "Basic app settings for GhostNote.")

        app_folder_var = tk.StringVar(value=str(config.DEFAULT_APP_FOLDER))
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

            # SQLite-backed general settings
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

    def show_scheduling_page(self):
        self.clear_content()
        self.page_title("Scheduling", "Configure when GhostNote should prompt you to capture your work.", info="How scheduling works\n\nGhostNote uses Windows Task Scheduler to launch capture prompts at your configured times. Enabling Capture Prompts creates a Windows scheduled task; disabling them removes it.\n\nTask name: GhostNote Capture Prompts", )
        scheduling_frame = ttk.Frame(self.page_frame, padding=(24, 16, 24, 8))
        scheduling_frame.pack(fill=tk.BOTH, expand=True, anchor="nw")
        scheduling_frame.columnconfigure(0, minsize=120)
        scheduling_frame.columnconfigure(1, minsize=365, weight=1)

        work_hours_header = ttk.Frame(scheduling_frame)
        work_hours_header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(work_hours_header, text="Work Hours", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 12))

        work_hours_toggle = tk.Button(work_hours_header, width=8, relief="flat", borderwidth=0, highlightthickness=0)
        work_hours_toggle.pack(side=tk.LEFT)
        work_hours_enabled_var = tk.BooleanVar(value=store.get_setting("schedule_work_hours_enabled", "false") == "true")

        saved_days = {int(day) for day in store.get_setting("schedule_work_days", "1,2,3,4,5").split(",") if day.strip()}
        day_vars = [tk.BooleanVar(value=day in saved_days) for day in range(7)]

        days_frame = ttk.Frame(scheduling_frame)
        days_frame.grid(row=1, column=1, sticky="w", pady=6)

        work_days_label = ttk.Label(scheduling_frame, text="Work days:")
        work_days_label.grid(row=1, column=0, sticky="e", padx=(0, 12), pady=6)

        day_buttons = []

        def update_day_buttons():
            enabled = work_hours_enabled_var.get()

            for day, button in enumerate(day_buttons):
                selected = day_vars[day].get()
                button.config(state="normal" if enabled else "disabled", bg=self.theme["button_bg"] if selected and enabled else self.theme["bg"], fg=self.theme["button_fg"] if selected and enabled else self.theme["muted"], disabledforeground=self.theme["muted"], activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], )

        def toggle_day(day):
            day_vars[day].set(not day_vars[day].get())
            update_day_buttons()
            update_preview()

        for day, label in enumerate(("S", "M", "T", "W", "T", "F", "S")):
            button = tk.Button(
                days_frame,
                text=label,
                width=2,
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                command=lambda day=day: toggle_day(day),
            )
            button.pack(side=tk.LEFT, padx=(0, 4))
            day_buttons.append(button)

        def time_vars(setting, default):
            hour, minute = map(int, store.get_setting(setting, default).split(":"))
            return (
                tk.StringVar(value=str(hour % 12 or 12)),
                tk.StringVar(value=f"{minute:02d}"),
                tk.StringVar(value="PM" if hour >= 12 else "AM"),
            )

        start_hour, start_minute, start_period = time_vars("schedule_work_start", "08:00")
        end_hour, end_minute, end_period = time_vars("schedule_work_end", "17:00")

        def add_time_row(row, label, hour_var, minute_var, period_var):
            time_label = ttk.Label(scheduling_frame, text=label)
            time_label.grid(row=row, column=0, sticky="e", padx=(0, 12), pady=6)

            frame = ttk.Frame(scheduling_frame)
            frame.grid(row=row, column=1, sticky="w", pady=6)

            hour_spin = tk.Spinbox(frame, from_=1, to=12, textvariable=hour_var, width=2, wrap=True, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], buttonbackground=self.theme["panel"], relief="sunken", borderwidth=1, highlightthickness=0)
            hour_spin.pack(side=tk.LEFT)

            ttk.Label(frame, text=":").pack(side=tk.LEFT, padx=3)

            minute_spin = tk.Spinbox(frame, values=tuple(f"{i:02d}" for i in range(0, 60, 5)), width=2, wrap=True, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], buttonbackground=self.theme["panel"], relief="sunken", borderwidth=1, highlightthickness=0)
            minute_spin.pack(side=tk.LEFT)
            minute_spin.config(textvariable=minute_var)

            def toggle_period(): period_var.set("PM" if period_var.get() == "AM" else "AM")

            period_button = tk.Button(frame, textvariable=period_var, width=4, relief="flat", borderwidth=0, highlightthickness=0, bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], command=toggle_period)
            period_button.pack(side=tk.LEFT, padx=(6, 0))

            return time_label, hour_spin, minute_spin, period_button

        start_time_controls = add_time_row(2, "Start time:", start_hour, start_minute, start_period)
        end_time_controls = add_time_row(3, "End time:", end_hour, end_minute, end_period)

        def update_work_hours_state():
            enabled = work_hours_enabled_var.get()
            state = "normal" if enabled else "disabled"

            work_hours_toggle.config(text="Enabled" if enabled else "Disabled", bg=self.theme["button_bg"] if enabled else "#a62828", fg=self.theme["button_fg"], activebackground=self.theme["button_hover"] if enabled else "#c03030", activeforeground=self.theme["button_fg"], )
            work_days_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])
            update_day_buttons()

            for controls in (start_time_controls, end_time_controls):
                label, hour_spin, minute_spin, period_button = controls

                label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])

                for spin in (hour_spin, minute_spin):
                    spin.config(state=state, disabledbackground=self.theme["bg"], disabledforeground=self.theme["muted"], )

                period_button.config(state=state, bg=self.theme["button_bg"] if enabled else self.theme["bg"], fg=self.theme["button_fg"] if enabled else self.theme["muted"], disabledforeground=self.theme["muted"], )

        def toggle_work_hours():
            work_hours_enabled_var.set(not work_hours_enabled_var.get())
            update_work_hours_state()
            update_specific_hour_buttons()
            update_preview()

        work_hours_toggle.config(command=toggle_work_hours)
        update_work_hours_state()

        tk.Frame(scheduling_frame, height=1, bg=self.theme["muted"]).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(18, 14))
        capture_prompts_header = ttk.Frame(scheduling_frame)
        capture_prompts_header.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(capture_prompts_header, text="Capture Prompts", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 12))

        schedule_toggle = tk.Button(capture_prompts_header, width=8, relief="flat", borderwidth=0, highlightthickness=0, fg=self.theme["button_fg"], activeforeground=self.theme["button_fg"])
        schedule_toggle.pack(side=tk.LEFT)

        schedule_enabled_var = tk.BooleanVar(value=store.get_setting("schedule_enabled", "false") == "true")
        schedule_type_var = tk.StringVar(value=store.get_setting("schedule_type", "interval"))
        interval_var = tk.StringVar(value=store.get_setting("schedule_interval_hours", "2"))
        specific_hours = {int(hour) for hour in store.get_setting("schedule_specific_hours", "8,10,12,14,16").split(",") if hour.strip()}
        specific_minute_var = tk.StringVar(value=store.get_setting("schedule_specific_minute", "00"))
        specific_period_var = tk.StringVar(value="AM")

        def update_schedule_toggle():
            enabled = schedule_enabled_var.get()
            schedule_toggle.config(text="Enabled" if enabled else "Disabled", bg=self.theme["button_bg"] if enabled else "#a62828", activebackground=self.theme["button_hover"] if enabled else "#c03030")

        def toggle_schedule():
            schedule_enabled_var.set(not schedule_enabled_var.get())
            update_schedule_toggle()
            update_schedule_type()

        schedule_toggle.config(command=toggle_schedule)
        update_schedule_toggle()

        schedule_type_label = ttk.Label(scheduling_frame, text="Schedule type:")
        schedule_type_label.grid(row=6, column=0, sticky="e", padx=(0, 12), pady=6)

        type_frame = ttk.Frame(scheduling_frame)
        type_frame.grid(row=6, column=1, sticky="w", pady=6)

        interval_border = tk.Frame(type_frame, bg=self.theme["button_bg"], padx=1, pady=1)
        interval_border.pack(side=tk.LEFT, padx=(0, 4))
        interval_button = tk.Button(interval_border, text="Interval", width=10, relief="flat", borderwidth=0, highlightthickness=0)
        interval_button.pack()

        specific_border = tk.Frame(type_frame, bg=self.theme["button_bg"], padx=1, pady=1)
        specific_border.pack(side=tk.LEFT)
        specific_button = tk.Button(specific_border, text="Specific Times", width=12, relief="flat", borderwidth=0, highlightthickness=0)
        specific_button.pack()

        interval_frame = ttk.Frame(scheduling_frame)
        specific_frame = ttk.Frame(scheduling_frame)

        every_label = ttk.Label(interval_frame, text="Every:")
        every_label.pack(side=tk.LEFT, padx=(0, 12))
        interval_spin = tk.Spinbox(interval_frame, from_=1, to=12, textvariable=interval_var, width=2, wrap=True, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], buttonbackground=self.theme["panel"], relief="sunken", borderwidth=1, highlightthickness=0)
        interval_spin.pack(side=tk.LEFT)
        hours_label = ttk.Label(interval_frame, text="hours")
        hours_label.pack(side=tk.LEFT, padx=(6, 0))

        period_frame = ttk.Frame(specific_frame)
        period_frame.pack(side=tk.LEFT, padx=(0, 8))

        period_buttons = []

        def update_period_buttons():
            enabled = schedule_enabled_var.get()

            for period, button in zip(("AM", "PM"), period_buttons):
                selected = specific_period_var.get() == period
                button.config(state="normal" if enabled else "disabled", bg=self.theme["button_bg"] if selected and enabled else self.theme["bg"], fg=self.theme["button_fg"] if selected and enabled else self.theme["muted"], disabledforeground=self.theme["muted"], activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], )

        def set_specific_period(period):
            specific_period_var.set(period)
            update_period_buttons()
            update_specific_hour_buttons()

        for period in ("AM", "PM"):
            button = tk.Button(period_frame, text=period, width=4, relief="flat", borderwidth=0, highlightthickness=0, command=lambda period=period: set_specific_period(period))
            button.pack(side=tk.LEFT, padx=(0, 4))
            period_buttons.append(button)

        hours_frame = ttk.Frame(specific_frame)
        hours_frame.pack(side=tk.LEFT)

        hour_buttons = []

        def hour_24(hour):
            return hour % 12 + (12 if specific_period_var.get() == "PM" else 0)

        def update_specific_hour_buttons():
            try:
                enabled = schedule_enabled_var.get()
                work_hours_enabled = work_hours_enabled_var.get()
                start = (int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)) * 60 + int(start_minute.get())
                end = (int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)) * 60 + int(end_minute.get())
                minute = int(specific_minute_var.get())

                for hour, button in zip((12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), hour_buttons):
                    value = hour_24(hour)
                    selected = value in specific_hours
                    available = not work_hours_enabled or start <= value * 60 + minute <= end
                    active = enabled and available

                    button.config(state="normal" if active else "disabled", bg=self.theme["button_bg"] if selected and active else self.theme["bg"], fg=self.theme["button_fg"] if selected and active else self.theme["muted"], disabledforeground="#555555" if store.get_setting("general_theme", "dark") == "dark" else "#b0b0b0", activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], )
            except ValueError:
                pass

        def toggle_specific_hour(hour):
            value = hour_24(hour)
            if value in specific_hours:
                specific_hours.remove(value)
            else:
                specific_hours.add(value)
            update_specific_hour_buttons()
            update_preview()

        for index, hour in enumerate((12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)):
            button = tk.Button(hours_frame, text=str(hour), width=2, relief="flat", borderwidth=0, highlightthickness=0, command=lambda hour=hour: toggle_specific_hour(hour))
            button.grid(row=0, column=index, padx=(0, 2))
            hour_buttons.append(button)

        minute_frame = ttk.Frame(scheduling_frame)
        minute_frame.grid(row=8, column=1, sticky="w", pady=6)
        minute_spacer = ttk.Frame(scheduling_frame, height=30)
        minute_label = ttk.Label(minute_frame, text="Minute:")
        minute_label.pack(side=tk.LEFT, padx=(0, 8))
        minute_spin = tk.Spinbox(minute_frame, values=tuple(f"{i:02d}" for i in range(0, 60, 5)), width=2, wrap=True, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], buttonbackground=self.theme["panel"], relief="sunken", borderwidth=1, highlightthickness=0)
        minute_spin.pack(side=tk.LEFT)
        minute_spin.config(textvariable=specific_minute_var)

        def update_schedule_type():
            enabled = schedule_enabled_var.get()
            interval_selected = schedule_type_var.get() == "interval"
            state = "normal" if enabled else "disabled"

            schedule_type_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])

            interval_button.config(state=state, bg=self.theme["button_bg"] if interval_selected and enabled else self.theme["bg"], fg=self.theme["button_fg"] if interval_selected and enabled else self.theme["muted"], disabledforeground=self.theme["muted"], activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], )

            specific_button.config(state=state, bg=self.theme["button_bg"] if not interval_selected and enabled else self.theme["bg"], fg=self.theme["button_fg"] if not interval_selected and enabled else self.theme["muted"], disabledforeground=self.theme["muted"], activebackground=self.theme["button_hover"], activeforeground=self.theme["button_fg"], )

            interval_frame.grid_forget()
            specific_frame.grid_forget()
            minute_frame.grid_forget()
            minute_spacer.grid_forget()

            if interval_selected:
                interval_frame.grid(row=7, column=1, sticky="w", pady=6)
                minute_spacer.grid(row=8, column=1, sticky="w")

                every_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])
                hours_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])
                interval_spin.config(state=state, disabledbackground=self.theme["bg"], disabledforeground=self.theme["muted"], )
            else:
                specific_frame.grid(row=7, column=1, sticky="w", pady=6)
                minute_frame.grid(row=8, column=1, sticky="w", pady=6)

                minute_label.config(foreground=self.theme["text"] if enabled else self.theme["muted"])
                minute_spin.config(state=state, disabledbackground=self.theme["bg"], disabledforeground=self.theme["muted"], )

                update_period_buttons()
                update_specific_hour_buttons()

            update_preview()

        def set_schedule_type(schedule_type):
            schedule_type_var.set(schedule_type)
            update_schedule_type()

        interval_button.config(command=lambda: set_schedule_type("interval"))
        specific_button.config(command=lambda: set_schedule_type("specific"))

        ttk.Label(scheduling_frame, text="Preview:", foreground=self.theme["muted"]).grid(row=9, column=0, sticky="ne", padx=(0, 12), pady=(18, 6))

        preview_var = tk.StringVar()
        preview_label = ttk.Label(scheduling_frame, textvariable=preview_var, foreground=self.theme["muted"], wraplength=400, justify="left")
        preview_label.grid(row=9, column=1, sticky="w", pady=(18, 6))

        def update_preview(*args):
            try:
                if not schedule_enabled_var.get():
                    self.save_button.config(state="normal")
                    preview_var.set("Capture prompts are disabled.")
                    return

                work_hours_enabled = work_hours_enabled_var.get()

                if work_hours_enabled:
                    if not any(var.get() for var in day_vars):
                        self.save_button.config(state="disabled")
                        preview_var.set("Select at least one work day.")
                        return

                    start = (int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)) * 60 + int(start_minute.get())
                    end = (int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)) * 60 + int(end_minute.get())

                    if end <= start:
                        self.save_button.config(state="disabled")
                        preview_var.set("End time must be after start time.")
                        return

                if schedule_type_var.get() == "specific" and not specific_hours:
                    self.save_button.config(state="disabled")
                    preview_var.set("Select at least one capture time.")
                    return

                self.save_button.config(state="normal")

                if schedule_type_var.get() == "specific":
                    minute = int(specific_minute_var.get())
                    times = []

                    if work_hours_enabled:
                        start = (int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)) * 60 + int(start_minute.get())
                        end = (int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)) * 60 + int(end_minute.get())

                    for hour in sorted(specific_hours):
                        if work_hours_enabled and not start <= hour * 60 + minute <= end: continue
                        display_hour = hour % 12 or 12
                        period = "PM" if hour >= 12 else "AM"
                        times.append(f"{display_hour}:{minute:02d} {period}")

                    preview_var.set(", ".join(times))
                    return

                if work_hours_enabled:
                    start_hour_24 = int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)
                    end_hour_24 = int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)
                    start_minutes = start_hour_24 * 60 + int(start_minute.get())
                    end_minutes = end_hour_24 * 60 + int(end_minute.get())
                else:
                    start_minutes = 0
                    end_minutes = 24 * 60

                interval_minutes = int(interval_var.get()) * 60
                times = []
                current = start_minutes

                while current < end_minutes:
                    hour, minute = divmod(current, 60)
                    display_hour = hour % 12 or 12
                    period = "PM" if hour >= 12 else "AM"
                    times.append(f"{display_hour}:{minute:02d} {period}")
                    current += interval_minutes

                preview_var.set(", ".join(times))
            except ValueError:
                preview_var.set("")

        for var in (start_hour, start_minute, start_period, end_hour, end_minute, end_period, interval_var, specific_minute_var): var.trace_add("write", update_preview)
        for var in (start_hour, start_minute, start_period, end_hour, end_minute, end_period, specific_minute_var): var.trace_add("write", lambda *_: update_specific_hour_buttons())
        update_period_buttons()
        update_specific_hour_buttons()
        update_schedule_type()
        update_preview()

        def to_24_hour(hour_var, minute_var, period_var):
            hour = int(hour_var.get()) % 12
            if period_var.get() == "PM": hour += 12
            return f"{hour:02d}:{minute_var.get()}"

        def save_scheduling():
            work_hours_enabled = work_hours_enabled_var.get()
            schedule_enabled = schedule_enabled_var.get()
            scheduler_help = "Scheduling troubleshooting\n\nTry saving again. If the problem continues, make sure Windows Task Scheduler is available and allowed on this computer.\n\nIf Capture Prompts were disabled but the task could not be removed, you can manually remove it from Windows Task Scheduler.\n\nTask name: GhostNote Capture Prompts"

            store.set_setting("schedule_work_hours_enabled", "true" if work_hours_enabled else "false")
            store.set_setting("schedule_work_days", ",".join(str(day) for day, var in enumerate(day_vars) if var.get()))
            store.set_setting("schedule_work_start", to_24_hour(start_hour, start_minute, start_period))
            store.set_setting("schedule_work_end", to_24_hour(end_hour, end_minute, end_period))
            store.set_setting("schedule_enabled", "true" if schedule_enabled else "false")
            store.set_setting("schedule_type", schedule_type_var.get())
            store.set_setting("schedule_interval_hours", interval_var.get())
            store.set_setting("schedule_specific_hours", ",".join(str(hour) for hour in sorted(specific_hours)))
            store.set_setting("schedule_specific_minute", specific_minute_var.get())

            if not schedule_enabled:
                try:
                    task_scheduler.remove_task()
                    return f"Schedule saved successfully. Windows scheduled task removed: {task_scheduler.TASK_NAME}"
                except Exception:
                    return "Schedule saved, but the Windows task could not be removed. Try saving again.", scheduler_help

            if schedule_type_var.get() == "specific":
                minute = int(specific_minute_var.get())
                times = []

                for hour in sorted(specific_hours):
                    prompt_minutes = hour * 60 + minute

                    if work_hours_enabled:
                        start = (int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)) * 60 + int(start_minute.get())
                        end = (int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)) * 60 + int(end_minute.get())
                        if not start <= prompt_minutes <= end: continue

                    times.append(f"{hour:02d}:{minute:02d}")

            else:
                if work_hours_enabled:
                    start_minutes = (int(start_hour.get()) % 12 + (12 if start_period.get() == "PM" else 0)) * 60 + int(start_minute.get())
                    end_minutes = (int(end_hour.get()) % 12 + (12 if end_period.get() == "PM" else 0)) * 60 + int(end_minute.get())
                else:
                    start_minutes = 0
                    end_minutes = 24 * 60

                interval_minutes = int(interval_var.get()) * 60
                times = []
                current = start_minutes

                while current < end_minutes:
                    hour, minute = divmod(current, 60)
                    times.append(f"{hour:02d}:{minute:02d}")
                    current += interval_minutes

            work_days = [day for day, var in enumerate(day_vars) if var.get()] if work_hours_enabled else None
            try:
                task_scheduler.update_task(times, work_days)
                return f"Schedule saved successfully. Windows scheduled task updated: {task_scheduler.TASK_NAME}"
            except Exception:
                return "Schedule saved, but the Windows task could not be updated. Try saving again.", scheduler_help

        self.page_save_commands["Scheduling"] = save_scheduling
        self.page_restore_keys["Scheduling"] = ["schedule_work_hours_enabled", "schedule_work_days", "schedule_work_start", "schedule_work_end", "schedule_enabled", "schedule_type", "schedule_interval_hours", "schedule_specific_hours", "schedule_specific_minute"]

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