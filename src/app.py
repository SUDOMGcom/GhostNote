import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from pathlib import Path
from screeninfo import get_monitors
import src.config as config
from datetime import datetime
import src.sqlite_store as store
from src.ui.tooltip import ToolTip
from src.ui.settings_window import SettingsWindow

class GhostnoteApp(tk.Tk):
    # Section 1 : App Startup / Window Setup

    def __init__(self):
        super().__init__()

        self.attributes("-alpha", 0.0)
        self.title(f"{config.APP_VENDOR} {config.APP_NAME} v{config.APP_VERSION}")

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
        self.start_date_filter = store.get_latest_entry_date()
        self.end_date_filter = self.start_date_filter
        self.filter_mode = "Latest day"
        self.filter_active = False
        self.search_filter = None
        self.build_header()
        self.build_viewer()
        self.bind_keyboard_shortcuts()
        self.bind("<Configure>", self.close_edit_menu_on_move, add="+")
        self.apply_theme()
        self.after(10, self.fade_in)

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
        else: self.icon = None

    def apply_theme(self):
        theme = config.get_theme()
        self.configure(bg=theme["bg"])

        style = ttk.Style()
        style.theme_use("clam")

        if hasattr(self, "title_frame"): self.title_frame.configure(bg=theme["bg"])
        if hasattr(self, "title_canvas"): self.title_canvas.configure(bg=theme["bg"])
        if hasattr(self, "sudomg_label"): self.sudomg_label.configure(bg=theme["bg"], fg=theme["muted"])

        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["text"])
        style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"], padding=(10, 6), borderwidth=0)
        style.map("TButton", background=[("active", theme["button_hover"]), ("pressed", theme["button_pressed"]), ("disabled", theme["button_disabled"])], foreground=[("active", theme["button_fg"]), ("pressed", theme["button_fg"]), ("disabled", theme["button_disabled_fg"])])
        style.configure("TRadiobutton", background=theme["bg"], foreground=theme["text"])
        style.map("TRadiobutton", background=[("active", theme["bg"])], foreground=[("active", theme["text"])])
        style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"])
        style.map("TEntry", fieldbackground=[("!disabled", theme["entry_bg"])])
        style.configure("TCombobox", fieldbackground=theme["entry_bg"], background=theme["panel"], foreground=theme["entry_fg"], arrowcolor=theme["text"], bordercolor=theme["border"], lightcolor=theme["border"], darkcolor=theme["border"])
        self.option_add("*TCombobox*Listbox.background", theme["entry_bg"]); self.option_add("*TCombobox*Listbox.foreground", theme["entry_fg"]); self.option_add("*TCombobox*Listbox.selectBackground", theme["button_hover"]); self.option_add("*TCombobox*Listbox.selectForeground", theme["button_fg"])
        style.map("TCombobox", fieldbackground=[("readonly", theme["entry_bg"]), ("focus", theme["entry_bg"]), ("active", theme["entry_bg"]), ("!disabled", theme["entry_bg"])], foreground=[("readonly", theme["entry_fg"]), ("focus", theme["entry_fg"]), ("active", theme["entry_fg"]), ("!disabled", theme["entry_fg"])], selectbackground=[("readonly", theme["entry_bg"]), ("focus", theme["entry_bg"]), ("active", theme["entry_bg"])], selectforeground=[("readonly", theme["entry_fg"]), ("focus", theme["entry_fg"]), ("active", theme["entry_fg"])])
        style.configure("TSpinbox", fieldbackground=theme["entry_bg"], background=theme["panel"], foreground=theme["entry_fg"], arrowcolor=theme["text"], bordercolor=theme["border"], lightcolor=theme["border"], darkcolor=theme["border"])
        style.map("TSpinbox", fieldbackground=[("readonly", theme["entry_bg"]), ("focus", theme["entry_bg"]), ("active", theme["entry_bg"]), ("!disabled", theme["entry_bg"])], foreground=[("readonly", theme["entry_fg"]), ("focus", theme["entry_fg"]), ("active", theme["entry_fg"]), ("!disabled", theme["entry_fg"])])
        style.configure("Vertical.TScrollbar", background=theme["panel"], troughcolor=theme["bg"], arrowcolor=theme["text"])
        style.map("Vertical.TScrollbar", background=[("active", theme["entry_bg"])])
        style.configure("Active.TButton", background=theme["button_bg"], foreground=theme["active_filter_fg"], padding=(10, 6), borderwidth=0)
        style.map("Active.TButton", background=[("active", theme["button_hover"]), ("pressed", theme["button_pressed"])], foreground=[("active", theme["active_filter_fg"]), ("pressed", theme["active_filter_fg"])])
        style.configure("Treeview", font=("Segoe UI", 12), rowheight=36, background=theme["panel"], fieldbackground=theme["panel"], foreground=theme["text"], borderwidth=0, relief="flat")
        style.map("Treeview", background=[("selected", theme["button_hover"])], foreground=[("selected", theme["button_fg"])])
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background=theme["bg"], foreground=theme["text"], borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("active", theme["bg"])], foreground=[("active", theme["text"])])

    def fade_in(self, alpha=0.0):
        alpha += 0.05

        if alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            return

        self.attributes("-alpha", alpha)
        self.after(12, lambda: self.fade_in(alpha))

    def bind_keyboard_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.open_add_ghostnote_menu(self.addGN_button))
        self.bind("<Control-f>", lambda event: self.open_search_menu(self.search_button))
        self.bind("<Control-e>", lambda event: self.open_edit_ghostnote_menu())
        self.entry_table.bind("<Control-c>", lambda event: self.copy_selected_entry_note())
        self.bind("<Control-r>", lambda event: self.load_entries())
        self.bind("<F5>", lambda event: self.load_entries())

    # Section 2 : Main UI Builders

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

        self.sudomg_label = tk.Label(text_frame, text=f"{config.APP_VENDOR}", font=("Segoe UI", 7, "bold"), bg=theme["bg"], fg=theme["muted"])
        self.sudomg_label.pack(anchor="w")
        self.title_frame = tk.Frame(text_frame, bg=theme["bg"])
        self.title_frame.pack(anchor="w", pady=(0, 0))

        self.title_canvas = tk.Canvas(self.title_frame, bg=theme["bg"], highlightthickness=0, bd=0, width=185, height=28)
        self.title_canvas.pack(anchor="w")

        font = ("Segoe UI", 22, "bold")
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 0), (1, 1)]:
            self.title_canvas.create_text(0 + dx, 12 + dy, text="Ghost", font=font, fill=theme["title_outline"], anchor="w")
            self.title_canvas.create_text(80 + dx, 12 + dy, text="Note", font=font, fill=theme["title_outline"], anchor="w")

        self.title_canvas.create_text(0, 12, text="Ghost", font=font, fill=theme["title_ghost"], anchor="w")
        self.title_canvas.create_text(80, 12, text="Note", font=font, fill=theme["title_note"], anchor="w")
        ttk.Label(text_frame, text="Helping track your hidden work", font=("Segoe UI", 9)).pack(anchor="w")

        # Right button area
        button_frame = ttk.Frame(header)
        button_frame.pack(side=tk.RIGHT)

        #settings button
        settings_frame = ttk.Frame(button_frame, width=100, height=34)
        settings_frame.pack_propagate(False)
        settings_frame.pack(side=tk.LEFT, padx=4)
        settings_button = ttk.Button(settings_frame, text="⚙ Settings", padding=0, command=lambda: SettingsWindow(self, start_page="General"))
        settings_button.pack(fill=tk.BOTH, expand=True)
        ToolTip(settings_button, "Settings")

    def build_viewer(self):
        container = ttk.Frame(self, padding=(16, 4, 12, 12))
        container.pack(fill=tk.BOTH, expand=True)

        button_column = ttk.Frame(container)
        button_column.pack(side=tk.LEFT, anchor="sw", padx=(0, 16),  fill=tk.Y)

        #Left pane buttons
        self.addGN_button = self.icon_button(button_column, "✚", lambda: self.open_add_ghostnote_menu(self.addGN_button), "Add GhostNote")
        self.editGN_button = self.icon_button(button_column, "✎", self.open_edit_ghostnote_menu, "Edit Selected GhostNote"); self.editGN_button.config(state="disabled")
        export_button = self.icon_button(button_column, "💾", lambda: self.open_export_menu(export_button), "Export")
        #ttk.Frame(button_column).pack(expand=True) #big gap, expanding the space - keeping code for later
        ttk.Label(button_column, text="────", width=3, anchor="center").pack(pady=(0, 8))
        self.search_button = self.icon_button(button_column, "🔍", lambda: self.open_search_menu(self.search_button), "Search")
        self.filter_button = self.icon_button(button_column, "☰", lambda: self.open_filter_menu(self.filter_button), "Filter")
        refresh_button = self.icon_button(button_column, "🗘", self.load_entries, "Refresh")
        ttk.Label(button_column, text="────", width=3, anchor="center").pack(pady=(0, 8))
        analyze_button = self.icon_button(button_column, "✨", self.open_ai_modal, "Analyze")

        #viewer
        self.entry_table = ttk.Treeview(container, columns=("time", "content"), show="tree headings")
        self.entry_table.heading("#0", text="Date", anchor="w")
        self.entry_table.heading("time", text="Time", anchor="e")
        self.entry_table.heading("content", text="Entry", anchor="w")
        self.entry_table.column("#0", width=115, minwidth=115, anchor="w", stretch=False)
        self.entry_table.column("time", width=85, minwidth=85, anchor="e", stretch=False)
        self.entry_table.column("content", anchor="w", stretch=True)
        self.entry_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.entry_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_table.configure(yscrollcommand=scrollbar.set)
        self.entry_table.bind("<<TreeviewSelect>>", self.on_entry_selected)
        self.entry_table.bind("<Button-1>", self.on_entry_left_click, add="+")
        self.entry_table.bind("<Button-3>", self.on_entry_right_click)

        self.load_entries()

    # Section 3 : Shared small helpers

    def format_date(self, created_at):
        return datetime.fromisoformat(created_at).strftime("%Y-%m-%d")

    def format_time(self, created_at):
        return datetime.fromisoformat(created_at).strftime("%I:%M %p").lstrip("0")

    def select_segment(self, event, widget, separators="-: "):
        text = widget.get()
        index = widget.index(f"@{event.x}")

        if not text: return

        start = index
        while start > 0 and text[start - 1] not in separators: start -= 1

        end = index
        while end < len(text) and text[end] not in separators: end += 1

        widget.selection_range(start, end)
        return "break"

    def update_filter_button_states(self):
        if hasattr(self, "search_button"): self.search_button.configure(style="Active.TButton" if self.search_filter else "TButton")
        if hasattr(self, "filter_button"): self.filter_button.configure(style="Active.TButton" if self.filter_active else "TButton")

    def is_entry_row(self, item_id):
        return item_id and self.entry_table.parent(item_id)

    def deselect_entries(self):
        self.entry_table.selection_remove(*self.entry_table.selection())
        self.entry_table.focus("")
        self.editGN_button.config(state="disabled")

    def center_modal(self, modal, width, height):
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        modal.geometry(f"{width}x{height}+{x}+{y}")

    def icon_button(self, parent, text, command, tooltip, size=34):
        frame = ttk.Frame(parent, width=size, height=size)
        frame.pack_propagate(False)
        frame.pack(pady=(0, 8))

        button = ttk.Button(frame, text=text, command=command)
        button.pack(fill=tk.BOTH, expand=True)

        ToolTip(button, tooltip)
        return button

    # Section 4 : Viewer data + Selection behavior

    def load_entries(self):
        from datetime import timedelta

        if self.filter_mode == "Latest day":
            latest = store.get_latest_entry_date()
            self.start_date_filter = latest
            self.end_date_filter = latest
            self.filter_active = False

        elif self.filter_mode == "Last 7 days":
            today = datetime.now().date()
            self.start_date_filter = (today - timedelta(days=6)).isoformat()
            self.end_date_filter = today.isoformat()
            self.filter_active = True

        elif self.filter_mode == "Last 30 days":
            today = datetime.now().date()
            self.start_date_filter = (today - timedelta(days=29)).isoformat()
            self.end_date_filter = today.isoformat()
            self.filter_active = True

        self.entry_table.delete(*self.entry_table.get_children())
        self.update_filter_button_states()

        current_date = None
        current_parent = None
        first_group = True

        for entry in store.get_entries(self.start_date_filter, self.end_date_filter, self.search_filter):
            entry_date = self.format_date(entry["created_at"])

            if entry_date != current_date:
                current_date = entry_date
                current_parent = self.entry_table.insert("", "end", text=entry_date, values=("", ""), open=first_group)
                first_group = False

            tags = (entry["tags"][:27] + "…") if entry["tags"] and len(entry["tags"]) > 28 else (entry["tags"] or "")
            content = f"[{tags}] {entry['content']}" if tags else entry["content"]
            self.entry_table.insert(current_parent, "end", iid=entry["id"], text="", values=(self.format_time(entry["created_at"]), content))

    def truncate_text(self, value, limit=28):
        if not value:
            return ""
        return value if len(value) <= limit else value[:limit - 1] + "…"

    def on_entry_selected(self, event=None):
        selected = self.entry_table.selection()

        if not selected:
            self.editGN_button.config(state="disabled")
            return

        item_id = selected[0]
        parent_id = self.entry_table.parent(item_id)

        if not parent_id:
            self.editGN_button.config(state="disabled")
            return

        self.editGN_button.config(state="normal")

    def on_entry_left_click(self, event):
        row_id = self.entry_table.identify_row(event.y)
        if not self.is_entry_row(row_id): self.deselect_entries()

    def on_entry_right_click(self, event):
        row_id = self.entry_table.identify_row(event.y)

        if not self.is_entry_row(row_id):
            self.deselect_entries()
            return "break"

        self.entry_table.selection_set(row_id)
        self.entry_table.focus(row_id)
        self.editGN_button.config(state="normal")

        self.open_entry_context_menu(event)
        return "break"

    # Section 5 : Right-Click Menu

    def open_entry_context_menu(self, event):
        theme = config.get_theme()
        menu = tk.Menu(self, tearoff=0, bg=theme["panel"], fg=theme["text"], activebackground=theme["button_hover"], activeforeground=theme["button_fg"], borderwidth=0)
        menu.add_command(label="Copy", command=self.copy_selected_entry_note)
        menu.add_command(label="Edit", command=self.open_edit_ghostnote_menu)
        menu.add_command(label="New", command=lambda: self.open_add_ghostnote_menu(self.addGN_button))

        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def copy_selected_entry_note(self):
        selected = self.entry_table.selection()
        if not selected: return

        item_id = selected[0]
        if not self.is_entry_row(item_id): return

        entry = store.get_entry(int(item_id))
        note_text = entry["content"]

        self.clipboard_clear()
        self.clipboard_append(note_text)
        self.update()

    # Section 6 : Left-side button features (in button order)

    def open_add_ghostnote_menu(self, button):
        if getattr(self, "add_ghostnote_popup", None) and self.add_ghostnote_popup.winfo_exists(): self.add_ghostnote_popup.destroy()

        popup = self.add_ghostnote_popup = tk.Toplevel(self); popup.withdraw(); popup.overrideredirect(True)
        theme = config.get_theme(); now = datetime.now(); popup.configure(bg=theme["bg"])
        categories_enabled = store.get_setting("popup_categories_enabled", "false") == "true"
        popup_categories = [c.strip() for c in store.get_setting("popup_categories", "").split(",") if c.strip()] if categories_enabled else []

        category_var = tk.StringVar(value=popup_categories[0] if popup_categories else "")
        date_var = tk.StringVar(value=now.strftime("%Y-%m-%d")); time_var = tk.StringVar(value=now.strftime("%I:%M %p"))
        border = tk.Frame(popup, bg="#d0d0d0")
        border.pack(fill="both", expand=True)

        form = ttk.Frame(border, padding=(8, 8, 8, 8))
        form.pack(fill="both", expand=True, padx=3, pady=3)

        placeholder = store.get_setting("popup_prompt", "What are you working on?")
        note_var = tk.StringVar(value=placeholder)
        placeholder_active = True

        ttk.Label(form, text="Date").grid(row=0, column=0, sticky="w", padx=(0, 4)); date_entry = DateEntry(form, textvariable=date_var, date_pattern="yyyy-mm-dd", firstweekday="sunday"); date_entry.grid(row=0, column=1, sticky="w", padx=(0, 8))
        ttk.Label(form, text="Time").grid(row=0, column=2, sticky="w", padx=(0, 4)); time_options = [f"{h}:{m:02d} {ampm}" for ampm in ("AM", "PM") for h in range(1, 13) for m in range(0, 60, 5)]; time_entry = ttk.Spinbox(form, textvariable=time_var, values=time_options, width=10, style="TSpinbox"); time_entry.grid(row=0, column=3, sticky="w", padx=(0, 8)); time_entry.bind("<FocusIn>", lambda e: time_entry.selection_range(0, tk.END))

        if popup_categories:
            ttk.Label(form, text="Category").grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(8, 0))
            ttk.Combobox(form, textvariable=category_var, values=popup_categories, state="readonly", width=18).grid(row=1, column=1, columnspan=3, sticky="w", pady=(8, 0))
            note_row = 2
        else: note_row = 1

        note_entry = tk.Entry(form, textvariable=note_var, width=46, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"], highlightthickness=2, highlightbackground="#ffffff", highlightcolor="#4a90e2", relief="solid", borderwidth=1)
        note_entry.grid(row=note_row, column=0, columnspan=4, sticky="ew", pady=(8, 0))

        def clear_placeholder(event=None):
            nonlocal placeholder_active
            if placeholder_active:
                note_var.set("")
                note_entry.configure(fg=theme["entry_fg"])
                placeholder_active = False

        def force_field_focus(widget):
            widget.focus_force()
            widget.icursor(tk.END)

        note_entry.bind("<Button-1>", clear_placeholder)
        note_entry.bind("<KeyPress>", clear_placeholder)
        time_entry.bind("<ButtonRelease-1>", lambda e: self.select_segment(e, time_entry, ": "))
        date_entry.bind("<ButtonRelease-1>", lambda e: self.select_segment(e, date_entry, "-"))
        #date_entry.bind("<Button-1>", lambda e: force_field_focus(date_entry))
        time_entry.bind("<Button-1>", lambda e: force_field_focus(time_entry))
        note_entry.bind("<Button-1>", lambda e: force_field_focus(note_entry))

        def close_popup(event=None):
            if getattr(self, "add_ghostnote_popup", None) is popup: self.add_ghostnote_popup = None
            if popup.winfo_exists(): popup.destroy()

        def save_note(event=None):
            note_text = note_var.get().strip()
            if placeholder_active or not note_text: return
            try: created_at = datetime.strptime(f"{date_var.get().strip()} {time_var.get().strip().upper()}", "%Y-%m-%d %I:%M %p")
            except ValueError: messagebox.showerror("Invalid time", "Use a valid time like 2:45 PM."); time_entry.focus_force(); time_entry.selection_range(0, tk.END); return
            store.add_entry(note_text, source="Manual", created_at=created_at.isoformat(timespec="seconds"), tags=category_var.get())
            self.load_entries();
            close_popup()

        ttk.Button(form, text="Save", command=save_note).grid(row=note_row + 1, column=0, columnspan=4, pady=(8, 0))
        x = button.winfo_rootx() + button.winfo_width(); y = button.winfo_rooty()

        def close_if_focus_left(event=None):
            def check():
                if not popup.winfo_exists(): return

                try: focused = popup.focus_get()
                except KeyError: return

                while focused:
                    if focused == popup: return
                    focused = focused.master

                close_popup()

            popup.after(50, check)
        popup.geometry(f"+{x}+{y}")
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.bind("<Escape>", close_popup)
        popup.bind("<Return>", save_note)
        popup.bind("<FocusOut>", close_if_focus_left)
        popup.after(100, lambda: force_field_focus(note_entry))

    def open_edit_ghostnote_menu(self):
        self.close_edit_menu()

        selected = self.entry_table.selection()
        if not selected: return

        item_id = selected[0]
        entry_id = int(item_id)
        entry = store.get_entry(entry_id)
        current_tag = entry["tags"] or ""
        parent_id = self.entry_table.parent(item_id)
        self.edit_ghostnote_item_id = item_id

        if not parent_id: return

        date_text = self.entry_table.item(parent_id, "text")
        values = self.entry_table.item(item_id, "values")

        time_text = values[0]
        content_text = entry["content"]
        theme = config.get_theme()

        popup = self.edit_ghostnote_popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.transient(self)
        popup.configure(bg=theme["bg"])
        popup.attributes("-toolwindow", True)
        popup.attributes("-topmost", True)

        popup.date_var = tk.StringVar(value=date_text)
        popup.time_var = tk.StringVar(value=time_text)
        popup.note_var = tk.StringVar(value=content_text)
        popup.category_var = tk.StringVar(value=current_tag)

        categories_enabled = store.get_setting("popup_categories_enabled", "false") == "true"

        popup_categories = [
            c.strip()
            for c in store.get_setting("popup_categories", "").split(",")
            if c.strip()
        ] if categories_enabled else []

        if current_tag and current_tag not in popup_categories:
            popup_categories.append(current_tag)

        border = tk.Frame(popup, bg="#d0d0d0")
        border.pack(fill="both", expand=True)

        form = ttk.Frame(border, padding=(8, 8, 8, 8))
        form.pack(fill="both", expand=True, padx=3, pady=3)

        ttk.Label(form, text="Date").grid(row=0, column=0, sticky="w", padx=(0, 4))
        date_entry = ttk.Entry(form, textvariable=popup.date_var, width=12, cursor="xterm")
        date_entry.grid(row=0, column=1, sticky="w", padx=(0, 8))

        ttk.Label(form, text="Time").grid(row=0, column=2, sticky="w", padx=(0, 4))
        time_entry = ttk.Entry(form, textvariable=popup.time_var, width=10, cursor="xterm")
        time_entry.grid(row=0, column=3, sticky="w", padx=(0, 8))

        if categories_enabled:
            ttk.Label(form, text="Category").grid(row=0, column=4, sticky="w", padx=(0, 4))
            if popup_categories: category_entry = ttk.Combobox(form, textvariable=popup.category_var, values=popup_categories, state="readonly", width=18, style="TCombobox"); category_entry.bind( "<<ComboboxSelected>>", lambda e: e.widget.selection_clear())
            else: category_entry = ttk.Entry(form, textvariable=popup.category_var, width=18)
            category_entry.grid(row=0, column=5, sticky="w")

        ttk.Label(form, text="Note").grid(row=1, column=0, sticky="w", pady=(8, 0))
        note_entry = tk.Entry(form, textvariable=popup.note_var, width=45, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"], highlightthickness=2, highlightbackground="#ffffff", highlightcolor="#4a90e2", relief="solid", borderwidth=1)
        note_entry.grid(row=1, column=1, columnspan=5, sticky="ew", padx=(0, 8), pady=(8, 0))
        note_entry.icursor(tk.END)

        button_frame = ttk.Frame(form)
        button_frame.grid(row=2, column=0, columnspan=6, sticky="e", pady=(8, 0))

        save_button = ttk.Button(button_frame, text="Save", command=lambda: self.save_edited_ghostnote(entry_id, popup))
        save_button.pack(side=tk.LEFT, padx=(4, 0))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=lambda: self.close_edit_menu())
        cancel_button.pack(side=tk.LEFT, padx=(4, 0))

        delete_button = ttk.Button(button_frame, text="Delete", width=12)
        delete_button.pack(side=tk.LEFT, padx=(4, 0))

        def prompt_delete():
            save_button.pack_forget()

            cancel_button.config(text="Cancel", command=reset_delete_prompt)
            delete_button.config(text="Delete", command=delete_ghostnote)

            confirm_label.pack(side=tk.LEFT, padx=(4, 0))

        def delete_ghostnote():
            store.delete_entry(entry_id)
            self.close_edit_menu()
            self.entry_table.selection_remove(*self.entry_table.selection())
            self.editGN_button.config(state="disabled")
            self.load_entries()

        def reset_delete_prompt():
            confirm_label.pack_forget()

            if not save_button.winfo_ismapped():
                save_button.pack(side=tk.LEFT, padx=(4, 0), before=cancel_button)

            cancel_button.config(text="Cancel", command=self.close_edit_menu)
            delete_button.config(text="Delete", command=prompt_delete)

        confirm_label = ttk.Label(button_frame, text="<- Confirm?", width=14, anchor="center")
        delete_button.config(command=prompt_delete)

        date_entry.bind("<ButtonRelease-1>", lambda e: self.select_segment(e, date_entry, "-"))
        time_entry.bind("<ButtonRelease-1>", lambda e: self.select_segment(e, time_entry, ": "))

        self.position_edit_menu()
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.bind("<Escape>", lambda event: self.close_edit_menu())

        popup.after(100, lambda: (note_entry.focus_force(), note_entry.icursor(tk.END)))

    def save_edited_ghostnote(self, entry_id, popup):
        try: created_at = datetime.strptime(f"{popup.date_var.get().strip()} {popup.time_var.get().strip().upper()}","%Y-%m-%d %I:%M %p")
        except ValueError:
            messagebox.showerror("Invalid time", "Use a valid time like 2:45 PM.")
            return

        note_text = popup.note_var.get().strip()
        if not note_text: return

        store.update_entry(entry_id, note_text, created_at.isoformat(timespec="seconds"), popup.category_var.get().strip() or None)
        self.close_edit_menu()
        self.entry_table.selection_remove(*self.entry_table.selection())
        self.editGN_button.config(state="disabled")
        self.load_entries()

    def open_export_menu(self, button):
        theme = config.get_theme()
        menu = tk.Menu(self, tearoff=0, bg=theme["panel"], fg=theme["text"], activebackground=theme["button_hover"], activeforeground=theme["button_fg"], borderwidth=0)
        menu.add_command(label="Export as CSV...", command=lambda: self.export_as("csv"))
        menu.add_command(label="Export as Markdown...", command=lambda: self.export_as("markdown"))

        #dropdown opens from left side
        x = button.winfo_rootx() + button.winfo_width()
        y = button.winfo_rooty()
        menu.tk_popup(x, y)

    def export_as(self, export_type):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        visible_entries = []

        for parent in self.entry_table.get_children():
            date = self.entry_table.item(parent, "text")

            for child in self.entry_table.get_children(parent):
                values = self.entry_table.item(child, "values")

                visible_entries.append({
                    "date": date,
                    "time": values[0],
                    "content": values[1]
                })

        if export_type == "csv":
            import csv
            from tkinter import filedialog

            file_path = filedialog.asksaveasfilename(initialfile=f"GhostNote_Export_{timestamp}.csv", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if not file_path: return

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["date", "time", "content"])
                writer.writeheader()
                writer.writerows(visible_entries)

        elif export_type == "markdown":
            from tkinter import filedialog

            file_path = filedialog.asksaveasfilename(initialfile=f"GhostNote_Export_{timestamp}.md", defaultextension=".md", filetypes=[("Markdown Files", "*.md")])
            if not file_path: return

            grouped = {}
            for entry in visible_entries:
                grouped.setdefault(entry["date"], []).append(entry)

            lines = []
            for date, entries in grouped.items():
                lines.append(f"# {date}")
                lines.append("")

                for entry in entries:
                    lines.append(f"- {entry['time']}:\t{entry['content']}")

                lines.append("")

            markdown_content = "\n".join(lines)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(markdown_content)

    def open_search_menu(self, button):
        if getattr(self, "search_popup", None) and self.search_popup.winfo_exists(): self.search_popup.destroy()

        popup = self.search_popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        theme = config.get_theme()
        popup.configure(bg=theme["bg"])

        placeholder = "Search notes, tags, or source..."
        search_var = tk.StringVar(value=self.search_filter or placeholder)
        placeholder_active = True

        border = tk.Frame(popup, bg="#d0d0d0")
        border.pack(fill="both", expand=True)

        content = ttk.Frame(border, padding=(8, 8, 8, 8))
        content.pack(fill="both", expand=True, padx=3, pady=3)
        entry = ttk.Entry(content, textvariable=search_var, width=32);
        entry.pack(fill="x")

        def clear_placeholder(event=None):
            nonlocal placeholder_active
            if placeholder_active:
                search_var.set("")
                entry.configure(style="TEntry")
                placeholder_active = False

        entry.bind("<Button-1>", clear_placeholder)
        entry.bind("<KeyPress>", clear_placeholder)

        def close_popup(event=None):
            if getattr(self, "search_popup", None) is popup: self.search_popup = None
            if popup.winfo_exists(): popup.destroy()

        def close_if_focus_left(event=None):
            def check():
                if not popup.winfo_exists(): return

                try: focused = popup.focus_get()
                except KeyError: return

                while focused:
                    if focused == popup: return
                    focused = focused.master
                close_popup()
            popup.after(50, check)

        def apply_search(event=None):
            text = search_var.get().strip()
            self.search_filter = None if text == placeholder or not text else text
            self.load_entries()
            close_popup()

        def clear_search():
            self.search_filter = None
            self.load_entries()
            close_popup()

        button_frame = ttk.Frame(content)
        button_frame.pack(pady=(8, 0))
        ttk.Button(button_frame, text="Search", command=apply_search).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Clear", command=clear_search).pack(side="left", padx=4)

        popup.geometry(f"+{button.winfo_rootx() + button.winfo_width()}+{button.winfo_rooty()}")
        popup.deiconify(); popup.lift()
        popup.after(100, entry.focus_force)
        popup.bind("<Escape>", close_popup)
        popup.bind("<FocusOut>", close_if_focus_left)
        entry.bind("<Return>", apply_search)

    def open_filter_menu(self, button):
        theme = config.get_theme()
        menu = tk.Menu(self, tearoff=0, bg=theme["panel"], fg=theme["text"], activebackground=theme["button_hover"], activeforeground=theme["button_fg"], borderwidth=0)
        for label in ["Latest day", "Last 7 days", "Last 30 days", "Custom dates..."]:
            menu.add_command(label=("✓ " if self.filter_mode == label else "   ") + label, command=lambda value=label: self.apply_filter_mode(value))

        # dropdown opens from the left
        x = button.winfo_rootx() + button.winfo_width()
        y = button.winfo_rooty()
        menu.tk_popup(x, y)

    def apply_filter_mode(self, mode):
        from datetime import timedelta
        self.filter_mode = mode
        if mode == "Latest day":
            latest = store.get_latest_entry_date()
            self.start_date_filter = latest
            self.end_date_filter = latest
            self.filter_active = False
            self.load_entries()
        elif mode == "Last 7 days":
            today = datetime.now().date()
            self.start_date_filter = (today - timedelta(days=6)).isoformat()
            self.end_date_filter = today.isoformat()
            self.filter_active = True
            self.load_entries()
        elif mode == "Last 30 days":
            today = datetime.now().date()
            self.start_date_filter = (today - timedelta(days=29)).isoformat()
            self.end_date_filter = today.isoformat()
            self.filter_active = True
            self.load_entries()
        elif mode == "Custom dates...":
            self.open_filter_modal()

    def open_filter_modal(self):
        modal = tk.Toplevel(self)
        modal.withdraw()
        theme = config.get_theme()
        modal.configure(bg=theme["bg"])
        modal.title(f"{config.APP_VENDOR} {config.APP_NAME} v{config.APP_VERSION} - Filter GhostNote")
        modal_width, modal_height = 420, 175
        modal.iconbitmap(self.window_icon_path)
        self.center_modal(modal, modal_width, modal_height)

        modal.transient(self)
        modal.grab_set()
        start_var, end_var = tk.StringVar(value=self.start_date_filter or ""), tk.StringVar(value=self.end_date_filter or "")
        ttk.Label(modal, text="Filter GhostNote", font=("Segoe UI", 16, "bold")).pack(pady=(14, 8))
        form = ttk.Frame(modal, padding=(16, 0, 16, 16))
        form.pack(anchor="center")
        ttk.Label(form, text="Start Date").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        start_entry = DateEntry(form, textvariable=start_var, date_pattern="yyyy-mm-dd", firstweekday="sunday")
        start_entry.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(form, text="End Date").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=4)
        end_entry = DateEntry(form, textvariable=end_var, date_pattern="yyyy-mm-dd", firstweekday="sunday")
        end_entry.grid(row=0, column=3, sticky="w", pady=4)

        def apply_filter():
            self.start_date_filter = start_var.get().strip() or None
            self.end_date_filter = end_var.get().strip() or None
            self.filter_active = True
            self.filter_mode = "Custom dates..."
            self.load_entries()
            modal.destroy()

        def clear_filter():
            self.apply_filter_mode("Latest day")
            modal.destroy()

        button_frame = ttk.Frame(modal);
        button_frame.pack(pady=(4, 14))
        ttk.Button(button_frame, text="Apply", command=apply_filter).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Clear", command=clear_filter).pack(side=tk.LEFT, padx=4)
        modal.bind("<Escape>", lambda event: modal.destroy())
        modal.deiconify()
        start_entry.focus_force()

    def open_ai_modal(self):
        modal = tk.Toplevel(self);
        modal.withdraw()
        theme = config.get_theme()
        modal.configure(bg=theme["bg"])
        modal.title(f"{config.APP_VENDOR} {config.APP_NAME} v{config.APP_VERSION} - Ai Analyze")
        modal_width = 400
        modal_height = 300
        modal.iconbitmap(self.window_icon_path)
        self.center_modal(modal, modal_width, modal_height)

        modal.transient(self)
        modal.grab_set()

        ai_frame = ttk.Frame(modal, padding=12)
        ai_frame.columnconfigure(1, weight=1)
        ai_frame.pack(fill=tk.BOTH, expand=True)
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "teasers" / "AiSettings.png"
        if icon_path.exists():
            image = Image.open(icon_path)
            image = image.resize((360, 270), Image.LANCZOS)
            self.ai_modal_icon = ImageTk.PhotoImage(image)
            image_label = tk.Label(modal, image=self.ai_modal_icon, bg=theme["bg"], bd=0, highlightthickness=0)
            image_label.pack(expand=True, pady=(0, 0))

        title = ttk.Label(modal, text="AI Analyze", font=("Segoe UI", 16, "bold"))
        title.place(relx=.5, y=20, anchor="n")

        coming = ttk.Label(modal, text="Coming Soon!")
        coming.place(relx=.5, y=55, anchor="n")

        ttk.Button(modal, text="Close", command=modal.destroy).place(relx=.5, rely=.95, anchor="s")

        modal.deiconify()

    # Section 7 : Edit popup helpers

    def position_edit_menu(self):
        popup = getattr(self, "edit_ghostnote_popup", None)
        item_id = getattr(self, "edit_ghostnote_item_id", None)

        if not popup or not popup.winfo_exists() or not item_id: return

        bbox = self.entry_table.bbox(item_id)
        if not bbox: return

        x = self.entry_table.winfo_rootx()
        y = self.entry_table.winfo_rooty() + bbox[1] + bbox[3]

        popup.geometry(f"+{x}+{y}")

    def close_edit_menu_on_move(self, event=None):
        if event and event.widget != self: return
        if not getattr(self, "edit_ghostnote_popup", None): return
        self.close_edit_menu()

    def close_edit_menu(self, popup_to_close=None):
        popup = getattr(self, "edit_ghostnote_popup", None)

        if popup_to_close is not None and popup_to_close != popup:
            if popup_to_close.winfo_exists(): popup_to_close.destroy()
            return

        if popup and popup.winfo_exists():
            try: popup.attributes("-topmost", False)
            except tk.TclError: pass

            try: popup.grab_release()
            except tk.TclError: pass

            popup.destroy()

        self.edit_ghostnote_popup = None
        self.edit_ghostnote_item_id = None
        self.focus_force()

if __name__ == "__main__":
    app = GhostnoteApp()
    app.mainloop()
