import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

SCROLL_PAUSE = 2  # seconds to wait after each scroll for new cards to load
MAX_SCROLLS = 200  # hard cap so a stuck page can't loop forever
STABLE_LIMIT = 5  # stop after this many scrolls in a row add zero new cards

def search_divar() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    while True:
        city: str = input("City: ")
        query: str = input("Search: ")
        url: str = f"https://divar.ir/s/{city}"
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.select_one(".kt-page-title__title")
        if title is not None and title.get_text(strip=True) == "این صفحه حذف شده یا وجود ندارد":
            print("Wrong city")
            continue

        search_box = driver.find_element(By.NAME, "search")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(2)  # let results load
        break

    return driver


def parse_cards(html: str) -> dict[str, dict[str, str]]:
    """Extract post cards from a page of HTML, keyed by href to dedupe."""
    soup = BeautifulSoup(html, "html.parser")
    rows: dict[str, dict[str, str]] = {}

    for card in soup.select("a.kt-post-card__action"):
        href = card.get("href", "")
        if not href or href in rows:
            continue

        title_tag = card.select_one("h2.kt-post-card__title")
        desc_tags = card.select("div.kt-post-card__description")

        # divar shows two description lines per card: mileage, then price.
        # Missing tags just mean this card is malformed - fall back to "".
        title = title_tag.get_text(strip=True) if title_tag else ""
        description = desc_tags[0].get_text(strip=True) if len(desc_tags) > 0 else ""
        price = desc_tags[1].get_text(strip=True) if len(desc_tags) > 1 else ""

        rows[href] = {
            "title": title,
            "description": description,
            "price": price,
            "link": "https://divar.ir" + href,
        }

    return rows


def scrape(driver: webdriver.Chrome) -> list[dict[str, str]]:

    all_rows: dict[str, dict[str, str]] = {}

    try:
        stable_rounds = 0
        last_count = 0

        for _ in range(MAX_SCROLLS):
            all_rows.update(parse_cards(driver.page_source))

            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(SCROLL_PAUSE)

            count = len(all_rows)
            if count == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
            last_count = count

            if stable_rounds >= STABLE_LIMIT:
                break

            try:
                button = driver.find_element(By.CSS_SELECTOR, "button.post-list__load-more-btn-be092")
                print("Loading more ads!")
                button.click()

            except:
                pass

            print(f"{count} items found")

        # one last parse in case the final scroll loaded anything new
        all_rows.update(parse_cards(driver.page_source))
    finally:
        # always close the browser, even if something above raised
        driver.quit()

    return list(all_rows.values())


def save_csv(rows: list[dict[str, str]], path: str) -> None:
    if not rows:
        print("No rows to save - skipping CSV write.")
        return

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "price", "link"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    try:
        data = scrape(search_divar())
    except RuntimeError as e:
        print(f"Scraping failed: {e}")
        raise SystemExit(1)

    save_csv(data, "divar_export.csv")
    print(f"saved {len(data)} rows to divar_export.csv")
