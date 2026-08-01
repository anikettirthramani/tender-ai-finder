import requests
from io import BytesIO
from pypdf import PdfReader

PDF_URL = (
    "https://www.mahagenco.in/"
    "tenderpdf/"
    "EOI_Dry%20Fly%20Ash%20Transport%20"
    "from%20Koradi%20Khaperkheda%20"
    "Final_20260210111807662.pdf"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64)"
    )
}

response = requests.get(
    PDF_URL,
    headers=headers,
    timeout=120
)

response.raise_for_status()

pdf_file = BytesIO(
    response.content
)

reader = PdfReader(
    pdf_file
)

print(
    "PDF downloaded successfully."
)

print(
    "Total pages:",
    len(reader.pages)
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

print(
    "\nFIRST 5 PAGES:\n"
)

print(
    text[:12000]
)
