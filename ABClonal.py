from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv

options = webdriver.ChromeOptions()

binary_yandex_driver_file = 'G:\\Мой диск\\Colab Notebooks\\yadriver\\yandexdriver.exe' # path to YandexDriver
SITE_URL = "https://eu.abclonal.com/"
ARTS = ["a4923", "a15100"]

# TODO Разобраться с хэдлесс режимом
# TODO stop printing, put the date in title



print("Введите список артикулов:")
articles = [str(art) for art in input().split(",")]


def get_source_html(url, art):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(binary_yandex_driver_file, options=chrome_options)
    driver.get(url)
    time.sleep(2)

    search_input = driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")[1].send_keys(art + Keys.ENTER)
    return driver.page_source

def get_soup(url, art):
    html = get_source_html(url, art)
    if not html: return
    soup = BeautifulSoup(html, "html5lib")
    # print(soup)
    return soup

def get_art_structure(url, art):
    soup = get_soup(url, art)
    if not soup:
        print("No soup!")
    # art_all_info = soup.select("div.container-fluid.product-detail")
    # art_info = {}
    # art_info['title'] = soup.select_one("h1").get_text()
    table_ths = soup.find_all("th")
    for th in table_ths:
        th = str(th)[5:-5]
    tbl_ths = [str(th)[4:-5] for th in table_ths]
    table_tds = soup.find_all("td")
    tbl_tds = [str(td)[4:-5] for td in table_tds]
    dict_art = dict(zip(tbl_ths, tbl_tds))
    # print(dict_art)
    return dict_art

# art_div = get_art_structure(SITE_URL, ARTS)
# print(art_div)

def write_csv(result):
    date = date.today() # TODO Check it, Does it work?..
    with open("ABClonal_{}.csv".format(date), "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)

def main(url, arts):
    result = []
    counter = 0
    for art in arts:
        time.sleep(1)
        art_structure = get_art_structure(url, art)
        counter += 1
        print(counter)
        result.append(art_structure)
    return result

result_parce = main(SITE_URL, articles)
# print(result_parce)

write_csv(result_parce)
