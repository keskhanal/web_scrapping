import pytest
import scrapers.empire_flippers as empire_flippers
import pandas as pd
import config


def test_request():
    email = config.config['scraper_auth']['empire_flippers']['email']
    pw = config.config['scraper_auth']['empire_flippers']['pw']
    token = empire_flippers.retrieve_token(email, pw)
    data = empire_flippers.retrieve_page_results(token, 1) 
    results = data['results']
    total = data['total_results']
    print(f'Retrieved {len(results)} results of {total} results')
    assert len(results) > 0
    assert total >= len(results)

#TODO: we need better tests here?
#@pytest.mark.skip(reason="Not something that is reliably testable as there is no mock data")
def test_pagination():
    token = empire_flippers.retrieve_token("nikhil@termaproject.com", "N1kh1l87terma!")
    df = empire_flippers.scrape_all_pages(token, 200)
    print(df)
    assert len(df) > 0

