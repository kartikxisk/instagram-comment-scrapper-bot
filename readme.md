# Instagram Comment Scraper Bot

This project is a GUI-based Instagram comment scraper bot that extracts comments, usernames, and mentionable statuses from Instagram posts or reels. The bot uses the `instaloader` library for scraping and saves the extracted data into an Excel file.

## Features

- **GUI Interface**: Built with `Tkinter` for easy user interaction.
- **Session-Based Login**: Logs in using Instagram session data.
- **Comment Extraction**: Fetches comments, usernames, and mentionable statuses from Instagram posts or reels.
- **Excel Export**: Saves the extracted data into an Excel file (`.xlsx` format).
- **Rate Limiting Handling**: Custom rate controller to handle Instagram's rate limits.
- **Logging**: Logs messages to both the console and the GUI.

## Requirements

The project requires the following Python libraries:
- `Python 3.9.13` 
- `instaloader`
- `pandas`
- `openpyxl`
- `pyinstaller`

Install the dependencies using the following commands:

```bash
python -m venv myenv
myenv\Scripts\activate

pip install -r requirements.txt

```

Build Command

```bash
pyinstaller --noconfirm --onefile --windowed --name "InstagramCommentScraper" main.py
```
