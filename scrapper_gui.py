import tkinter as tk
from tkinter import messagebox
import threading
import config
import custom_utils
import main  # Import main scraping script
import log_utils  # Import the logging utility

def start_scraping():
    """Fetch input from the GUI and start the scraping process in a separate thread."""
    status_label.config(text="Validating inputs...", fg="blue")
    log_utils.log_message("[INFO] Validating user inputs...", config.log_text, "blue")

    # Collect session data from input fields
    config.session_data = {
        "csrftoken": csrftoken_entry.get().strip(),
        "sessionid": sessionid_entry.get().strip(),
        "ds_user_id": ds_user_id_entry.get().strip(),
        "mid": mid_entry.get().strip(),
        "ig_did": ig_did_entry.get().strip()
    }
    post_url = post_url_entry.get().strip()

    # Validate inputs
    if not all(config.session_data.values()) or not post_url:
        messagebox.showerror("Error", "All fields are required!")
        log_utils.log_message("[ERROR] Validation failed: Missing required fields.", config.log_text, "red")
        return

    # Extract shortcode
    try:
        shortcode = custom_utils.extract_id(post_url)
        config.post_url = post_url
        config.shortcode = shortcode
        log_utils.log_message(f"[INFO] Extracted shortcode: {shortcode}", config.log_text, "blue")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid URL: {e}")
        log_utils.log_message(f"[ERROR] Failed to extract shortcode: {e}", config.log_text, "red")
        return

    def run_scraper():
        """Run the scraper in a separate thread to avoid UI freezing."""
        try:
            status_label.config(text="Scraping in progress...", fg="blue")
            log_utils.log_message("[INFO] Scraper started...", config.log_text, "green")

            main.main()  # Calls the main function

            status_label.config(text="Scraping completed! Data saved.", fg="green")
            log_utils.log_message("[SUCCESS] Scraping completed successfully.", config.log_text, "green")
        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")
            log_utils.log_message(f"[ERROR] An error occurred: {e}", config.log_text, "red")

    # Start scraping in a new thread
    threading.Thread(target=run_scraper, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Instagram Scraper")
root.geometry("400x700")

# Labels & Input Fields
tk.Label(root, text="Session Data", font=("Arial", 14, "bold")).pack(pady=5)

tk.Label(root, text="csrftoken").pack()
csrftoken_entry = tk.Entry(root, width=50)
csrftoken_entry.pack()

tk.Label(root, text="sessionid").pack()
sessionid_entry = tk.Entry(root, width=50)
sessionid_entry.pack()

tk.Label(root, text="ds_user_id").pack()
ds_user_id_entry = tk.Entry(root, width=50)
ds_user_id_entry.pack()

tk.Label(root, text="mid").pack()
mid_entry = tk.Entry(root, width=50)
mid_entry.pack()

tk.Label(root, text="ig_did").pack()
ig_did_entry = tk.Entry(root, width=50)
ig_did_entry.pack()

tk.Label(root, text="Post/Reel URL").pack()
post_url_entry = tk.Entry(root, width=50)
post_url_entry.pack()

# Submit Button
scrape_button = tk.Button(root, text="Start Scraping", command=start_scraping, bg="blue", fg="white", font=("Arial", 12))
scrape_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=5)

# Logging Text Widget
log_text = tk.Text(root, height=20, width=50, state=tk.DISABLED)
log_text.pack(pady=10)

# Link logging text widget to config
config.log_text = log_text

# Run GUI
root.mainloop()
