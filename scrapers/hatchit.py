import util
import config
import logging
from datetime import datetime
from pymongo import MongoClient

from helpers.hatchit import *

def main(driver, page:int)->list:
    url = f"https://www.hatchit.us/search-businesses-for-sale/page/{page}/"
    deal_soup = extract_content(driver, url)
    deal_data = get_table_data(deal_soup)
    
    return deal_data

if __name__ == '__main__':
    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_latonas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    driver = chrome_driver_setup()
    scribe = ScribeLatonas()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    
    for page in range(1,12):
        hitchat_deal_data = main(driver, page)

        c = mongoclient[config.dbconf['db']][config.dbconf['collection']]
        new_recs = util.flush_to_db(hitchat_deal_data, scribe, c)
        print(f"done page: {page}")
        time.sleep(60)