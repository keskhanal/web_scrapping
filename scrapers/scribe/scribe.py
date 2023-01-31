from abc import ABC, abstractmethod
from pymongo import MongoClient
from price_parser import Price
import hashlib
import logging
from datetime import datetime
import json


class Scribe(ABC):

    def __init__(self):
        logging.basicConfig(filename="myapp.log", level=logging.INFO)

    @abstractmethod
    def marketplace(self):
        pass

    @abstractmethod
    def get_id(self, rec):
        pass
    
    @abstractmethod
    def get_name(self, rec):
        pass

    @abstractmethod
    def get_description(self, rec):
        pass

    @abstractmethod
    def get_marketplace_id(self, rec):
        pass
    
    @abstractmethod
    def get_url(self, rec):
        pass

    @abstractmethod
    def get_askingprice(self, rec):
        pass

    def standardize_record(self, rec):
        try:
            new_rec = rec.copy()
            new_rec['std_id'] = self.get_id(rec)
            new_rec['std_marketplace_id'] = self.get_marketplace_id(rec)
            new_rec['std_name'] = self.get_name(rec)
            new_rec['std_description'] = self.get_description(rec)
            new_rec['std_url'] = self.get_url(rec)
            new_rec['std_askingprice'] = self.get_askingprice(rec)
            new_rec['std_marketplace_id'] = self.get_marketplace_id(rec)
            new_rec['std_create_ts'] = str(datetime.now())
            new_rec['status'] = 'NEW' # 'NEW' | 'SKIP' | 'IN_CLICKUP' 
        except Exception as e:
            logging.error(f"Error with record: {json.dumps(rec)}", exc_info=True)
            raise e
        return new_rec
    
    def insert_new_record(self, rec, collection):
        existing_record = collection.find_one({'std_id': rec['std_id']})
        if existing_record is None:
            # Record is new, insert it into the collection
            new_record = collection.insert_one(rec)
            return (False, new_record)
        else:
            # Record already exists, do not insert it
            return (True, existing_record)
        return

