import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

URL = "https://divar.ir/s/tehran/car/peugeot/207i/automatic-p-tu5?q=207"
SCROLL_PAUSE = 1.5  # seconds to wait after each scroll for new cards to load
MAX_SCROLLS = 200  # hard cap so a stuck page can't loop forever
STABLE_LIMIT = 3  # stop after this many scrolls in a row add zero new cards


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
        km = desc_tags[0].get_text(strip=True) if len(desc_tags) > 0 else ""
        price = desc_tags[1].get_text(strip=True) if len(desc_tags) > 1 else ""

        rows[href] = {
            "title": title,
            "km": km,
            "price": price,
            "link": "https://divar.ir" + href,
        }

    return rows


def scrape(url: str) -> list[dict[str, str]]:
    """Load the page, scroll to trigger lazy-loading, and collect all cards.

    The list is virtualized - cards scrolled out of view can be removed
    from the DOM - so we parse and accumulate after every scroll step
    instead of only reading the page once at the end.
    """
    options = Options()
    options.add_argument("--headless=new")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        raise RuntimeError(
            "Could not start Chrome. Make sure Chrome/Chromium is installed "
            "and matches your selenium version."
        ) from e

    all_rows: dict[str, dict[str, str]] = {}

    try:
        try:
            driver.get(url)
        except WebDriverException as e:
            raise RuntimeError(f"Failed to load {url}") from e

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
        writer = csv.DictWriter(f, fieldnames=["title", "km", "price", "link"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    try:
        data = scrape(URL)
    except RuntimeError as e:
        print(f"Scraping failed: {e}")
        raise SystemExit(1)

    save_csv(data, "divar_207.csv")
    print(f"saved {len(data)} rows to divar_207.csv")
