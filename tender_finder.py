import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = "https://www.mahagenco.in"
TENDER_URL = "https://www.mahagenco.in/tenders"

SEEN_FILE = "seen_tenders.json"

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
    "earthwork",
    "excavation",
    "construction material",
    "sand supply",
    "stone supply",
    "aggregate supply",
    "loading and transportation",
    "lifting and transportation"
]


def send_telegram(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        },
        timeout=60
    )

    response.raise_for_status()


def clean_text(text):

    return " ".join(
        text.split()
    )


def load_seen():

    if not os.path.exists(
        SEEN_FILE
    ):
        return []

    with open(
        SEEN_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def save_seen(links):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            links,
            file,
            indent=2
        )


def get_title_before_link(link):

    previous = link.find_previous(
        string=True
    )

    while previous:

        title = clean_text(
            str(previous)
        )

        if (
            title
            and title.lower()
            not in [
                "download",
                "open tenders",
                "awarded tenders"
            ]
            and len(title) > 10
        ):

            return title

        previous = (
            previous.find_previous(
                string=True
            )
        )

    return ""


def get_matching_tenders():

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

    matches = []
    found_links = set()

    for link in soup.find_all(
        "a",
        href=True
    ):

        link_text = clean_text(
            link.get_text(
                " ",
                strip=True
            )
        ).lower()

        if "download" not in link_text:
            continue

        title = (
            get_title_before_link(
                link
            )
        )

        if not title:
            continue

        title_lower = (
            title.lower()
        )

        matched = [

            keyword

            for keyword in KEYWORDS

            if keyword in title_lower

        ]

        if not matched:
            continue

        tender_link = urljoin(
            BASE_URL,
            link["href"]
        )

        if tender_link in found_links:
            continue

        found_links.add(
            tender_link
        )

        matches.append({
            "title": title,
            "link": tender_link,
            "matched": matched
        })

    return matches


try:

    seen = set(
        load_seen()
    )

    tenders = (
        get_matching_tenders()
    )

    new_tenders = [

        tender

        for tender in tenders

        if tender["link"]
        not in seen

    ]

    if new_tenders:

        message = (
            "🔔 NEW RELEVANT "
            "MAHAGENCO TENDERS\n\n"
            f"New tenders: "
            f"{len(new_tenders)}\n\n"
        )

        for number, tender in enumerate(
            new_tenders[:5],
            start=1
        ):

            message += (
                f"{number}. "
                f"{tender['title']}\n\n"
                f"Matched: "
                f"{', '.join(tender['matched'])}\n"
                f"Document: "
                f"{tender['link']}\n\n"
                "━━━━━━━━━━\n\n"
            )

        send_telegram(
            message
        )

        seen.update(
            tender["link"]
            for tender
            in new_tenders
        )

        save_seen(
            sorted(seen)
        )

        print(
            f"New tenders sent: "
            f"{len(new_tenders)}"
        )

    else:

        print(
            "No new relevant "
            "tenders found."
        )

except Exception as error:

    error_message = (
        "⚠️ Tender Finder Error\n\n"
        + str(error)
    )

    send_telegram(
        error_message
    )

    print(error)
