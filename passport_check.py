import os
import json
import requests
from playwright.sync_api import sync_playwright

URL = "https://moj.gov.pl/uslugi/engine/ng/index?xFormsAppName=SprawdzCzyDokumentPaszportowyJestGotowy&Language=en#"

PASSPORT_NUMBER = os.environ["PASSPORT_NUMBER"]

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

STATUS_FILE = "status.json"


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )


def load_previous_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f).get("status")
    return None


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": status}, f)


def get_status():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        page.locator("input").fill(PASSPORT_NUMBER)

        page.get_by_role("button", name="CHECK").click()

        page.wait_for_timeout(3000)

        status_box = page.locator("text=Passport")

        text = page.locator("body").inner_text()

        browser.close()

        return text


def extract_status(page_text):

    if "Passport is ready for collection" in page_text:
        return "READY"

    if "Passport is in production" in page_text:
        return "IN_PRODUCTION"

    if "Passport application registered" in page_text:
        return "REGISTERED"

    return "UNKNOWN"


page_text = get_status()
current_status = extract_status(page_text)
previous_status = load_previous_status()

print(f"Current: {current_status}")
print(f"Previous: {previous_status}")

if previous_status is None:
    save_status(current_status)

elif current_status != previous_status:

    send_telegram(
        f"🇵🇱 Passport status changed\n\n"
        f"Old: {previous_status}\n"
        f"New: {current_status}"
    )

    save_status(current_status)

if current_status == "READY":
    send_telegram(
        "🎉 PASSPORT READY FOR COLLECTION!"
    )
