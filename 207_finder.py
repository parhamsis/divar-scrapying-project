import csv
import requests
from bs4 import BeautifulSoup

URL = "https://divar.ir/s/tehran/car/peugeot/207i/automatic-p-tu5?q=207"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape(url: str) -> list[dict[str, str]]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows: list[dict[str, str]] = []
    for card in soup.select("a.kt-post-card__action"):
        title_tag = card.select_one("h2.kt-post-card__title")
        desc_tags = card.select("div.kt-post-card__description")

        title = title_tag.get_text(strip=True) if title_tag else ""
        km = desc_tags[0].get_text(strip=True) if len(desc_tags) > 0 else ""
        price = desc_tags[1].get_text(strip=True) if len(desc_tags) > 1 else ""
        link = "https://divar.ir" + card.get("href", "")

        rows.append({"title": title, "km": km, "price": price, "link": link})

    return rows


def save_csv(rows: list[dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "km", "price", "link"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = scrape(URL)
    save_csv(data, "divar_207.csv")
    print(f"saved {len(data)} rows to divar_207.csv")
