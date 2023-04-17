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

def get_art_page(driver, art):
    driver.implicitly_wait(10)
    # driver.get(url)
    # print(len(driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")))
    try:
        time.sleep(2)
        search_input = driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")[0].send_keys(art + Keys.ENTER)
        time.sleep(2)
        return driver.page_source
    except:
        print('No search input, art ' + art)
    # TODO в зависимости от хэдлесс и размера окна, то 0, то 1 элемент. If-else? Попробовать другой набор классов в качестве пути

def get_soup(html):
    try:
        soup = BeautifulSoup(html, "html5lib")
        return soup
    except:
        print('No soup!')

def get_art_structure(soup):
    # soup = get_soup(url, art)
    # if not soup:
    #     print("No soup!")

    # table_ths = soup.find_all("th")
    # tbl_ths = [th.get_text(" ") for th in table_ths]
    # table_tds = soup.find_all("td")
    # tbl_tds = [td.get_text(" ") for td in table_tds]
    # dict_art = dict(zip(tbl_ths, tbl_tds))
    # catpos = soup.find("h3", class_="catpos")
    # dict_art["Catalog position"] = catpos.get_text(" ")
    clonality_dict = {
        "mAb": "monoclonal",
        "pAb": "polyclonal"
    }

    reactivity_dict = {
        "Human": "человек",
        "Mouse": "мышь",
        "Rat": "крыса"
    }

    applications_dict = {
        "WB": "вестерн-блоттинга",
        "IHC": "иммуногистохимии",
        "IF/ICC": "иммунофлуоресцентного/иммуноцитохимического анализа",
        "IP": "иммунопреципитации",
        "ChIP": "иммунопреципитации хроматина",
        "ChIP-seq": "иммунопреципитации хроматина и высокоэффективного секвенирования",
        "RIP": "иммунопреципитации РНК",
        "FC": "проточной цитометрии",
        "FC(Intra)": "проточной цитометрии (Intra)",
        "ELISA": "ИФА",
        "MeDIP": "иммунопреципитации метилированной ДНК",
        "Nucleotide Array": "исследования нуклеотидных последовательностей",
        "DB": "дот-блоттинга",
        "FACS": "сортировки клеток, активируемых флуоресценцией",
        "CoIP": "коиммунопреципитации",
        "CUT&Tag": "CUT&Tag секвенирование",
        "meRIP": "иммунопреципитации метилированной РНК"
    }
    cat_no = soup.find("th", string="Catalog No.").find_next_sibling("td").get_text().strip()
    title = soup.find("th", string="Product name").find_next_sibling("td").get_text().strip()
    host = soup.find("th", string="Host species").find_next_sibling("td").get_text().strip()
    antigen = title[:title.find(host)]
    clonality = title.split(" ")[-1]
    clonality_en = clonality_dict.get(clonality, clonality)

    try:
        clone = soup.find("th", string="CloneNo.").find_next_sibling("td").get_text().strip()
    except:
        clone = ""
    dilus_con = soup.find("th", string="Recommended dilution").find_next_sibling("td").find("ul").find_all("li")
    dilus = []
    for li in dilus_con:
        txt = li.get_text().strip()
        dilus.append(txt)
    # print(dilus)
    dilutions = "\n".join(dilus)
    appls = soup.find("th", string="Tested applications").find_next_sibling("td").find_all("a")
    appl_list = []
    for appl in appls:
        if appl["data-label"] != "none":
            appl_txt = appl["data-label"].strip()
            appl_list.append(appl_txt)

    reactivity = soup.find("th", string="Reactivity").find_next_sibling("td").get_text().strip()
    reactivity_ru = ", ".join([reactivity_dict.get(w.strip(), "") for w in reactivity.split(", ")])
    appl_ru = ", ".join([applications_dict.get(w.strip(), "") for w in appl_list])
    text = dilutions + "\n" + reactivity

    storage_buff = soup.find("th", string="Storage buffer").find_next_sibling("td").get_text().strip()
    storage = soup.find("th", string="Storage buffer").find_next_sibling("td").get_text().strip()

    # title = soup.find("h1", itemprop="name").get_text().strip()
    volumes_con = soup.find("select", class_="selectsize form-control")
    volumes_opt = volumes_con.find_all("option")
    volumes = [volume["data-size"].split(" ")[0] for volume in volumes_opt]
    volume_units = [volume["data-size"].split(" ")[1].replace("μ", "u") for volume in volumes_opt]
    # print(volumes)
    prices = [price["data-price"] for price in volumes_opt]
    # print(prices)

    dict_list = []
    for i in range(0, len(volumes)):
        dict_art = {
            # "Article": art,
            "Article": cat_no,
            # "CatNo": cat_no,
            "Volume": volumes[i],
            "Volume units": volume_units[i],
            "Antigen": antigen,
            "Host": host,
            "Clonality": clonality_en,
            "Clone_num": clone,
            "Text": text,
            "Applications_ru": appl_ru,
            "Reactivity": reactivity_ru,
            "Title": title,
            "Applications": appl_list,
            "Dilutions": dilutions,
            # # "Form": form,
            "Conjugation": "",
            "Storage instructions": storage,
            "Storage buffer": storage_buff,
            "Concentration": "",
            "Price": prices[i],
        }
        dict_list.append(dict_art)
    # print(dict_list)
    return dict_list

def write_csv(result):
    date = datetime.now().strftime('%d.%m.%Y_%H.%M')
    # columns = set(i for d in result for i in d)
    with open("data\\ABClonal_{}.csv".format(date), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)

def get_articles_list():
    print("Введите список артикулов:")
    articles = [str(art) for art in input().split(",")]
    return articles

service = Service("C:\\Users\\shurshun_4ik\\AppData\\Local\\Programs\\Python\\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--disable-infobars")
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
driver.get(SITE_URL)
print("Main site opened")
time.sleep(3)

try:
    arts = get_articles_list()
    start_time = datetime.now()
    result = []
    counter = 0
    for art in arts:
        counter += 1
        print(counter, " art No ", art)
        src = get_art_page(driver, art)
        soup = get_soup(src)
        art_info = get_art_structure(soup)
        result.extend(art_info)
    # result_parse = main(SITE_URL, articles)
    # print(result_parse)
    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)
    write_csv(result)

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()

# TODO try pool for 3 browsers with if on len(arts)
