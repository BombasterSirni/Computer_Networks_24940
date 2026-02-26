import time
import re

import pandas as pd
from selenium import webdriver
# Для работы с gecko вебдрайвером firefox
from selenium.webdriver.firefox.service import Service
# Для поиска объекта на странице с помощью выбранной стратегии из By
from selenium.webdriver.common.by import By


webdriver_path = '/home/covo43k/study/year_2/comp_networks/task3/geckodriver'
service = Service(webdriver_path)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(service=service, options=options)

data = []

print("-------------------Скрейпинг Arxiv.org/cs--------------------")
show = int(input(
    "Укажите количество статей для отображения (25, 50, 100, 250, 500, 1000, 2000): "))
skip = int(input(
    f"Укажите номер статьи кратный {show},  (номер статьи, с которой отображаются {show} статей): "))


arxiv_page_url = f"https://arxiv.org/list/cs/recent?skip={skip}&show={show}"
driver.get(arxiv_page_url)
time.sleep(3.5)

# Номера статей отмечены тегом dt
dts = driver.find_elements(By.TAG_NAME, "dt")
# Превью статьи (название, авторы, предмет статьи) отмечены тегом dd
dds = driver.find_elements(By.TAG_NAME, "dd")

for (article_num_container, article_desc_container) in zip(dts, dds):
    try:

        # Парсинг номеров статей
        article_id = ""
        id_elem = article_num_container.find_elements(
            By.CSS_SELECTOR, "a[href^='/abs/']")
        if id_elem:
            article_id_text = id_elem[0].text.strip()
            article_id = article_id_text.replace("arXiv:", "").strip()

        # Парсинг заголовка
        article_title = ""
        title_elem = article_desc_container.find_elements(
            By.CSS_SELECTOR, ".list-title.mathjax")
        if title_elem:
            article_title = title_elem[0].text.strip()
        else:
            article_title = "Unknown"

        # Парсинг Авторов
        article_authors = ""
        authors_elem = article_desc_container.find_elements(
            By.CSS_SELECTOR, ".list-authors")
        if authors_elem:
            article_authors = authors_elem[0].text.strip()
            article_authors = re.sub(
                r'^Authors?:\s*', '', article_authors, flags=re.IGNORECASE).strip()
        else:
            article_authors = "Unknown"

        # Парсинг предмета статьи
        article_subjects = ""
        article_subjects_elem = article_desc_container.find_elements(
            By.CSS_SELECTOR, ".list-subjects")
        if article_subjects_elem:
            article_subjects = article_subjects_elem[0].text.strip()
            article_subjects = re.sub(
                r'^Subjects:\s*', '', article_subjects, flags=re.IGNORECASE).strip()
        else:
            article_subjects = "Unknown"

        data.append({
            "arxiv_id": article_id,
            "title": article_title,
            "Authors": article_authors,
            "subjects": article_subjects,
            "url": f"https://arxiv.org/abs/{article_id}" if article_id else ""
        })

    except Exception as e:
        print(f"Ошибка при обработке одной статьи: {e}")
        continue

driver.quit()


if data:
    df = pd.DataFrame(data)
    print(f"Собрано статей: {len(df)}")
    print(f"Вот данные первых 10 статей:\n", df.head(10))

    output_path = f"arxiv_cs_skip{skip}_show{show}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Данные статей по CS загружены в {output_path}")

else:
    print("Не найдено ни одной статьи :(")
