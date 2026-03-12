import time
import re
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By


def init_driver(geckodriver_path: str) -> webdriver.Firefox:
    """Инициализирует и возвращает headless Firefox webdriver"""
    service = Service(str(geckodriver_path.resolve()))
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return webdriver.Firefox(service=service, options=options)


def get_pagination_parameters() -> tuple[int, int]:
    """Запрашивает у пользователя параметры пагинации (show и skip)"""
    print("-------------------Скрейпинг Arxiv.org/cs--------------------")

    valid_show = {25, 50, 100, 250, 500, 1000, 2000}
    while True:
        try:
            show = int(input(
                "Укажите количество статей для отображения (25, 50, 100, 250, 500, 1000, 2000): "))
            if show not in valid_show:
                print(
                    "Недопустимое значение. Выберите одно из: 25, 50, 100, 250, 500, 1000, 2000")
                continue
            break
        except ValueError:
            print("Введите число")

    skip = int(
        input(f"Укажите номер статьи кратный {show} (с какой начинать): "))

    return show, skip


def build_arxiv_url(skip: int, show: int) -> str:
    """Формирует URL страницы списка arXiv с заданными параметрами пагинации"""
    return f"https://arxiv.org/list/cs/recent?skip={skip}&show={show}"


def parse_article_number(dt_element) -> str:
    """Извлекает arXiv ID из элемента dt"""
    id_elems = dt_element.find_elements(By.CSS_SELECTOR, "a[href^='/abs/']")
    if not id_elems:
        return ""
    return id_elems[0].text.strip().replace("arXiv:", "").strip()


def parse_article_data(dd_element) -> dict:
    """
    Извлекает основную информацию о статье из элемента dd
    Возвращает словарь с данными или значения по умолчанию при отсутствии
    """
    data = {
        "title": "Unknown",
        "authors": "Unknown",
        "subjects": "Unknown"
    }

    # Заголовок
    title_elems = dd_element.find_elements(
        By.CSS_SELECTOR, ".list-title.mathjax")
    if title_elems:
        data["title"] = title_elems[0].text.strip()

    # Авторы
    authors_elems = dd_element.find_elements(By.CSS_SELECTOR, ".list-authors")
    if authors_elems:
        text = authors_elems[0].text.strip()
        text = re.sub(r'^Authors?:\s*', '', text, flags=re.IGNORECASE).strip()
        data["authors"] = text

    # Предметы
    subjects_elems = dd_element.find_elements(
        By.CSS_SELECTOR, ".list-subjects")
    if subjects_elems:
        text = subjects_elems[0].text.strip()
        text = re.sub(r'^Subjects:\s*', '', text, flags=re.IGNORECASE).strip()
        data["subjects"] = text

    return data


def scrape_arxiv_page(driver, url: str) -> list[dict]:
    """Основная функция скрапинга одной страницы списка статей"""
    print(f"Загружаю страницу: {url}")
    driver.get(url)
    time.sleep(3.5)

    data = []

    try:
        dts = driver.find_elements(By.TAG_NAME, "dt")
        dds = driver.find_elements(By.TAG_NAME, "dd")

        if len(dts) != len(dds):
            print(f"Внимание: количество dt ({len(dts)}) ≠ dd ({len(dds)})")

        for dt, dd in zip(dts, dds):
            try:
                article_id = parse_article_number(dt)
                if not article_id:
                    continue

                article_data = parse_article_data(dd)

                record = {
                    "arxiv_id": article_id,
                    "title": article_data["title"],
                    "Authors": article_data["authors"],
                    "subjects": article_data["subjects"],
                    "url": f"https://arxiv.org/abs/{article_id}"
                }
                data.append(record)

            except Exception as e:
                print(f"Ошибка при обработке статьи: {e}")
                continue

    except Exception as e:
        print(f"Критическая ошибка при загрузке страницы: {e}")

    return data


def main():
    GECKODRIVER_PATH = Path(__file__).parent / "geckodriver"

    # 1. Получаем параметры от пользователя
    show, skip = get_pagination_parameters()

    # 2. Инициализация браузера
    driver = init_driver(GECKODRIVER_PATH)

    try:
        # 3. Формируем URL и собираем данные
        url = build_arxiv_url(skip, show)
        scraped_data = scrape_arxiv_page(driver, url)

        if not scraped_data:
            print("Не найдено ни одной статьи :(")
            return

        # 4. Преобразуем в DataFrame
        df = pd.DataFrame(scraped_data)
        print(f"\nСобрано статей: {len(df)}")
        print("\nПервые 10 строк:")
        print(df.head(10))

        # 5. Сохраняем результат
        output_file = f"arxiv_cs_skip{skip}_show{show}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\nДанные сохранены в: {output_file}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
