import logging
import pandas as pd
from datetime import datetime 
from scribe.scribe import Scribe

def get_proxies(user: str, pw: str):
    """Using BrightData services, this returns the proxy servers.
    """
    proxy_user = user 
    proxy_pass = pw 
    proxies = {
        'http': f'http://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225',
        'https': f'http://{proxy_user}:{proxy_pass}@zproxy.lum-superproxy.io:22225'
        }
    return proxies


def save_to_s3(MARKETPLACE: str, df: pd.DataFrame, bucket_name:  str, prefix: str, access_key: str = None, secret_key: str = None):
    dtstr = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f'{MARKETPLACE}/{MARKETPLACE}_{dtstr}.json'
    uri = f's3://{bucket_name}/{prefix}/{filepath}'
    print(uri)
    try:
        logging.info(f'Saving results file: {uri} ...')
        if secret_key and access_key:
            df.to_json(uri, orient='records', lines=True, storage_options={'key': access_key, 'secret': secret_key})
        else:
            df.to_json(uri, orient='records', lines=True)
        logging.info(f'Results saved')
        return uri
    except Exception as e:
        logging.error('Exception while saving results', exc_info=True)


def flush_to_db(recs, scribe: Scribe, mongo_collection):
    """Flushes all the scraped records to mongo using Scribe service
    """
    N = len(recs)
    new_recs = []
    logging.info(f"Flushing {N} records")
    for rec in recs:
        std_rec = scribe.standardize_record(rec)
        result = scribe.insert_new_record(std_rec, mongo_collection)
        if not result[0]:
            new_recs.append(result[1]) 
        
    logging.info(f"Out of {N} records, {len(new_recs)} were new")
    return new_recs