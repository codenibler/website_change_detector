from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

import subprocess
import datetime
import requests
import os

DEFAULT_URL = (
    "https://www.uva.nl/en/programmes/minors/amsterdam-data-science-minor/"
    "amsterdam-data-science-and-artificial-intelligence.html?origin=6xQ7G8NhQXOpa9cYEg%2BQRg"
)
DEFAULT_HEADING_TITLE = "Application and Admission"
DEFAULT_CHECK_INTERVAL_SECONDS = "300"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TZ = ZoneInfo("Europe/Amsterdam")

def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

def get_check_interval_seconds():
    value = os.getenv("CHECK_INTERVAL_SECONDS", DEFAULT_CHECK_INTERVAL_SECONDS)

    try:
        interval = int(value)
    except ValueError as exc:
        raise ValueError("CHECK_INTERVAL_SECONDS must be a whole number.") from exc

    if interval <= 0:
        raise ValueError("CHECK_INTERVAL_SECONDS must be greater than 0.")

    return interval

load_dotenv()

URL = os.getenv("WEBSITE_URL", DEFAULT_URL)
HEADING_TITLE = os.getenv("HEADING_TITLE", DEFAULT_HEADING_TITLE)
CHECK_INTERVAL_SECONDS = get_check_interval_seconds()

def extract_registration_section(html):
    soup = BeautifulSoup(html, "html.parser")

    for section in soup.select("div.richtext"):
        heading = section.find("h2")
        if heading and heading.get_text(" ", strip=True) == HEADING_TITLE:
            return str(section)

    raise ValueError(f'Could not find the "{HEADING_TITLE}" section.')

def main():

    print(f"{datetime.datetime.now(TZ)}. Checking whether Registration dates have changed.")
    print(f"{datetime.datetime.now(TZ)}. Configured check interval: {CHECK_INTERVAL_SECONDS} seconds.")
    with open("last_fetch/latest.html", "r", encoding="utf-8") as file:
        previous_html = file.read()

    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    text = response.text

    previous_section = extract_registration_section(previous_html)
    current_section = extract_registration_section(text)

    if current_section != previous_section:
        print(f"{datetime.datetime.now(TZ)}. Changes detected on website. Sending Osascript notification.")
        subprocess.run(
            ["osascript", "-e", 'display notification "UvA Minor Opened! Check it out!" with title "Minor Scanning Machine"'], 
            check=False
        )
    else:
        print(f"{datetime.datetime.now(TZ)}. No changes detected.")

    with open("last_fetch/latest.html", "w", encoding="utf-8") as file:
        file.write(text)

if __name__ == "__main__":
    main()
