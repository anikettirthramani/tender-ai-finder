import requests
from bs4 import BeautifulSoup

URL = "https://nmc.gov.in/home/quotation"

KEYWORDS = [
    "jcb",
    "backhoe",
    "backhoe loader",
    "earthmoving",
    "earthmoving equipment",
    "excavator",
    "dumper",
    "tipper",
    "transportation",
    "loading",
    "material supply",
    "sand",
    "stone",
    "aggregate",
    "road",
    "earthwork"
]


headers = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(
    URL,
    headers=headers,
    timeout=60
)

response.raise_for_status()


soup = BeautifulSoup(
    response.text,
    "html.parser"
)


text = soup.get_text(
    " ",
    strip=True
).lower()


matches = []


for keyword in KEYWORDS:

    if keyword in text:

        matches.append(keyword)


print("NMC TEST REPORT")
print("----------------")
print("Page status: OK")
print("Matched keywords:")

for item in matches:
    print("✅", item)


if len(matches) == 0:
    print("No matching keywords found")
