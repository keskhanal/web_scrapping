import re
import sys
import time
import util
import config
import hashlib
import logging
from datetime import datetime
from pymongo import MongoClient
from scribe.scribe import Scribe

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

MARKETPLACE = 'motion_invest'

class ScribeMotionInvest(Scribe):
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


# from selenium import webdriver
# driver = webdriver.Chrome(ChromeDriverManager().install())

def scrape_motion_invest():
    site_username = 'subashb@termaproject.com'
    site_password = 'motioninvest123!@#'
    
    # proxies=config.get_proxies()
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

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_opts)
    driver.set_page_load_timeout(120)
    return scrape_data(driver, site_username, site_password)

def login(driver, site_username, site_password):
    """
    login by URL
    """
    driver.get("https://www.motioninvest.com/login-main/")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Login Now']"))
    )
    username_input = driver.find_element(By.CSS_SELECTOR, '#userlr56100e4')
    password_input = driver.find_element(By.CSS_SELECTOR, '#passwordlr56100e4')
    username_input.send_keys(site_username)
    password_input.send_keys(site_password)
    
    submit_button = driver.find_element(By.XPATH, "//form[@id='tp-user-loginlr56100e4']//button[@name='wp-submit']")
    
    print(submit_button.click())
    time.sleep(2)


def scrape_data(driver, site_username, site_password):
    # login to site
    login(driver, site_username, site_password)
    motioninvest_data = []
    url = "https://www.motioninvest.com/sites-available/"
    driver.get(url)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")  
    loader_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.jet-listing-grid__loader-spinner')))
    
    while True:
        current_height = driver.execute_script('return document.body.scrollHeight')
        
        actions = ActionChains(driver)
        actions.move_to_element(loader_element).perform()
        
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.jet-listing-grid__loader-spinner')))
        
        new_height = driver.execute_script('return document.body.scrollHeight')

        # Check scroll height, if not equal then there will be no more content loaded...
        if new_height == current_height:
            break
        
    soup = BeautifulSoup(driver.page_source, 'lxml')
    content_list = soup.find('div', {'class': 'jet-listing-grid__items grid-col-desk-1 grid-col-tablet-1 grid-col-mobile-1 jet-listing-grid--985'})
    i = 0
    for site in content_list:
        site_data = {}
        name = site.find('section', {'class': 'elementor-section elementor-inner-section elementor-element elementor-element-7d1a574 elementor-section-boxed elementor-section-height-default elementor-section-height-default'}).find('h1', {'class': 'elementor-heading-title elementor-size-default'}).text
        niche = site.find('div', {'class': 'elementor-element elementor-element-c077b0c elementor-widget__width-auto Niche-main-area elementor-view-default elementor-vertical-align-top elementor-widget elementor-widget-icon-box'}).find('p', {'class': 'elementor-icon-box-description'}).find('a').text
        monthly_income = site.find('div', {'class': 'elementor-element elementor-element-379f18a elementor-widget__width-auto elementor-view-default elementor-vertical-align-top elementor-widget elementor-widget-icon-box'}).find('p', {'class': 'elementor-icon-box-description'}).text
        asking_price = site.find('div', {'class': 'elementor-element elementor-element-df65f2e elementor-widget__width-auto elementor-view-default elementor-vertical-align-top elementor-widget elementor-widget-icon-box'}).find('span', {'class': 'woocommerce-Price-amount amount'}).text
        multiple = site.find('div', {'class': 'elementor-element elementor-element-82e339f elementor-widget__width-auto elementor-view-default elementor-vertical-align-top elementor-widget elementor-widget-icon-box'}).find('p', {'class': 'elementor-icon-box-description'}).text
        monitization = site.find('div', {'class': 'elementor-element elementor-element-15d48da elementor-widget__width-auto Niche-main-area elementor-view-default elementor-vertical-align-top elementor-widget elementor-widget-icon-box'}).find('p', {'class': 'elementor-icon-box-description'}).text
        detail_url = site.find('a',{'class':'elementor-button-link elementor-button elementor-size-md'}).get('href')
        # Append all data to dictionary
        site_data['title'] = name
        site_data['category'] = niche
        site_data['monthly_revenue'] = monthly_income.replace('\n', '').replace('\t', '').replace('$', '')
        site_data['listing_url'] = detail_url
        site_data['price'] = int(re.sub(r'[\$,]', '', asking_price))
        site_data['multiple'] = multiple.replace('\n', '').replace('\t', '').replace('$', '')
        site_data['monitization_method'] = monitization.replace('\n', '')
        site_data['property_type'] = 'N/A'

        motioninvest_data.append(site_data)
        print(f"Item-{i} scraped successfully!!")
        i += 1

    for detail_site in motioninvest_data:
        navigate_single_page(driver, detail_site['listing_url'])
        motion_soup = BeautifulSoup(driver.page_source, 'lxml')

        detail_site['title'] = detail_site['title'] + ' - ' +motion_soup.find('div', {'class': 'woocommerce-product-details__short-description'}).text
        detail_site['summary'] = (motion_soup.find('div', {'class': 'post-content-main-area'}).text).replace('\n', '')


    print("Scraping completed successfully!!!")
    driver.close()
    return motioninvest_data


def navigate_single_page(driver, url):
    """search by URL
    """
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='elementor-widget-container']"))
    )
    time.sleep(2)

if __name__ == '__main__':

    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_{MARKETPLACE}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    all_recs = scrape_motion_invest()
    scribe = ScribeMotionInvest()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    c = mongoclient[config.dbconf['db']][config.dbconf['collection']]

    #new_recs = util.flush_to_db(all_recs, scribe, c)