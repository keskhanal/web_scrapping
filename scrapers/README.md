This module contains all the scraper / transform jobs.

Two types of jobs:
- Scrapers -- These programmatically scrape, transform and ingest the results into the DB
- Transformers -- These take existing files scraped from a marketplace and simply transform them and ingest them into the DB.

The non-programmatic scrapers will likely be run in octoparse and processed via lambda jobs. 



To run the scrapers, you need to create `config.yml` from the template `config.yml.example`

In the configuration file, fill in any required credentials for brightdata as well as marketplace specific credentials needed.



