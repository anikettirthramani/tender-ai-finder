import os
import json
import re
import requests

from io import BytesIO
from datetime import datetime

from bs4 import BeautifulSoup
from pypdf import PdfReader
from urllib.parse import urljoin


BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

BASE_URL = (
    "https://www.mahagenco.in"
)

TENDER_URL = (
    "https://www.mahagenco.in/tenders"
)

SEEN_FILE = (
    "seen_tenders.json"
)


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

        "https://api.telegram.org/"
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

    try:

        with open(

            SEEN_FILE,

            "r",

            encoding="utf-8"

        ) as file:

            data = json.load(
                file
            )

            if isinstance(
                data,
                list
            ):

                return data

            return []

    except Exception:

        return []


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

    previous = (
        link.find_previous(
            string=True
        )
    )

    while previous:

        title = clean_text(
            str(previous)
        )

        if (

            title

            and

            title.lower()

            not in [

                "download",

                "open tenders",

                "awarded tenders"

            ]

            and

            len(title) > 10

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

            "(Windows NT 10.0; "

            "Win64; x64)"

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

            for keyword

            in KEYWORDS

            if keyword

            in title_lower

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


def read_pdf_text(pdf_url):

    headers = {

        "User-Agent": (
            "Mozilla/5.0"
        )

    }

    response = requests.get(

        pdf_url,

        headers=headers,

        timeout=120

    )

    response.raise_for_status()

    reader = PdfReader(

        BytesIO(
            response.content
        )

    )

    text = ""

    for page in reader.pages[:5]:

        page_text = (
            page.extract_text()
        )

        if page_text:

            text += (
                page_text
                + "\n"
            )

    return text


def find_closing_date(text):

    patterns = [

        r"(?:last date.*?"
        r"(?:submission|bid|eoi).*?)"
        r"(\d{2}[./-]"
        r"\d{2}[./-]"
        r"\d{4})",

        r"(?:bid submission"
        r".{0,100}?)"
        r"(\d{2}[./-]"
        r"\d{2}[./-]"
        r"\d{4})",

        r"(?:closing date"
        r".{0,100}?)"
        r"(\d{2}[./-]"
        r"\d{2}[./-]"
        r"\d{4})",

        r"(?:due date"
        r".{0,100}?)"
        r"(\d{2}[./-]"
        r"\d{2}[./-]"
        r"\d{4})"

    ]

    text_lower = (
        text.lower()
    )

    for pattern in patterns:

        match = re.search(

            pattern,

            text_lower,

            re.DOTALL

        )

        if match:

            date_text = (

                match.group(1)

            )

            date_text = (

                date_text

                .replace(
                    "/",
                    "."
                )

                .replace(
                    "-",
                    "."
                )

            )

            try:

                return datetime.strptime(

                    date_text,

                    "%d.%m.%Y"

                )

            except ValueError:

                pass

    return None


def check_tender(tender):

    try:

        pdf_text = (

            read_pdf_text(
                tender["link"]
            )

        )

        closing_date = (

            find_closing_date(
                pdf_text
            )

        )

        if closing_date:

            today = (
                datetime.now()
            )

            if closing_date < today:

                return {

                    "status":
                    "expired",

                    "date":

                    closing_date.strftime(
                        "%d-%m-%Y"
                    )

                }

            return {

                "status":
                "active",

                "date":

                closing_date.strftime(
                    "%d-%m-%Y"
                )

            }

        return {

            "status":
            "unknown",

            "date":
            "Not found"

        }

    except Exception:

        return {

            "status":
            "unknown",

            "date":
            "Could not read"

        }


try:

    seen = set(
        load_seen()
    )

    tenders = (
        get_matching_tenders()
    )

    new_tenders = [

        tender

        for tender

        in tenders

        if tender["link"]

        not in seen

    ]

    active_tenders = []

    unknown_tenders = []

    expired_count = 0


    for tender in new_tenders:

        result = (
            check_tender(
                tender
            )
        )

        if (
            result["status"]
            == "active"
        ):

            tender[
                "closing_date"
            ] = (
                result["date"]
            )

            active_tenders.append(
                tender
            )

        elif (
            result["status"]
            == "expired"
        ):

            expired_count += 1

        else:

            unknown_tenders.append(
                tender
            )


    message = (

        "📋 MAHAGENCO "
        "TENDER SCAN\n\n"

        f"Relevant notices found: "
        f"{len(tenders)}\n"

        f"New notices checked: "
        f"{len(new_tenders)}\n\n"

        f"🟢 Active: "
        f"{len(active_tenders)}\n"

        f"🔴 Expired: "
        f"{expired_count}\n"

        f"🟡 Date not found: "
        f"{len(unknown_tenders)}\n\n"

    )


    if active_tenders:

        message += (

            "🟢 ACTIVE "
            "TENDERS\n\n"

        )

        for number, tender in enumerate(

            active_tenders[:5],

            start=1

        ):

            message += (

                f"{number}. "

                f"{tender['title']}\n\n"

                f"Closing date: "

                f"{tender['closing_date']}\n"

                f"Matched: "

                f"{', '.join(tender['matched'])}\n"

                f"Document: "

                f"{tender['link']}\n\n"

                "━━━━━━━━━━\n\n"

            )

    else:

        message += (

            "Status: No new active "
            "tender found today. ✅\n\n"

        )


    if unknown_tenders:

        message += (

            "🟡 REVIEW "
            "MANUALLY\n\n"

        )

        for number, tender in enumerate(

            unknown_tenders[:3],

            start=1

        ):

            message += (

                f"{number}. "

                f"{tender['title']}\n"

                f"Document: "

                f"{tender['link']}\n\n"

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

        "New tenders checked:",

        len(new_tenders)

    )

    print(

        "Active tenders:",

        len(active_tenders)

    )

    print(

        "Expired tenders:",

        expired_count

    )

    print(

        "Date not found:",

        len(unknown_tenders)

    )


except Exception as error:

    send_telegram(

        "⚠️ Tender Finder Error\n\n"

        + str(error)

    )

    print(error)
