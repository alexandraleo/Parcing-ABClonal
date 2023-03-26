from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import html5lib
import time
from datetime import datetime
from random import randrange
import csv

SITE_URL = "https://eu.abclonal.com/"
ARTS = "a4923, a15100"
# ARTS = ["a4923"]

service = Service('G:\\Мой диск\\Colab Notebooks\\Webdrivers\\chromedriver.exe')
options = webdriver.ChromeOptions()

options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-infobars')
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

def get_source_html(url, art):
    driver.implicitly_wait(10)
    driver.get(url)
    # print(len(driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")))
    search_input = driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")[0].send_keys(art + Keys.ENTER)
    # TODO в зависимости от хэдлесс и размера окна, то 0, то 1 элемент. If-else? Message: element not interactable
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

    table_ths = soup.find_all("th")
    tbl_ths = [th.get_text(" ") for th in table_ths]
    table_tds = soup.find_all("td")
    tbl_tds = [td.get_text(" ") for td in table_tds]
    dict_art = dict(zip(tbl_ths, tbl_tds))
    catpos = soup.find("h3", class_="catpos")
    dict_art["Catalog position"] = catpos.get_text(" ")
    return dict_art

def write_csv(result):
    date = datetime.now().strftime('%d.%m.%Y_%H.%M')
    columns = set(i for d in result for i in d)
    with open("ABClonal_{}.csv".format(date), "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(result)

def main(url, arts):
    result = []
    counter = 0
    for art in arts:
        # time.sleep(randrange(3, 5))
        art_structure = get_art_structure(url, art)
        counter += 1
        print(counter)
        result.append(art_structure)
    return result

try:
    print("Введите список артикулов:")
    articles = [str(art) for art in input().split(",")]
    start_time = datetime.now()
    result_parse = main(SITE_URL, articles)
    # print(result_parse)
    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)
    write_csv(result_parse)

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()

# TODO try pool for 3 browsers with if on len(arts)
