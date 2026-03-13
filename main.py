from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

import subprocess
import datetime
import requests
import os

URL = (
    "https://www.uva.nl/en/programmes/minors/amsterdam-data-science-minor/"
    "amsterdam-data-science-and-artificial-intelligence.html?origin=6xQ7G8NhQXOpa9cYEg%2BQRg"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}
TZ = ZoneInfo("Europe/Amsterdam")

def extract_registration_section(html):
    soup = BeautifulSoup(html, "html.parser")

    for section in soup.select("div.richtext"):
        heading = section.find("h2")
        if heading and heading.get_text(" ", strip=True) == "Application and Admission":
            return str(section)

    raise ValueError("Could not find the Application and Admission section.")

def main():

    print(f"{datetime.datetime.now(TZ)}. Checking whether Registration dates have changed.")
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
