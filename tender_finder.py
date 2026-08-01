import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = [
    "fly ash",
    "pond ash",
    "ash transportation",
    "jcb hiring",
    "backhoe loader hiring",
    "hydraulic excavator hiring",
    "dumper hiring",
    "tipper hiring",
    "transportation",
    "earthwork",
    "construction material supply",
    "sand supply",
    "stone supply",
    "aggregate supply"
]

LOCATIONS = [
    "Nashik",
    "Maharashtra"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()

today = datetime.now().strftime("%d-%m-%Y")

message = (
    "🔔 Tender AI Finder is running\n\n"
    f"Date: {today}\n\n"
    "Categories being monitored:\n"
    + "\n".join(f"• {item}" for item in KEYWORDS)
    + "\n\nLocations:\n"
    + "\n".join(f"• {place}" for place in LOCATIONS)
    + "\n\nThe automatic system is active."
)

send_telegram(message)

print("Telegram message sent successfully.")
