import util
import config
import logging
from datetime import datetime
from pymongo import MongoClient

from helpers.latonas import *

def main(driver, page:int)->list:
    deal_links = [] 
    url = f"https://latonas.com/listings/?page={page}&result_sorting_quantity=20&result_sorting_order=&broker=any&price_range=any&revenue_range=any&searchTags=&unique_range=any&profit_range=any&&&location=any"
    deal_soup = extract_content(driver, url)
    deal_links = fetch_deal_links(deal_soup)

    latonas_data = []
    for deal_url in deal_links:
        deal_content = extract_content(driver, deal_url)
        deal_data = {
            "listing_url":deal_url,
            "name": extract_name(deal_content),
            "annual_revenue": extract_numbers(deal_content)[0],
            "asking_price": extract_numbers(deal_content)[2],
            "description": extract_desc(deal_content),
            "monetization_type": extract_revenue_sources(deal_content),
            "annual_profit": extract_numbers(deal_content)[1]
        }
        latonas_data.append(deal_data)
    
    return latonas_data

if __name__ == '__main__':
    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_latonas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    driver = driver_setup()
    scribe = ScribeLatonas()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    
    for page in range(1,4):
        latonas_data = main(driver, page)

        c = mongoclient[config.dbconf['db']][config.dbconf['collection']]
        new_recs = util.flush_to_db(latonas_data, scribe, c)