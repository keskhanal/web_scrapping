from flippa import ScribeFlippa
import pymongo
import pytest



@pytest.fixture
def db_conf():
    return {
        'connection_string': 'mongodb+srv://scribeuser:ex0GJe5tbyWUSRDs@dealflowdb.s6j76.mongodb.net/?retryWrites=true&w=majority',
        'host':  "dealflowdb.s6j76.mongodb.net",
        'db': "dealflow_dev",
        'collection': "alldeals_test"
    }

@pytest.fixture
def db_client(db_conf):
    client = pymongo.MongoClient(db_conf['connection_string'])
    c = client[db_conf['db']][db_conf['collection']]
    b = c.delete_many({})
    return client


@pytest.fixture
def scribe_flippa():
    return ScribeFlippa() 

""" Will test the super class insert using Flippa instantiation"""
def test_insert(scribe_flippa, db_client, db_conf):
    record = {
        'listing_url': 'https://flippa.com/11318653',
        'title': 'ShtfPreparedness.com & ShtfDad.com',
        'summary': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising.',
        'Type': 'Content',
        'Niche': 'Lifestyle',
        'Age': '10 years',
        'MonthProfit': 'USD $8,113 /mo',
        'Profitmargin': '86%',
        'Profitmultiple': '2.7x',
        'Revenuemultiple': '2.3x',
        'price': 'USD $260,000'
    }

    transformed = scribe_flippa.standardize_record(record)

    c = db_client[db_conf['db']][db_conf['collection']]
    scribe_flippa.insert_new_record(transformed, c)
    result = c.find_one({'std_id': transformed['std_id']}) 
    assert result 

    scribe_flippa.insert_new_record(transformed, c)
    num_docs = c.count_documents({})
    assert num_docs == 1


    