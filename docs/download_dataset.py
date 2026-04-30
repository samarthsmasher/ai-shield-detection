"""
Task 3.1 - Download SMS Spam Collection dataset into /models/data/spam.csv
Uses a reliable Kaggle-mirror raw URL. Falls back to UCI if needed.
"""
import urllib.request
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'data')
OUT_PATH = os.path.join(DATA_DIR, 'spam.csv')

os.makedirs(DATA_DIR, exist_ok=True)

# Primary: Kaggle mirror (raw CSV, no authentication needed)
URLS = [
    "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv",
    "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/tips.csv",  # fallback test only
]

# We'll fetch from a well-known GitHub mirror of the SMS Spam Collection
PRIMARY_URL = "https://raw.githubusercontent.com/mohitgupta-omg/Kaggle-SMS-Spam-Collection-Dataset-/master/spam.csv"
BACKUP_URL  = "https://raw.githubusercontent.com/nicapotato/SpamSMS/master/spam.csv"

def download(url, dest):
    print(f"Downloading from: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        size = os.path.getsize(dest)
        print(f"Saved to: {dest}  ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

if os.path.exists(OUT_PATH) and os.path.getsize(OUT_PATH) > 10000:
    print(f"Dataset already exists at {OUT_PATH}")
    sys.exit(0)

if not download(PRIMARY_URL, OUT_PATH):
    print("Trying backup URL...")
    if not download(BACKUP_URL, OUT_PATH):
        print("ERROR: Both downloads failed. Please manually place spam.csv in models/data/")
        sys.exit(1)

# Quick sanity check
with open(OUT_PATH, 'r', encoding='latin-1') as f:
    lines = f.readlines()
print(f"Dataset lines: {len(lines)}")
print(f"First line: {lines[0].strip()[:80]}")
print("Dataset download complete!")
