from config import LOG_FILE


def read_GhostNotes():
    """
    Reads the GhostNote markdown log and prints it to the terminal.
    """

    if not LOG_FILE.exists():
        print("No GhostNote log found yet.")
        print(f"Expected location: {LOG_FILE}")
        return

    content = LOG_FILE.read_text(encoding="utf-8")

    if not content.strip():
        print("GhostNote log exists, but it is empty.")
        return

    print(content)


if __name__ == "__main__":
    read_GhostNotes()