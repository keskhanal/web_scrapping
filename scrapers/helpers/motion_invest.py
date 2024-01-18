import re
import time
import hashlib

from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from scribe.scribe import Scribe

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


def driver_setup():
    chrome_options = Options()

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--remote-debugging-port=9222')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        driver = webdriver.Chrome(options=chrome_options)
    
    # a fake user agent
    user_agent = UserAgent().random

    # Set a user agent
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    driver.implicitly_wait(20)
    
    return driver


def login(driver, site_username, site_password):
    """login by URL
    """
    login_url = "https://www.motioninvest.com/login-main/"
    driver.get(login_url)
    print("logged in successfully...")

    # Wait for the login form to be loaded
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Login Now']"))
    )
    
    # Locate the username and password input fields
    username_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#userlr56100e4'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#passwordlr56100e4'))
    )
    
    # Enter the username and password
    username_input.send_keys(site_username)
    password_input.send_keys(site_password)
    
    # Locate and click the submit button
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//form[@id='tp-user-loginlr56100e4']//button[@name='wp-submit']"))
    )
    submit_button.click()
    
    # Wait for a short period to allow for the login process to complete
    time.sleep(2)


def get_name(site)->str:
    name_section = site.find('section', {'class': 'elementor-section elementor-inner-section elementor-element elementor-element-7d1a574 elementor-section-boxed elementor-section-height-default elementor-section-height-default'})
    name = name_section.find('h1', {'class': 'elementor-heading-title elementor-size-default'}).text
    return name

def get_niche(site):
    niche_div = site.find('div', {'class': 'elementor-element elementor-element-c077b0c elementor-widget__width-auto Niche-main-area elementor-widget elementor-widget-icon-box'})
    niche = niche_div.find('p', {'class': 'elementor-icon-box-description'}).find('a').text
    return niche

def get_monthly_income(site):
    monthly_income_div = site.find('div', {'class': 'elementor-element elementor-element-379f18a elementor-widget__width-auto elementor-widget elementor-widget-icon-box'})
    monthly_income = monthly_income_div.find('p', {'class': 'elementor-icon-box-description'}).text
    return monthly_income

def get_asking_price(site):
    asking_price_div = site.find('div', {'class': 'elementor-element elementor-element-df65f2e elementor-widget__width-auto elementor-widget elementor-widget-icon-box'})
    asking_price = asking_price_div.find('span', {'class': 'woocommerce-Price-amount amount'}).text
    return asking_price

def get_multiple(site):
    multiple_div = site.find('div', {'class': 'elementor-element elementor-element-82e339f elementor-widget__width-auto elementor-widget elementor-widget-icon-box'})
    multiple = multiple_div.find('p', {'class': 'elementor-icon-box-description'}).text
    return multiple

def get_monitization(site):
    monitization_div = site.find('div', {'class': 'elementor-element elementor-element-15d48da elementor-widget__width-auto Niche-main-area elementor-widget elementor-widget-icon-box'})
    monitization = monitization_div.find('p', {'class': 'elementor-icon-box-description'}).text
    return monitization

def get_detail_url(site):
    detail_url = site.find('a',{'class':'elementor-button elementor-button-link elementor-size-md'}).get('href')
    return detail_url

def navigate_single_page(driver, listing_data):
    """search by URL
    """
    listing_url = listing_data["listing_url"]
    driver.get(listing_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='elementor-widget-container']"))
    )
    time.sleep(5)

    deal_soup = BeautifulSoup(driver.page_source, 'lxml')
    listing_title = listing_data['title'] + ' - ' + deal_soup.find('div', {'class': 'woocommerce-product-details__short-description'}).text
    listing_summary = (deal_soup.find('div', {'class': 'post-content-main-area'}).text).replace('\n', '')
    
    listing_data['title'] = listing_title
    listing_data['summary'] = listing_summary

    return listing_data


def scrape_motion_invest(driver, deals_url, site_username, site_password):
    login(driver, site_username, site_password)
    
    driver.get(deals_url)
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

    motioninvest_data = []
    for index, content in enumerate(content_list):
        name = get_name(content)
        niche = get_niche(content)
        monthly_income = get_monthly_income(content).replace('\n', '').replace('\t', '').replace('$', '')
        detail_url = get_detail_url(content)
        asking_price = int(re.sub(r'[\$,]', '', get_asking_price(content)))
        multiple = get_multiple(content).replace('\n', '').replace('\t', '').replace('$', '')
        monitization = get_monitization(content).replace('\n', '')
        
        site_data = {
            'title': name,
            'category': niche,
            'monthly_revenue': monthly_income,
            'listing_url': detail_url,
            'price': asking_price,
            'multiple': multiple,
            'monitization_method': monitization,
            'property_type': 'N/A'
        }
        motioninvest_data.append(site_data)

    return motioninvest_data