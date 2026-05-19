from markdown_store import add_entry
from ui.prompt_window import PromptWindow


def handle_submit(note_text):
    add_entry(note_text)


if __name__ == "__main__":
    app = PromptWindow(handle_submit)
    app.run()