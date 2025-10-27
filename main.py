import instaloader
import pandas as pd
import custom_utils
import config
import log_utils
from datetime import datetime, timedelta
import os


def login_with_session(session_data):
    """Logs in using a session dictionary."""

    class MyRateController(instaloader.RateController):
        def __init__(self, context):
            super().__init__(context)
            self.rate_limited = False

        def query_waittime(self, query_type: str, current_time: float, untracked_queries: bool = False) -> float:
            """
            Custom wait time calculation that ensures no query waits more than 1 minute (60 seconds).
            """
            base_wait_time = super().query_waittime(
                query_type, current_time, untracked_queries)
            return min(base_wait_time, 0)

        def sleep(self, secs):
            # ADDED: Check for stop during sleep
            stop_event = getattr(config, 'stop_event', None)

            if secs > 0:
                wait_msg = f"Too many queries. Waiting {round(secs)} seconds, until {(datetime.now() + timedelta(seconds=secs)).strftime('%H:%M:%S')}."
                log_utils.log_message(
                    f"[RATE LIMIT] {wait_msg}", config.log_text, "yellow")

            # MODIFIED: Sleep in small increments and check stop event
            remaining = min(secs, 0)
            while remaining > 0:
                if stop_event and stop_event.is_set():
                    log_utils.log_message(
                        "[INFO] Stop requested during rate limit wait", config.log_text, "orange")
                    return
                sleep_time = min(0.5, remaining)  # Sleep 0.5 seconds at a time
                super().sleep(sleep_time)
                remaining -= sleep_time

        def handle_429(self, query_type: str) -> None:
            """
            Handle Instagram's 429 Too Many Requests error by enforcing a one-time wait,
            then resetting rate limits so it can continue normally.
            """
            stop_event = getattr(config, 'stop_event', None)

            # Check if stop was requested
            if stop_event and stop_event.is_set():
                return

            if not self.rate_limited:
                wait_time = 60
                log_utils.log_message(
                    f"[RATE LIMIT] 429 Too Many Requests. Waiting {wait_time} seconds to reset...", config.log_text, "yellow")
                self.sleep(wait_time)
                self.rate_limited = True

            self._query_timestamps.clear()
            self._earliest_next_request_time = 0.0
            self._iphone_earliest_next_request_time = 0.0
            log_utils.log_message(
                "[RATE LIMIT] Resuming normal query speed.", config.log_text, "yellow")
            self.rate_limited = False

    L = instaloader.Instaloader(
        rate_controller=lambda ctx: MyRateController(ctx))

    try:
        log_utils.log_message(
            "[INFO] Attempting to log in using session...", config.log_text, "blue")
        L.load_session(session_data["ds_user_id"], session_data)
        log_utils.log_message(
            "[SUCCESS] Logged in successfully.", config.log_text, "green")
        return L
    except Exception as e:
        log_utils.log_message(
            f"[ERROR] Login failed: {e}", config.log_text, "red")
        return None


def get_post(L, shortcode):
    """Fetch post details using its shortcode."""
    # ADDED: Check for stop event
    stop_event = getattr(config, 'stop_event', None)
    if stop_event and stop_event.is_set():
        return None

    try:
        log_utils.log_message(
            f"[INFO] Fetching post details for shortcode: {shortcode}", config.log_text, "blue")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        log_utils.log_message(
            "[SUCCESS] Post fetched successfully.", config.log_text, "green")
        return post
    except Exception as e:
        log_utils.log_message(
            f"[ERROR] Failed to fetch post: {e}", config.log_text, "red")
        return None


