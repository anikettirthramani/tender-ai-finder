import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://www.mahagenco.in/tenders"

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
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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


def get_tenders():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    page_text = soup.get_text(
        " ",
        strip=True
    )

    found = []

    for keyword in KEYWORDS:

        if keyword.lower() in page_text.lower():

            found.append(keyword)

    return found


try:

    matches = get_tenders()

    today = datetime.now().strftime(
        "%d-%m-%Y"
    )

    if matches:

        message = (
            "🔔 MAHAGENCO Tender Alert\n\n"
            f"Date: {today}\n\n"
            "Possible matching categories found:\n\n"
            + "\n".join(
                f"✅ {item}"
                for item in matches
            )
            + "\n\nCheck official tender page:\n"
            + URL
        )

    else:

        message = (
            "📋 Tender search completed\n\n"
            f"Date: {today}\n\n"
            "No matching keyword was found "
            "on the MAHAGENCO tender page today."
        )

    send_telegram(message)

    print(
        "Tender search completed successfully."
    )

except Exception as error:

    error_message = (
        "⚠️ Tender Finder Error\n\n"
        + str(error)
    )

    send_telegram(error_message)

    print(error)
