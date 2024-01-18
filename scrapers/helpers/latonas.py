import time
import hashlib
from bs4 import BeautifulSoup
from bs4 import NavigableString
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from scribe.scribe import Scribe

class ScribeLatonas(Scribe):
    def __init__(self):
        super().__init__()

    def get_id(self, rec):
        concatenated_fields = rec['listing_url']
        sha256 = hashlib.sha256()
        sha256.update(concatenated_fields.encode())
        return sha256.hexdigest()
    
    def marketplace(self):
        return "latonas"
    
    def get_name(self, rec):
        return rec['name']

    def get_description(self, rec):
        return rec['description']

    def get_marketplace_id(self, rec):
        return self.marketplace()

    def get_url(self, rec):
        return rec['listing_url']

    def get_askingprice(self, rec):
        return rec['asking_price'] if rec['asking_price'] else 0
    
    def get_niche(self, rec):
        return 'N/A'

    def get_multiple(self, rec):
        return 'N/A'

    def get_currency(self, rec):
        return "USD" 

    def get_type(self, rec):
        return 'N/A'


# driver setup
def driver_setup():
    chrome_options = Options()

    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    # proxies = get_proxies()
    # proxy_config = f"{proxies['https']}"
    # print(proxy_config)
    # chrome_options.add_argument(f'proxy-server={proxy_config}')  # Corrected line

    # Set up WebDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(120)
        
    except:
        driver.quit()
        time.sleep(4)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(120)
        
    finally:
        return driver 
    

# extract content of the page
def extract_content(driver, url):
    try:
        driver.get(url)
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')

        return soup
    except TimeoutException as e:
        print(f"{str(e)}")


def fetch_deal_links(deal_soup):
    all_deals = deal_soup.find('div', attrs={"class": "row ct-js-search-results ct-showProducts--list"})
    
    deal_links = []
    for deal_content in all_deals:
        if isinstance(deal_content, NavigableString):
            continue
    
        deal_link = deal_content.find('a')
        if deal_link:
            if deal_link['href'].startswith('https:'):
                deal_links.append(deal_link['href'])
            else:
                deal_links.append('https://www.latonas.com' + deal_link['href'])
    
    return deal_links


def extract_name(soup):
    """extract deal name
    Args:
        soup (str): deal content

    Returns:
        str: name of deal
    """
    try:
        deal_name = soup.find('h2', attrs={"style": "line-height: 30px !important; position: relative; top: 50%; transform: translateY(-80%)"}).text.strip()
    except:
        deal_name = 'name not available '
    return deal_name


def extract_desc(soup):
    try:
        description = soup.find_all('div', attrs={"class": "col-xs-12 col-md-6 ct-u-paddingTop20"})[0].find_all("p")
        description = description[1].get_text() if len(description) > 1 else None
    except:
        description = "Description not available"
    return description


def extract_revenue_sources(soup):  
    try:
        rev_sources = soup.find_all('div', attrs={"class": "col-xs-12 col-md-6 ct-u-paddingTop20"})[1].find_all("li")
        rev_sources = [rev_source.get_text() for rev_source in rev_sources]
    except:
        rev_sources = "revenue sources not available"
    return rev_sources


def extract_numbers(soup):  
    try:
        numbers = soup.find_all('span', attrs={"class": "numbers ct-fw-600"})
        revenue, profit, asking_price = [int(number.get_text()) for number in numbers]
    except:
        revenue, profit, asking_price = None, None, None
    return revenue, profit, asking_price
