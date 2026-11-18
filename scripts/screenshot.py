import os
import datetime
from playwright.sync_api import sync_playwright

url = os.environ["TARGET_URL"]
width = int(os.environ.get("VIEW_WIDTH", "1280"))
height = int(os.environ.get("VIEW_HEIGHT", "800"))
full_page = os.environ.get("FULL_PAGE", "false") == "true"

os.makedirs("screenshots", exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
out_path = f"screenshots/screenshot-{ts}.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": width, "height": height})
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.screenshot(path=out_path, full_page=full_page)
    browser.close()

print(f"saved: {out_path}")
