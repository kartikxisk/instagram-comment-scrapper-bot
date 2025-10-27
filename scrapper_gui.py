import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import csv
import json
import os
import tempfile
from datetime import datetime
import config
import custom_utils
import main
import log_utils


class InstagramScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Scraper Pro")
        self.root.geometry("650x800")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        # Threading control
        self.is_scraping = False
        self.stop_event = threading.Event()
        self.stop_requested = False

        # Session data file path
        temp_dir = tempfile.gettempdir()
        self.session_file = os.path.join(
            temp_dir, "instagram_scraper_session.json")

        print(f"Session file location: {self.session_file}")

        self.load_session()
        self.create_ui()

    def create_ui(self):
        """Create modern UI with better layout"""

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Instagram Scraper",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=15)

        # Session Data Section
        session_frame = tk.LabelFrame(
            main_frame,
            text="Session Data",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=12,
            pady=12
        )
        session_frame.pack(fill=tk.X, pady=(0, 12))

        csv_button_frame = tk.Frame(session_frame, bg="#ffffff")
        csv_button_frame.pack(fill=tk.X, pady=(0, 10))

        btn_width = 16

        self.import_btn = tk.Button(
            csv_button_frame,
            text="📁 Import CSV",
            command=self.import_from_csv,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            width=btn_width,
            pady=6,
            cursor="hand2"
        )
        self.import_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_btn = tk.Button(
            csv_button_frame,
            text="💾 Save Session",
            command=self.save_session,
            bg="#27ae60",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            width=btn_width,
            pady=6,
            cursor="hand2"
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(
            csv_button_frame,
            text="🗑️ Clear Session",
            command=self.clear_session,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.FLAT,
            width=btn_width,
            pady=6,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Input fields
        self.entries = {}
        fields = ["csrftoken", "sessionid", "ds_user_id", "mid", "ig_did"]

        for field in fields:
            field_frame = tk.Frame(session_frame, bg="#ffffff")
            field_frame.pack(fill=tk.X, pady=4)

            tk.Label(
                field_frame,
                text=field,
                font=("Arial", 9),
                bg="#ffffff",
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT, padx=(0, 5))

            entry = tk.Entry(
                field_frame,
                font=("Arial", 9),
                relief=tk.FLAT,
                bg="#ecf0f1",
                highlightthickness=1,
                highlightbackground="#bdc3c7",
                highlightcolor="#3498db"
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            self.entries[field] = entry

        # Post URL Section
        url_frame = tk.LabelFrame(
            main_frame,
            text="Post/Reel URL",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=12,
            pady=12
        )
        url_frame.pack(fill=tk.X, pady=(0, 12))

        self.post_url_entry = tk.Entry(
            url_frame,
            font=("Arial", 9),
            relief=tk.FLAT,
            bg="#ecf0f1",
            highlightthickness=1,
            highlightbackground="#bdc3c7",
            highlightcolor="#3498db"
        )
        self.post_url_entry.pack(fill=tk.X, ipady=6)

        # Control Buttons
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Scraping",
            command=self.start_scraping,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            pady=10,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, expand=True,
                               fill=tk.X, padx=(0, 5))

        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop Scraping",
            command=self.stop_scraping,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, expand=True,
                              fill=tk.X, padx=(5, 0))

        # Status Label
        self.status_label = tk.Label(
            main_frame,
            text="Ready to scrape",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=(5, 10))

        # Logging Section
        log_frame = tk.LabelFrame(
            main_frame,
            text="Activity Log",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=8,
            pady=8
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_container = tk.Frame(log_frame, bg="#ffffff")
        log_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            log_container,
            height=20,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#f9fafb",
            fg="#1f2937",
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        config.log_text = self.log_text

        self.log_message("[INFO] Application started successfully", "green")
        self.log_message(f"[INFO] Session file: {self.session_file}", "blue")

    def import_from_csv(self):
        """Import session data from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                data = next(reader)

                for field in self.entries:
                    if field in data:
                        self.entries[field].delete(0, tk.END)
                        self.entries[field].insert(0, data[field])

                self.log_message(
                    "[SUCCESS] Session data imported from CSV", "green")
                messagebox.showinfo(
                    "Success", "Session data imported successfully!")
        except Exception as e:
            self.log_message(f"[ERROR] Failed to import CSV: {e}", "red")
            messagebox.showerror("Error", f"Failed to import CSV: {e}")

    def save_session(self):
        """Save session data to JSON file for persistence"""
        session_data = {
            field: entry.get().strip()
            for field, entry in self.entries.items()
        }
        session_data["last_updated"] = datetime.now().isoformat()

        try:
            with open(self.session_file, 'w') as file:
                json.dump(session_data, file, indent=4)
            self.log_message(
                "[SUCCESS] Session data saved successfully", "green")
            messagebox.showinfo(
                "Success", f"Session saved to:\n{self.session_file}")
        except Exception as e:
            self.log_message(f"[ERROR] Failed to save session: {e}", "red")

    def load_session(self):
        """Load saved session data"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                print(f"Failed to load session: {e}")
        return {}

    def clear_session(self):
        """Clear all session fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.post_url_entry.delete(0, tk.END)

        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
                self.log_message(
                    "[INFO] Session file deleted from temp directory", "blue")
            except Exception as e:
                self.log_message(
                    f"[ERROR] Failed to delete session file: {e}", "red")

        self.log_message("[INFO] Session data cleared", "blue")

    def populate_fields(self):
        """Populate fields with saved session data"""
        saved_data = self.load_session()
        if saved_data:
            for field, entry in self.entries.items():
                if field in saved_data:
                    entry.insert(0, saved_data[field])
            self.log_message(
                "[INFO] Previous session data loaded from temp storage", "blue")

    def start_scraping(self):
        """Start the scraping process"""
        if self.is_scraping:
            return

        self.status_label.config(text="⏳ Validating inputs...", fg="#3498db")
        self.log_message("[INFO] Validating user inputs...", "blue")

        config.session_data = {
            field: entry.get().strip()
            for field, entry in self.entries.items()
        }
        post_url = self.post_url_entry.get().strip()

        if not all(config.session_data.values()) or not post_url:
            messagebox.showerror("Error", "All fields are required!")
            self.log_message(
                "[ERROR] Validation failed: Missing required fields", "red")
            self.status_label.config(text="❌ Validation failed", fg="#e74c3c")
            return

        try:
            shortcode = custom_utils.extract_id(post_url)
            config.post_url = post_url
            config.shortcode = shortcode
            self.log_message(
                f"[INFO] Extracted shortcode: {shortcode}", "blue")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid URL: {e}")
            self.log_message(
                f"[ERROR] Failed to extract shortcode: {e}", "red")
            self.status_label.config(text="❌ Invalid URL", fg="#e74c3c")
            return

        self.stop_requested = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scraping = True
        self.stop_event.clear()

        # IMPORTANT: Store stop_event in config so main.py can access it
        config.stop_event = self.stop_event

        threading.Thread(target=self.run_scraper, daemon=True).start()

    def run_scraper(self):
        """Run the scraper in a separate thread"""
        try:
            self.status_label.config(
                text="⚙️ Scraping in progress...", fg="#f39c12")
            self.log_message("[INFO] Scraper started...", "green")

            # Call main function WITHOUT passing stop_event
            # The stop_event is now accessible via config.stop_event
            main.main()

            if not self.stop_event.is_set():
                self.status_label.config(
                    text="✅ Scraping completed!", fg="#27ae60")
                self.log_message(
                    "[SUCCESS] Scraping completed successfully", "green")
            else:
                self.status_label.config(
                    text="⏹ Stopped by user", fg="#e67e22")
                self.log_message("[INFO] Scraping stopped by user", "orange")
        except Exception as e:
            if not self.stop_event.is_set():
                self.status_label.config(text=f"❌ Error: {e}", fg="#e74c3c")
                self.log_message(f"[ERROR] An error occurred: {e}", "red")
        finally:
            self.is_scraping = False
            self.stop_requested = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_scraping(self):
        """Stop the scraping process"""
        if self.is_scraping and not self.stop_requested:
            self.stop_requested = True
            self.stop_event.set()
            self.stop_button.config(state=tk.DISABLED)
            self.log_message(
                "[INFO] Stop requested. Waiting for operation to complete...", "orange")
            self.status_label.config(text="⏸️ Stopping...", fg="#e67e22")

    def log_message(self, message, color="black"):
        """Add message to log with color"""
        self.log_text.config(state=tk.NORMAL)

        color_map = {
            "red": "#dc2626",
            "green": "#16a34a",
            "blue": "#2563eb",
            "orange": "#ea580c",
            "black": "#1f2937"
        }

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        tag_name = f"color_{color}"
        self.log_text.tag_config(
            tag_name, foreground=color_map.get(color, "#1f2937"))

        self.log_text.insert(tk.END, formatted_message, tag_name)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramScraperGUI(root)
    app.populate_fields()
    root.mainloop()
