import sys

def log_message(message, log_text_widget=None, color="black"):
    """Logs messages to the console and optionally to a Tkinter Text widget."""
    
    formatted_message = f"[{color.upper()}] {message}"
    print(formatted_message, file=sys.stderr if color == "red" else sys.stdout)

    if log_text_widget:
        log_text_widget.config(state="normal")
        log_text_widget.insert("end", f"{message}\n", color)
        log_text_widget.tag_configure(color, foreground=color)
        log_text_widget.yview("end")
        log_text_widget.config(state="disabled")