def fetch_comments(post):
    """Extract comments, usernames, and mentionable status from a post with pagination logging."""
    comments_data = []
    count = 0

    # ADDED: Get stop event from config
    stop_event = getattr(config, 'stop_event', None)

    try:
        log_utils.log_message(
            "[INFO] Fetching comments...", config.log_text, "blue")

        file_path = custom_utils.get_data_folder(f"{config.shortcode}.xlsx")

        if os.path.exists(file_path):
            os.remove(file_path)
            log_utils.log_message(
                f"Deleted Previous File: {file_path}", config.log_text, "blue")
        else:
            log_utils.log_message(
                f"File does not exist: {file_path}", config.log_text, "blue")

        for comment in post._get_comments_via_iphone_endpoint():
            # ⚠️ CRITICAL: Check stop event at the start of each iteration
            if stop_event and stop_event.is_set():
                log_utils.log_message(
                    f"[INFO] Scraping stopped by user. Fetched {count} comments before stopping.",
                    config.log_text,
                    "orange"
                )
                # Save any pending comments before exiting
                if comments_data:
                    save_to_excel(comments_data, custom_utils.get_data_folder(
                        f"{config.shortcode}.xlsx"), append=True, showMessage=False)
                return  # Exit the function immediately

            username = comment.owner.username
            comment_text = comment.text
            is_mentionable = comment._node.get("iphone_struct", {}).get(
                "user", {}).get("is_mentionable", False)

            # Append data to list
            comments_data.append([username, comment_text, is_mentionable])
            count += 1

            # Log every 10 comments
            if count % 10 == 0:
                log_utils.log_message(
                    f"[INFO] Fetched {count} comments so far...", config.log_text, "blue")

            # Append to Excel every 20 comments
            if count % 20 == 0:
                # ADDED: Check stop before saving
                if stop_event and stop_event.is_set():
                    log_utils.log_message(
                        "[INFO] Stop requested. Saving data...", config.log_text, "orange")
                    save_to_excel(comments_data, custom_utils.get_data_folder(
                        f"{config.shortcode}.xlsx"), append=True, showMessage=False)
                    return

                save_to_excel(comments_data, custom_utils.get_data_folder(
                    f"{config.shortcode}.xlsx"), append=True, showMessage=False)
                comments_data = []  # Clear the list after appending

        # Save remaining comments
        if comments_data:
            save_to_excel(comments_data, custom_utils.get_data_folder(
                f"{config.shortcode}.xlsx"), append=True)

        log_utils.log_message(
            f"[SUCCESS] Total comments fetched: {count}", config.log_text, "green")

    except Exception as e:
        log_utils.log_message(
            f"[ERROR] Error fetching comments: {e}", config.log_text, "red")
        # Save any pending comments even if there's an error
        if comments_data:
            save_to_excel(comments_data, custom_utils.get_data_folder(
                f"{config.shortcode}.xlsx"), append=True, showMessage=False)


def save_to_excel(comments_data, filename="instagram_comments.xlsx", append=False, showMessage=True):
    """Save extracted comments to an Excel file with an option to append."""
    if comments_data:
        df_new = pd.DataFrame(comments_data, columns=[
                              "Username", "Comment", "Is Mentionable"])

        try:
            if append:
                existing_df = pd.read_excel(filename)
                df_new = pd.concat([existing_df, df_new], ignore_index=True)
        except FileNotFoundError:
            pass  # If file doesn't exist, it will be created

        df_new.to_excel(filename, index=False)

        if showMessage:
            log_utils.log_message(
                f"[SUCCESS] Data appended to '{filename}' successfully.", config.log_text, "green")
    else:
        log_utils.log_message(
            "[WARNING] No comments to save.", config.log_text, "orange")


def main():
    # ADDED: Get stop event at the beginning
    stop_event = getattr(config, 'stop_event', None)

    log_utils.log_message(
        "[INFO] Starting script execution...", config.log_text, "blue")

    # Check if stopped before starting
    if stop_event and stop_event.is_set():
        return

    L = login_with_session(config.session_data)

    # Check after login
    if stop_event and stop_event.is_set():
        return

    if L and L.context.is_logged_in:
        post = get_post(L, config.shortcode)

        # Check after getting post
        if stop_event and stop_event.is_set():
            return

        if post:
            fetch_comments(post)
        else:
            log_utils.log_message(
                "[ERROR] Failed to retrieve post.", config.log_text, "red")
    else:
        log_utils.log_message(
            "[ERROR] Login required. Exiting.", config.log_text, "red")

    # Only log completion if not stopped
    if not (stop_event and stop_event.is_set()):
        log_utils.log_message(
            "[INFO] Script execution completed.", config.log_text, "blue")


if __name__ == "__main__":
    main()
