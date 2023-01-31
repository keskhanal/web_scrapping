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


MARKETPLACE = 'empire_flippers'

class ScribeEmpireFlippers(Scribe):

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
        p = Price.fromstring(str(rec['price']))
        return {
            "amount": float(p.amount),
            "currency": p.currency if p.currency else 'USD'
        }

    def __init__(self):
        super().__init__()




def retrieve_token(email, password):
    headers = {
        'authority': 'api.empireflippers.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://app.empireflippers.com',
        'referer': 'https://app.empireflippers.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    json_data = {
        'email': email,
        'password': password,
        'totp_password': '',
    }
    try:
        logging.info("Retrieving token...")
        response = requests.post('https://api.empireflippers.com/api/v1/sessions/create', headers=headers, json=json_data)
        data = json.loads(response.text)
        logging.info("Extracted token!")
        return data['data']['jwt']
    except:
        logging.error('Exception with Token Retrieval', exc_info=True)

"""
    This retrieves page results using empire_flipper's api. 
    Bearer Token required
    There doesn't seem to be any authentication needed!
"""
def retrieve_page_results(token, page_num):
  
    headers = {
        'authority': 'api.empireflippers.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {token}',
        'origin': 'https://app.empireflippers.com',
        'referer': 'https://app.empireflippers.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    params = {
        'q': '',
        'page': page_num,
        'new_listing': 'true',
        'listing_status': 'New Listing||For Sale||Pending Sold',
        'monetizations': '',
        'niches': '',
        'platforms': '',
        'listing_price_include_unpriced': 'true',
        'limit': 100,
    }

    url = f'https://api.empireflippers.com/api/v1/listings/marketplace'
    try:
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        data = json.loads(response.text)
        results = data['data']['listings']
        total_results = data['data']['count']
        return {
            'results': results,
            'total_results': total_results
        }
    except Exception as e:
        logging.error("Exception Occured")
    

def scrape_all_pages(token, max_results=100000):
    listings = []
    curr_page = 1 #Flippa starts with page 1, not 0
    data = retrieve_page_results(token, curr_page)
    total = data['total_results']
    listings.extend(data['results'])
    logging.info(f'Retrived first set of results -- {len(listings)} out of a total of {total}')

    while len(listings) < total and len(listings) < max_results:
        curr_page += 1
        data = retrieve_page_results(token, curr_page)
        listings.extend(data['results'])
        logging.info(f'Retrieved {len(listings)} out of a total of {total} results')

    return listings





if __name__ == '__main__':

    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_{MARKETPLACE}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config['logs']['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    all_recs = scrape_all_pages()

    scribe = ScribeEmpireFlippers()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    c = mongoclient[config.dbconf['db']][config.dbconf['collection']]

    new_recs = util.flush_to_db(all_recs, scribe, c)


    # uri = util.save_to_s3(
    #     MARKETPLACE,
    #     results_df, 
    #     config['s3_output_path']['bucket'],
    #     config['s3_output_path']['prefix']
    # )
