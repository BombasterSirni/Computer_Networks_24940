import time
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By


def parse_arxiv(url: str):
    """Парсит arXiv. geckodriver установлен в /usr/local/bin внутри контейнера"""
    data = []

    #
    service = Service("/usr/local/bin/geckodriver")
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Firefox(service=service, options=options)

    try:
        print(f"Открываю: {url}")
        driver.get(url)
        time.sleep(4)

        dts = driver.find_elements(By.TAG_NAME, "dt")
        dds = driver.find_elements(By.TAG_NAME, "dd")

        for dt, dd in zip(dts, dds):
            try:
                id_elem = dt.find_elements(By.CSS_SELECTOR, "a[href^='/abs/']")
                article_id = id_elem[0].text.strip().replace("arXiv:", "").strip() if id_elem else ""
                if not article_id:
                    continue

                title = dd.find_elements(By.CSS_SELECTOR, ".list-title.mathjax")
                title = title[0].text.strip() if title else "Unknown"

                authors = dd.find_elements(By.CSS_SELECTOR, ".list-authors")
                authors = authors[0].text.strip() if authors else "Unknown"
                authors = re.sub(r'^Authors?:\s*', '', authors, flags=re.IGNORECASE).strip()

                subjects = dd.find_elements(By.CSS_SELECTOR, ".list-subjects")
                subjects = subjects[0].text.strip() if subjects else "Unknown"
                subjects = re.sub(r'^Subjects:\s*', '', subjects, flags=re.IGNORECASE).strip()

                data.append({
                    "arxiv_id": article_id,
                    "title": title,
                    "authors": authors,
                    "subjects": subjects,
                    "url": f"https://arxiv.org/abs/{article_id}"
                })
            except Exception as e:
                print(f"Ошибка статьи: {e}")
                continue
    finally:
        driver.quit()

    print(f"Спарсено: {len(data)} статей")
    return data