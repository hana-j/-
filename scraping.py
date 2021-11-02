from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week3

driver = webdriver.Chrome('./chromedriver')

url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=강남구비건"

driver.get(url)
time.sleep(5)
for i in range(10):
    try:
        btn_more = driver.find_element_by_css_selector(".spnew_bf cmm_pg_next on > div > a")
        btn_more.click()
        time.sleep(5)
    except NoSuchElementException:
        break
req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

places = soup.select("ul.restaurant_list > div > div > li > div > a")

print(len(places))
for place in places:
    title = place.select_one("strong.box_module_title").text
    address = place.select_one("div.box_module_cont > div > div > div.mil_inner_spot > span.il_text").text
    category = place.select_one("div.box_module_cont > div > div > div.mil_inner_kind > span.il_text").text
    show, episode = place.select_one("div.box_module_cont > div > div > div.mil_inner_tv > span.il_text").text.rsplit(
        " ", 1)

    doc = {
        "title": title,
        "category": category,
        "call" : call,
        "address": address,

    }
    db.matjips.insert_one(doc)
