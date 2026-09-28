import os
from playwright.sync_api import sync_playwright

URL = "https://moj.gov.pl/uslugi/engine/ng/index?xFormsAppName=SprawdzCzyDokumentPaszportowyJestGotowy&Language=en#"

PASSPORT_NUMBER = os.environ["PASSPORT_NUMBER"]


def get_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        page.screenshot(path="debug.png", full_page=True)

        print("TITLE:")
        print(page.title())

        print("BODY:")
        print(page.locator("body").inner_text())

        browser.close()

        return "DEBUG"


def extract_status(page_text):
    if "Passport is ready for collection" in page_text:
        return "READY"

    if "Passport is in production" in page_text:
        return "IN_PRODUCTION"

    if "Passport application registered" in page_text:
        return "REGISTERED"

    return "UNKNOWN"


page_text = get_status()

print(page_text)
