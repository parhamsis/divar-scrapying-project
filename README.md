# Divar Scraper

A Python web scraper for extracting advertisement data from [Divar](https://divar.ir) and exporting the results to CSV.

The scraper uses Selenium to interact with Divar's web interface, searches for a user-specified item in a selected city, automatically scrolls through the results, loads additional advertisements when available, and extracts relevant information from each listing.

## Features

- Search Divar by city and query
- Headless Chrome support
- Automatically scroll through search results
- Automatically load additional advertisements
- Deduplicate advertisements by URL
- Extract:
  - Title
  - Description
  - Price
  - Advertisement URL
- Export results to CSV
- UTF-8 CSV output with BOM for spreadsheet compatibility
- Configurable scraping limits and delays

## Requirements

- Python 3.10+
- Google Chrome or Chromium
- Selenium
- BeautifulSoup4
- Pipenv

## Installation

Clone the repository:

```bash
git clone https://github.com/parhamsis/divar-scrapying-project.git
cd divar-scrapying-project
```

Install dependencies:

```bash
pipenv install
```

Run the scraper through Pipenv:

```bash
pipenv run python divar_scraper.py
```

## Usage

Run:

```bash
python divar_scraper.py
```

The program asks for a city and search query:

```text
City: tehran
Search: laptop
```

The scraper then:

1. Opens the Divar search page for the selected city.
2. Searches for the requested item.
3. Collects advertisement cards.
4. Scrolls through the results.
5. Clicks the "load more advertisements" button when available.
6. Deduplicates advertisements using their URLs.
7. Exports the collected data to a CSV file.

Example:

```text
City: tehran
Search: لپتاپ

Loading more ads!
Loading more ads!
Loading more ads!

127 items found
saved 127 rows to divar_export.csv
```

## Output

The scraper creates:

```text
divar_export.csv
```

The CSV contains:

| Column | Description |
|---|---|
| `title` | Advertisement title |
| `description` | Advertisement description |
| `price` | Advertisement price |
| `link` | Direct URL to the advertisement |

Example:

```csv
title,description,price,link
"Lenovo ThinkPad T14","i5 / 16GB / 512GB","35,000,000 تومان","https://divar.ir/v/..."
```

## Project Structure

```text
divar-scrapying-project/
├── divar_scraper.py    # Main scraper
├── Pipfile             # Python dependencies
├── Pipfile.lock        # Locked dependency versions
├── LICENSE             # MIT license
└── README.md
```

### `divar_scraper.py`

The main scraping pipeline:

```text
User input
    ↓
Divar search
    ↓
Load search results
    ↓
Scroll / load more
    ↓
Parse advertisement cards
    ↓
Deduplicate by URL
    ↓
Export CSV
```


## Configuration

The scraper uses several parameters to control the scraping process:

```python
SCROLL_PAUSE = 2
MAX_SCROLLS = 200
STABLE_LIMIT = 5
```

### `SCROLL_PAUSE`

Time to wait after scrolling for new advertisements to load.

```python
SCROLL_PAUSE = 2
```

Increase this if the connection or Divar is slow to load new results.

### `MAX_SCROLLS`

Maximum number of scroll iterations:

```python
MAX_SCROLLS = 200
```

This prevents the scraper from running indefinitely.

### `STABLE_LIMIT`

Number of consecutive scrolls without discovering new advertisements before stopping:

```python
STABLE_LIMIT = 5
```

This provides a termination condition when there are no more results to collect.

## How It Works

The scraper uses Selenium to control Chrome and interact with Divar's dynamically rendered interface.

Advertisement cards are parsed from the rendered page using BeautifulSoup.

Each advertisement is stored using its URL as the key. This means the URL also acts as the deduplication key, preventing the same advertisement from being collected multiple times during scrolling.

The scraper also attempts to locate and click Divar's "load more advertisements" button after scrolling so that additional listings can be loaded.

## Limitations

- Requires a working Chrome or Chromium installation.
- Depends on Divar's current HTML structure and CSS selectors.
- Changes to Divar's frontend may require selector updates.
- Scraping speed depends on network conditions and configured delays.
- Advertisements removed from Divar may no longer be accessible.
- The current scraper extracts information from search-result cards rather than opening every advertisement individually.

## Responsible Use

This project is intended for personal research, experimentation, and data-processing purposes.

When using the scraper, respect Divar's terms of service, robots policies, rate limits, and applicable laws. Avoid unnecessarily aggressive request rates or behavior that could negatively affect the service.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
