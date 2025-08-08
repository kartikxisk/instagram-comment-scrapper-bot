import re
import os

def extract_id(url):
    match = re.search(r'/(reel|p)/([A-Za-z0-9_-]+)', url)
    return match.group(2) if match else None

def get_data_folder(filename=None):
    """
    Returns the path to the 'data' folder one level up.
    If a filename is provided, returns the full path to the file inside 'data'.
    """
    # parent_dir = os.path.join(os.getcwd(), "..", "data")
    parent_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(parent_dir, exist_ok=True)  # Ensure the folder exists

    if filename:
        return os.path.join(parent_dir, filename)  # Return full file path
    return parent_dir  # Return only the folder path