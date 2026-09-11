import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://divar.ir/s/tehran/car/peugeot/207i/automatic-p-tu5?q=207"
SCROLL_PAUSE = 1.5
MAX_SCROLLS = 200
STABLE_LIMIT = 6


def parse_cards(html: str) -> dict[str, dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    rows: dict[str, dict[str, str]] = {}

    for card in soup.select("a.kt-post-card__action"):
        href = card.get("href", "")
        if not href or href in rows:
            continue

        title_tag = card.select_one("h2.kt-post-card__title")
        desc_tags = card.select("div.kt-post-card__description")

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
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    all_rows: dict[str, dict[str, str]] = {}
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

    all_rows.update(parse_cards(driver.page_source))
    driver.quit()
    return list(all_rows.values())


def save_csv(rows: list[dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "km", "price", "link"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = scrape(URL)
    save_csv(data, "divar_207.csv")
    print(f"saved {len(data)} rows to divar_207.csv")
