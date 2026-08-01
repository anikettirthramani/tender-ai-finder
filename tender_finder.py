import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = "https://www.mahagenco.in"
TENDER_URL = "https://www.mahagenco.in/tenders"

KEYWORDS = [
    "fly ash",
    "pond ash",
    "ash transportation",
    "ash handling",
    "jcb",
    "backhoe",
    "excavator",
    "earthmoving",
    "dumper",
    "tipper",
    "transportation",
    "transport",
    "earthwork",
    "excavation",
    "construction material",
    "sand",
    "stone",
    "aggregate",
    "loading"
]

SEEN_FILE = "seen_tenders.json"


def send_telegram(message):

    api_url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }

    response = requests.post(
        api_url,
        data=data,
        timeout=30
    )

    response.raise_for_status()


def load_seen_tenders():

    if not os.path.exists(SEEN_FILE):
        return []

    with open(
        SEEN_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_seen_tenders(tenders):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tenders,
            file,
            indent=2
        )


def get_matching_tenders():

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    response = requests.get(
        TENDER_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    matches = []

    links = soup.find_all(
        "a",
        href=True
    )

    for link in links:

        title = link.get_text(
            " ",
            strip=True
        )

        href = link.get(
            "href"
        )

        if not title:
            continue

        title_lower = (
            title.lower()
        )

        matched_words = [

            keyword

            for keyword in KEYWORDS

            if keyword in title_lower

        ]

        if matched_words:

            tender_link = urljoin(
                BASE_URL,
                href
            )

            tender = {
                "title": title,
                "link": tender_link,
                "matched": matched_words
            }

            if tender not in matches:

                matches.append(
                    tender
                )

    return matches

try:

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/131.0 Safari/537.36"
        )
    }

    response = requests.get(
        TENDER_URL,
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    page_title = ""

    if soup.title:
        page_title = soup.title.get_text(
            " ",
            strip=True
        )

    all_links = soup.find_all(
        "a",
        href=True
    )

    page_text = soup.get_text(
        " ",
        strip=True
    )

    message = (
        "🔧 MAHAGENCO DIAGNOSTIC REPORT\n\n"
        f"Status code: {response.status_code}\n"
        f"Page title: {page_title}\n"
        f"HTML size: {len(response.text)} characters\n"
        f"Links found: {len(all_links)}\n"
        f"Page text size: {len(page_text)} characters\n\n"
        "First page text:\n"
        + page_text[:2500]
    )

    send_telegram(
        message
    )

    print(
        "Diagnostic report sent."
    )

except Exception as error:

    error_message = (
        "⚠️ Diagnostic Error\n\n"
        + str(error)
    )

    send_telegram(
        error_message
    )

    print(error)

    
