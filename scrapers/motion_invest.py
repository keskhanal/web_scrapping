import util
import config
import logging
from datetime import datetime
from pymongo import MongoClient

from helpers.motion_invest import scrape_motion_invest, ScribeMotionInvest, driver_setup, navigate_single_page

if __name__ == '__main__':
    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_motion_invest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")
    site_username = 'subashb@termaproject.com'
    site_password = 'motioninvest123!@#'
    site_url = "https://www.motioninvest.com/sites-available/"
    driver = driver_setup()

    scribe = ScribeMotionInvest()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    deal_list = scrape_motion_invest(driver, site_url, site_username, site_password)

    for deal in deal_list:
        try:
            deal_data = navigate_single_page(driver, deal)
            print(f"{deal['title']} scrapped successfully...")

            client = mongoclient[config.dbconf['db']][config.dbconf['collection']]
            new_recs = util.flush_to_db([deal_data], scribe, client)
            print(f"{deal['title']} dummped to db successfully...")
        
        except Exception as e:
            print(str(e))
            pass