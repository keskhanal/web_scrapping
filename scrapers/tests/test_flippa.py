import pytest
import scrapers.flippa as flippa
import pandas as pd


def check_transform(t, e) -> bool:
    return  (
        t['std_id'] == e['std_id'] and
        t['std_marketplace_id'] == e['std_marketplace_id'] and
        t['std_name'] == e['std_name'] and
        t['std_description'] == e['std_description'] and
        t['std_url'] == e['std_url'] and
        t['std_askingprice'] == e['std_askingprice'] and
        t['std_create_ts'] and
        len(t.keys()) == len(e.keys())
    )


def test_transform():
    client = flippa.ScribeFlippa()
    record = {
        'id': '11318653',
        'listing_url': 'https://flippa.com/11318653',
        'title': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ',
        'summary': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ',
        'has_verified_traffic': 'True',
        'has_verified_revenue': 'False',
        'price': '260000',
        'bid_count': '0',
        'sale_method': 'classified'
    }

    output_record = {
        'id': '11318653', 
        'listing_url': 'https://flippa.com/11318653', 
        'title': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ', 
        'summary': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ', 
        'has_verified_traffic': 'True', 
        'has_verified_revenue': 'False', 
        'price': '260000', 
        'bid_count': '0', 
        'sale_method': 'classified', 
        'std_id': '6b86f3595884ac8946dc037850cee7372787206f8d4a94bf12eed7493615612e', 
        'std_marketplace_id': 'flippa', 
        'std_name': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ', 
        'std_description': 'Successful 9-year-old, Content Site, in the Survival/Prepper Niche, Making $8,978/m from Diverse Sources in Affiliate Marketing and Display Advertising. ', 
        'std_url': 'https://flippa.com/11318653', 
        'std_askingprice': {'amount': 260000.0, 'currency': 'USD'}, 
        'std_create_ts': '2023-01-23 12:16:09.013121', 
        'status': 'NEW'
    }
    assert check_transform(client.standardize_record(record), output_record)



def test_request():
    data = flippa.retrieve_page_results(1) 
    results = data['results']
    total = data['total_results']
    print(f'Retrieved {len(results)} results of {total} results')
    assert len(results) > 0
    assert total >= len(results)

#TODO: we need better tests here?
def test_pagination():
    df = flippa.scrape_all_pages(200)
    print(df)
    assert len(df) > 0


