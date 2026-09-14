import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

city: str = "tehran"
search_item: str = "کفش"
URL: str = f"https://divar.ir/s/{city}"


def search_divar(url: str, query: str) -> webdriver.Chrome:
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    search_box = driver.find_element(By.NAME, "search")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)  # let results load
    return driver


if __name__ == "__main__":
    driver = search_divar(URL, search_item)
