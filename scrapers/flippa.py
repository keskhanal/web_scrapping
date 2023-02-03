import requests
import sys
import json
import logging
import time
import pandas as pd
import util
import config
from pymongo import MongoClient
from datetime import datetime
from scribe.scribe import Scribe
from price_parser import Price
import hashlib

MARKETPLACE = 'flippa'

class ScribeFlippa(Scribe):

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



"""
    This retrieves page results using flippa's api. 
    There doesn't seem to be any authentication needed!
"""
def retrieve_page_results(page_num):

    headers = {
        'authority': 'flippa.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://flippa.com/websites?search_template=most_relevant&filter%5Bsale_method%5D=auction,classified&filter%5Bstatus%5D=open&filter%5Bproperty_type%5D=website&filter%5Bsitetype%5D=content,blog,directory,review,forum-community&filter%5Brevenue_generating%5D=T,F',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'traceparent': '00-67aa3b652e4202f19daa1f7b96e96a60-fe092873fb37b0f0-01',
        'tracestate': '3168357@nr=0-1-3168357-498618715-fe092873fb37b0f0----1674093768498',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-newrelic-id': 'VwcBWVVWDxAEXVlUBgYHUVI=',
    }
    url = f'https://flippa.com/search?filter%5Bproperty_type%5D=website&filter%5Brevenue_generating%5D=T,F&filter%5Bsale_method%5D=auction,classified&filter%5Bsitetype%5D=content,blog,directory,review,forum-community&filter%5Bstatus%5D=open&format=js&search_template=most_relevant&page%5Bnumber%5D={page_num}&page%5Bsize%5D={100}'
    try:
        response = requests.get(url, headers=headers, proxies=config.get_proxies())
        data = json.loads(response.text)
        results = data['results']
        total_results = data['metadata']['totalResults']
        return {
            'results': results,
            'total_results': total_results
        }
    except Exception as e:
        logging.error("Exception Occured", exc_info=True)
    

def scrape_all_pages(max_results=100000):
    listings = []
    curr_page = 1 #Flippa starts with page 1, not 0
    data = retrieve_page_results(curr_page)
    total = data['total_results']
    listings.extend(data['results'])
    logging.info(f'Retrived first set of results -- {len(listings)} out of a total of {total}')
    while len(listings) < total and len(listings) < max_results:
        curr_page += 1
        data = retrieve_page_results(curr_page)
        listings.extend(data['results'])
        logging.info(f'Retrieved {len(listings)} out of a total of {total} results')

    #df = pd.DataFrame(listings)
    return listings


if __name__ == '__main__':

    logpath = config.logconf['path']
    logfile = f'{logpath}/scraper_{MARKETPLACE}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    logging.basicConfig(filename=logfile, level=config.logconf['level'], filemode='w', format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')

    logging.info(f"Configuration -- \n {config} \n")

    all_recs = scrape_all_pages()

    scribe = ScribeFlippa()
    mongoclient = MongoClient(config.dbconf['connection_string'])
    c = mongoclient[config.dbconf['db']][config.dbconf['collection']]

    new_recs = util.flush_to_db(all_recs, scribe, c)

    df = pd.DataFrame(new_recs)
    uri = util.save_to_s3(
        MARKETPLACE,
        df, 
        config.config['s3_output_path']['bucket'],
        config.config['s3_output_path']['prefix']
    )

