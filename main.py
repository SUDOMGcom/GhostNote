import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

from src.app import GhostnoteApp

app = GhostnoteApp()
app.mainloop()