import requests
import json
import logging
import time
import config
import hashlib
import pandas as pd
import util
from pymongo import MongoClient
from price_parser import Price
from scribe.scribe import Scribe
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

MARKETPLACE = 'fe_international'

class ScribeFeInternational(Scribe):

    def marketplace(self):
        return MARKETPLACE

    def get_id(self, rec):

        concatenated_fields = f"{self.marketplace()}{rec['listing_url']}"
        sha256 = hashlib.sha256()
        sha256.update(concatenated_fields.encode())
        return sha256.hexdigest()

    def get_name(self, rec):
        return rec['title']

    def get_description(self, rec):
        return rec['summary']

    def get_marketplace_id(self, rec):
        return self.marketplace()

    def get_url(self, rec):
        return rec['listing_url']

    def get_askingprice(self, rec):
        return rec['price'] if rec['price'] else 0

    def get_niche(self, rec):
        return rec['category']

    def get_multiple(self, rec):
        return rec["multiple"]

    def get_type(self, rec):
        return rec["property_type"]

    def get_currency(self, rec):
        return 'USD'
    
    def __init__(self):
        super().__init__()



def search(driver):
    """
    search by URL
    """
    driver.get("https://feinternational.com/buy-a-website/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[normalize-space()='Available']"))
    )
    time.sleep(2)

def scrape_data(driver):
    search(driver)
    feint_data = []
    
    available_button = driver.find_element(By.XPATH, "//a[normalize-space()='Available']")
    available_button.click()
    time.sleep(3)
    
    feint_soup = BeautifulSoup(driver.page_source, 'lxml')
    available_soup = feint_soup.find('div', {'class': 'tab available-list active'})
    cards_list = available_soup.find_all('div', {'class': 'card-item'})
    # print(cards_list)
    i = 0
    for item in cards_list:
        item_data = {}
        category_name = item.find('span', {'class': 'category'}).text
        title = item.find('h5').text
        
        details_link = item.find('a').get("href")
        driver.get(details_link)
        item_soup = BeautifulSoup(driver.page_source, 'lxml')
        main_benefits = item_soup.find('ul', {'class': 'main-benefits'}).text
        description = item_soup.find('p', {'class': 'listing_description'}).text
        
        item_data['category'] = category_name
        item_data['title'] = title
        quick_info = main_benefits.replace('\n', '').replace('\t', '')
        item_data['summary'] = description + quick_info
        item_data['listing_url'] = details_link
        item_data['price'] = 0
        item_data['multiple'] = 'N/A'
        item_data['property_type'] = category_name
        feint_data.append(item_data)
        print(f"Business {title[:20]}... has been scrapped successfully!")
        i += 1
    driver.close()
    return feint_data

def main():
    
    chrome_opts = Options()

    chrome_opts.add_argument('--headless')
    chrome_opts.add_argument('--no-sandbox')
    chrome_opts.add_argument('--disable-infobars')
    chrome_opts.add_argument('--disable-dev-shm-usage')
    chrome_opts.add_argument('--disable-gpu')
    chrome_opts.add_argument('--remote-debugging-port=9222')
    proxies = config.get_proxies()
    proxy_config = f"{proxies['https']}"
    chrome_opts.add_argument = f'proxy-server={proxy_config}'

    chrome_opts.add_argument="user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"
    driver = webdriver.Chrome(options=chrome_opts)
    driver.set_page_load_timeout(120)
    return scrape_data(driver)

if __name__ == '__main__':

    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_{MARKETPLACE}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    #TODO::change to config file changes
    all_recs = main()
    scribe = ScribeFeInternational()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    c = mongoclient[config.dbconf['db']][config.dbconf['collection']]

    new_recs = util.flush_to_db(all_recs, scribe, c)
