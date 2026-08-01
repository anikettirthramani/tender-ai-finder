import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    seen_links = set()

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

        tender_title = (
            get_title_before_link(
                link
            )
        )

        if not tender_title:
            continue

        title_lower = (
            tender_title.lower()
        )

        matched_words = [

            keyword

            for keyword in KEYWORDS

            if keyword in title_lower

        ]

        if not matched_words:
            continue

        tender_link = urljoin(
            BASE_URL,
            link["href"]
        )

        if tender_link in seen_links:
            continue

        seen_links.add(
            tender_link
        )

        matches.append({
            "title": tender_title,
            "link": tender_link,
            "matched": matched_words
        })

    return matches


try:

    tenders = (
        get_matching_tenders()
    )

    if tenders:

        message = (
            "🔔 RELEVANT MAHAGENCO "
            "TENDERS\n\n"
            f"Found: {len(tenders)}\n\n"
        )

        for number, tender in enumerate(
            tenders[:5],
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

    else:

        message = (
            "📋 MAHAGENCO Search Complete\n\n"
            "No relevant tender was found "
            "for your selected categories."
        )

    send_telegram(
        message
    )

    print(
        f"Relevant tenders: "
        f"{len(tenders)}"
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
