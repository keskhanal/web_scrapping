from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import config
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
from scribe.scribe import Scribe
import logging
from pymongo import MongoClient
from datetime import datetime
import hashlib
import util
import re

MARKETPLACE = 'investors_club'

class ScribeInvestorsClub(Scribe):

    # TODO is this okay?
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


def scrape_investors_club():
    listings = []
    # proxies=config.get_proxies()
    chrome_opts = Options()

    chrome_opts.add_argument('--headless')
    chrome_opts.add_argument('--no-sandbox')
    chrome_opts.add_argument('--disable-infobars')
    chrome_opts.add_argument('--disable-dev-shm-usage')
    chrome_opts.add_argument('--disable-gpu')
    chrome_opts.add_argument('--remote-debugging-port=9222')
    driver = webdriver.Chrome(options=chrome_opts)

    driver.get('https://investors.club/buy-online-business/')
    WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "redacted-card")))
    content = driver.page_source
    doc = BeautifulSoup(content, "html.parser")
    for item in doc.body.find_all("li", {"class": "redacted-card"}):
       fetched_data = scrape_each_page_data(driver=driver, url='https://investors.club'+item.a.get('href'))
       time.sleep(10)
       listings.append(fetched_data)
    driver.close()
    return listings

def navigate_single_page(driver, url):
    
    """
    search by URL
    """
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//section[@class='generalinfo']"))
    )
    time.sleep(2)

def scrape_each_page_data(driver, url):
    navigate_single_page(driver, url)
    investorclub_data = {}

    investor_soup = BeautifulSoup(driver.page_source, 'lxml')
    items_div = investor_soup.find_all('div', {'class': 'generalinfo__details__meta-item'})
    items_div_large = investor_soup.find_all('div', {'class': 'generalinfo__details__meta-item generalinfo__details__meta-item--large'})
    
    asking_price = investor_soup.find('div', {'class': 'generalinfo__details__top__price'}).find('div', {'class': 't-gamma t-primary'}).text
    monthly_revenue = investor_soup.find('div', {'class': 'generalinfo__details__top__averagerevenue'}).find('div', {'class': 't-text t-delta s-bottom--sml'}).text
    display_ad = items_div_large[0].find('p', {'class': 't-micro t-darktext'}).text
    business_type = items_div_large[1].find('p', {'class': 't-micro t-darktext'}).text
    
    # print(items_div)
    site_age = items_div[1].find('div', {'class': 't-darktext'}).text
    multiple = items_div[2].find('div', {'class': 't-darktext'}).text
    date_published = items_div[4].find('div', {'class': 't-darktext'}).text
    date_updated = items_div[5].find('div', {'class': 't-darktext'}).text
    
    seller_title = investor_soup.find('div', {'class': 'sellerinfo__heading'}).find('h1', {'class': 't-zeta s-bottom--lrg'}).text
    seller_description = investor_soup.find('div', {'class': 'sellerinfo__heading'}).find('p', {'class': 't-'}).text
    
    investorclub_data['price'] = int(re.sub(r'[\$,]', '', asking_price))
    investorclub_data['listing_url'] = url
    investorclub_data['summary'] = seller_description
    investorclub_data['title'] = seller_title
    investorclub_data['property_type'] = business_type
    investorclub_data['multiple'] = multiple
    investorclub_data['category'] = business_type


    investorclub_data['monthly_revenue'] = monthly_revenue
    investorclub_data['monitization_method'] = display_ad
    investorclub_data['site_age'] = site_age
    investorclub_data['date_published'] = date_published
    investorclub_data['date_updated'] = date_updated

    return investorclub_data


if __name__ == '__main__':

    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_{MARKETPLACE}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    all_recs = scrape_investors_club()
    #print(all_recs);
    scribe = ScribeInvestorsClub()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    c = mongoclient[config.dbconf['db']][config.dbconf['collection']]

    new_recs = util.flush_to_db(all_recs, scribe, c)