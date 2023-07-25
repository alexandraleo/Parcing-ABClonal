from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import lxml
import time
from datetime import datetime
from random import randrange
import csv

SITE_URL = "https://eu.abclonal.com/"
ARTS = "a4923, a15100"
# ARTS = ["a4923"]

def get_art_page(driver, art):
    driver.implicitly_wait(10)

    try:
        time.sleep(2)
        search_input = driver.find_elements(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input")[0].send_keys(art + Keys.ENTER)
        time.sleep(2)
        return driver.page_source
    except:
        print('No search input, art ' + art)

def get_soup(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        return soup
    except:
        print('No soup!')

def get_dilut_ihc(diluts):
    if "IHC-P" in diluts:
        ihc_dilut = diluts[diluts.find("IHC-P") + 6:diluts.find("\n")]
        print(ihc_dilut)
        ihc_dilut_text = "иммуногистохимии на парафиновых срезах (рекомендуемое разведение " + ihc_dilut.strip() + ")"
    elif "IHC" in diluts:
        ihc_dilut = diluts[diluts.find("IHC")+4:diluts.find("\n")]
        print(ihc_dilut)
        ihc_dilut_text = "иммуногистохимии (рекомендуемое разведение " + ihc_dilut.strip() + ")"
    else:
        ihc_dilut_text = "иммуногистохимии"

    return ihc_dilut_text

def get_art_structure(soup, art):
    clonality_dict = {
        "mAb": "monoclonal",
        "pAb": "polyclonal"
    }

    reactivity_dict = {
        "Human": "человек",
        "Mouse": "мышь",
        "Rat": "крыса",
        "Monkey": "обезьяна"
    }
    applications_dict = {
        "WB": "вестерн-блоттинга",
        "IHC": "иммуногистохимии",
        "IHC-P": "иммуногистохимии на парафиновых срезах",
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
    #  TODO переписать ифы на аналоги с контейнерами, чтобы не ломалось на некст_сиблинг
    discont = soup.find("h1", class_="search-header-title")
    if discont:
            cat_no = art,
            volumes = []
            volume_units = []
            antigen = ""
            host = ""
            clonality_en = ""
            clone = ""
            text = ""
            appl_ru = []
            reactivity_ru = []
            title = ""
            appl_list = []
            dilutions = []
            storage = ""
            storage_buff = ""
            synonyms = ""
            prices = []
    else:
        cat_no = soup.find("th", string="Catalog No.").find_next_sibling("td").get_text().strip()
        if not cat_no:
            cat_no = art
        title = soup.find("th", string="Product name").find_next_sibling("td").get_text().strip()
        if not title:
            title = ""
        host = soup.find("th", string="Host species").find_next_sibling("td").get_text().strip()
        if not host:
            host = ""
        antigen = title[:title.find(host)].strip()
        if not antigen:
            antigen = ""
        clonality = title.split(" ")[-1]
        if not clonality:
            clonality = ""
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
            if "IHC-P" in txt:
                ihc_dilut = txt[txt.find("IHC-P") + 6 :]
                ihc_dilut_text = "иммуногистохимии на парафиновых срезах (рекомендуемое разведение " + ihc_dilut + ")"
                applications_dict["IHC-P"] = ihc_dilut_text
            elif "IHC" in txt:
                ihc_dilut = txt[txt.find("IHC") + 4 :]
                ihc_dilut_text = "иммуногистохимии (рекомендуемое разведение " + ihc_dilut + ")"
                applications_dict["IHC"] = ihc_dilut_text

        dilutions = "\n".join(dilus)

        appls = soup.find("th", string="Tested applications").find_next_sibling("td").find_all("a")
        if not appls:
            appls = ""
        appl_list = []
        for appl in appls:
            if appl["data-label"] != "none":
                appl_txt = appl["data-label"].strip()
                appl_list.append(appl_txt)


        reactivity = soup.find("th", string="Reactivity").find_next_sibling("td").get_text().strip()
        if not reactivity:
            reactivity = ""
        reactivity_ru = ", ".join([reactivity_dict.get(w.strip(), w.strip()) for w in reactivity.split(", ")])
        appl_ru = ", ".join([applications_dict.get(w.strip(), w.strip()) for w in appl_list])
        text = dilutions + "\n" + reactivity

        storage_buff = soup.find("th", string="Storage buffer").find_next_sibling("td").get_text().strip()
        if not storage_buff:
            storage_buff = ""
        storage = soup.find("th", string="Storage buffer").find_next_sibling("td").get_text().strip()
        if not storage:
            storage = ""
        synonyms = soup.find("th", string="Synonyms").find_next_sibling("td").get_text().strip()
        if not synonyms:
            synonyms = ""

        volumes_con = soup.find("select", class_="selectsize form-control")
        if volumes_con:
            volumes_opt = volumes_con.find_all("option")
            volumes = [volume["data-size"].split(" ")[0] for volume in volumes_opt]

            volume_units = [volume["data-size"].split(" ")[1].replace("μ", "u").lower() for volume in volumes_opt]
            prices = [price["data-price"] for price in volumes_opt]

            volume_20 = soup.find("a", string="Hot 20 μL Inquiry")
            if volume_20:
                volumes.insert(0, "20")
                volume_units.insert(0, "ul")
                prices.insert(0, "?")
        else:
            volumes = []
            volume_units = []
            prices = []
# TODO conjugation

    dict_list = []
    if len(volumes) > 0:
        for i in range(0, len(volumes)):
            dict_art = {
                "Article": cat_no,
                "Volume": volumes[i],
                "Volume units": volume_units[i],
                "Antigen": antigen,
                "Host": host,
                "Clonality": clonality_en,
                "Clone_num": clone,
                "Text": text,
                "Applications_ru": appl_ru,
                "Reactivity": reactivity_ru,
                "Conjugation": "",
                "Title": title,
                "Applications": appl_list,
                "Dilutions": dilutions,
                # "Form": form,
                "Storage instructions": storage,
                "Storage buffer": storage_buff,
                "Synonyms": synonyms,
                "Concentration": "",
                "Price": prices[i],
            }
            dict_list.append(dict_art)
    else:
            dict_art = {
                "Article": cat_no,
                "Volume": volumes,
                "Volume units": volume_units,
                "Antigen": antigen,
                "Host": host,
                "Clonality": clonality_en,
                "Clone_num": clone,
                "Text": text,
                "Applications_ru": appl_ru,
                "Reactivity": reactivity_ru,
                "Conjugation": "",
                "Title": title,
                "Applications": appl_list,
                "Dilutions": dilutions,
                # "Form": form,
                "Storage instructions": storage,
                "Storage buffer": storage_buff,
                "Synonyms": synonyms,
                "Concentration": "",
                "Price": prices,
            }
            dict_list.append(dict_art)
    return dict_list

def write_csv(result):
    date = datetime.now().strftime('%d.%m.%Y_%H.%M')

    with open("data-abc\\ABClonal_{}.csv".format(date), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)

def get_articles_list():
    print("Введите список артикулов:")
    articles = [art.strip() for art in input().split(",")]
    return articles

service = Service("C:\\Users\\Public\\Parsing programs\\chromedriver.exe")
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
        art_info = get_art_structure(soup, art)
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
