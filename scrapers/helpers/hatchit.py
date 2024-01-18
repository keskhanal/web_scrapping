import time
import hashlib
from price_parser import Price

from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
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
        return "hatchit"
    
    def get_name(self, rec):
        return rec['Title']

    def get_description(self, rec):
        return rec['Description']

    def get_marketplace_id(self, rec):
        return self.marketplace()

    def get_url(self, rec):
        return rec['listing_url']

    def get_askingprice(self, rec):
        asking_price = rec["Price"]
        if asking_price:
            asking_price = Price.fromstring(asking_price)
            amount = asking_price.amount_text
        else:
            amount = 'N/A'
        return amount
    
    def get_niche(self, rec):
        return 'N/A'

    def get_multiple(self, rec):
        return 'N/A'

    def get_currency(self, rec):
        asking_price = rec["Price"]
        asking_price = Price.fromstring(asking_price)
        currency = int(asking_price.currency)
        
        return currency 

    def get_type(self, rec):
        return rec["Monetization"]


def chrome_driver_setup():
    chrome_options = Options()

    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Add a fake user agent
    user_agent = UserAgent().random
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    # proxies = get_proxies()
    # proxy_config = f"{proxies['https']}"
    # print(proxy_config)
    # chrome_options.add_argument(f'proxy-server={proxy_config}')  # Corrected line

    # Set up WebDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        driver = webdriver.Chrome(options=chrome_options)
        
    finally:
        driver.set_page_load_timeout(120)
        return driver 


# extract content of the page
def extract_content(driver, url):
    try:
        driver.get(url)

        # element to be present on the page
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'w2dc-table w2dc-dashboard-listings w2dc-table-striped bm-table-search'))
        WebDriverWait(driver, 20).until(element_present)
    
        # proceed to extract content
        time.sleep(10)
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # driver.quit()
        return soup
    
    except TimeoutException as e:
        print(f"Timed out waiting for page to load: {str(e)}")


def get_table_data(deal_soup):
    table_data = deal_soup.find('table', {'class': 'w2dc-table w2dc-dashboard-listings w2dc-table-striped bm-table-search'})
    rows = table_data.find_all('tr')

    # Extract column headers from the first row
    headers = [header.text.strip() for header in rows[0].find_all('th')]
    headers.append("listing_url")
    
    deal_data = []
    for row in rows[1:]:  # Skip the first row as it is the header
        row_data = {}
        cells = row.find_all('td')
        
        for index, cell in enumerate(cells):
            header = headers[index] if index < len(headers) else f"Column {index}"
            cell_text = ''.join(cell.find_all(string=True, recursive=False)).strip()
            row_data[header] = cell_text
            
            # Check if the cell has the class 'w2dc-td-listing-title' to extract the URL
            if 'w2dc-td-listing-title' in cell.get('class', []):
                anchor_tag = cell.find('a', href=True)
                if anchor_tag and 'href' in anchor_tag.attrs:
                    row_data['listing_url'] = anchor_tag.attrs['href']
                
                # Extract the title text
                row_data['Title'] = anchor_tag.get_text(strip=True)
        
        if row_data.get('Title'):
            deal_data.append(row_data)  # Add the row data to table data

    return deal_data