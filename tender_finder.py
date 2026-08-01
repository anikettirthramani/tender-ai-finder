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
    seen_titles = set()

    for link in soup.find_all(
        "a",
        href=True
    ):

        link_text = link.get_text(
            " ",
            strip=True
        ).lower()

        if (
            "download" not in link_text
            and "tender" not in link_text
        ):
            continue

        parent = link

        for _ in range(5):

            if parent.parent:
                parent = parent.parent

        block_text = parent.get_text(
            " ",
            strip=True
        )

        block_lower = (
            block_text.lower()
        )

        matched_words = [

            keyword

            for keyword in KEYWORDS

            if keyword in block_lower

        ]

        if not matched_words:
            continue

        title = block_text

        if len(title) > 700:

            title = title[:700] + "..."

        if title in seen_titles:
            continue

        seen_titles.add(
            title
        )

        tender_link = urljoin(
            BASE_URL,
            link["href"]
        )

        matches.append({
            "title": title,
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
            "🔔 MAHAGENCO "
            "MATCHING TENDERS\n\n"
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
            "No matching tender blocks "
            "were found."
        )

    send_telegram(
        message
    )

    print(
        f"Matching tenders: "
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
