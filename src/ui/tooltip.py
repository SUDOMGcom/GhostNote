import tkinter as tk


class ToolTip:
    def __init__(self, widget, text="", auto_bind=True, duration=4500, position="below"):
        self.widget = widget
        self.text = text
        self.duration = duration
        self.position = position
        self.tooltip = None
        self.after_id = None

        if auto_bind:
            widget.bind("<Enter>", self.show_tooltip)
            widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None, text=None):
        if text is not None:
            self.text = text

        if self.tooltip:
            self.hide_tooltip()

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.attributes("-topmost", True)

        if self.position == "above":
            label = tk.Label(
                self.tooltip,
                text=self.text,
                bg="#2b2b2b",
                fg="white",
                relief="flat",
                bd=0,
                padx=10,
                pady=6,
                font=("Segoe UI", 9),
                wraplength=280,
                justify="left",
            )
        else:
            label = tk.Label(
                self.tooltip,
                text=self.text,
                bg="#222",
                fg="white",
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 9),
                padx=6,
                pady=2,
            )
        label.pack()

        self.tooltip.update_idletasks()

        if self.position == "above":
            x = self.widget.winfo_rootx()
            y = self.widget.winfo_rooty() - self.tooltip.winfo_height() - 4
        else:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2

        self.tooltip.geometry(f"+{x}+{y}")

    def show_for(self, text, duration=None):
        self.show_tooltip(text=text)

        if self.after_id:
            self.widget.after_cancel(self.after_id)

        self.after_id = self.widget.after(duration or self.duration, self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None