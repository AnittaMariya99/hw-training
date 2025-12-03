import json
import requests
from parsel import Selector
from pymongo import MongoClient
from logger import get_logger
from settings import BASE_URL, HEADERS, MONGO_URI, DB_NAME, COLLECTION
from exceptions import DataMiningError

logger = get_logger("main_crawler")


# ---------------------------------------------------------
# BAYUT CRAWLER CLASS
# ---------------------------------------------------------
class Bayutrcrawler:
    def __init__(self):
        """Initialize crawler, DB, logs."""
        logger.info("Initializing bayut...")

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

        self.raw_file = "raw.html"
        self.cleaned_file = "cleaned_data.txt"


    # ---------------------------------------------------------
    # FETCH HTML
    # ---------------------------------------------------------
    def fetch_html(self, url):
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} from {url}"
                )

            html = response.text

            with open(self.raw_file, "w", encoding="utf-8") as f:
                f.write(html)

            return html

        except Exception as err:
            logger.error(f"Connection error: {err}")


    # ---------------------------------------------------------
    # PARSE HTML
    # ---------------------------------------------------------
    def parse_data(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"Parsing failed: {err}")


    # ---------------------------------------------------------
    # SAVE CLEANED DATA TO FILE
    # ---------------------------------------------------------
    def save_to_file(self, data_list):
        with open(self.cleaned_file, "w", encoding="utf-8") as f:
            for item in data_list:
                f.write(item + "\n")


    # ---------------------------------------------------------
    # PARSE ITEMS – BAYUT COMMERCIAL RENT LISTINGS
    # ---------------------------------------------------------
    def parse_item(self, html):
        """Extract property listing links from Bayut.bh with pagination."""

        sel = self.parse_data(html)

        BASE_URL = "https://www.bayut.bh"
        start_url = "https://www.bayut.bh/en/to-rent/commercial/bahrain/"

        logger.info(f"Starting Bayut crawler at: {start_url}")

        all_property_links = []
        next_page_url = start_url

        # ---------------- Pagination loop ----------------
        while next_page_url:

            logger.info(f"Fetching page: {next_page_url}")
            page_html = self.fetch_html(next_page_url)
            page_sel = Selector(page_html)

            # Extract property listing URLs
            property_links = page_sel.xpath(
                '//a[contains(@class,"_8969fafd")]/@href'
            ).getall()

            logger.info(f"Found {len(property_links)} property links")

            cleaned_links = [
                link if link.startswith("http") else BASE_URL + link
                for link in property_links
            ]

            # Add to master list
            all_property_links.extend(cleaned_links)

            # Save in DB
            self.save_urls_to_mongo(cleaned_links)

            # Pagination
            next_page = page_sel.xpath('//a[@title="Next"]/@href').get()

            if next_page:
                next_page_url = BASE_URL + next_page
            else:
                logger.info("No more pages. Scraping completed.")
                next_page_url = None

        return all_property_links


    # ---------------------------------------------------------
    # SAVE CLEANED URLS TO MONGO
    # ---------------------------------------------------------
    def save_urls_to_mongo(self, url_list):
        for url in url_list:
            self.collection.update_one(
                {"url": url},
                {"$set": {"url": url}},
                upsert=True
            )


    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------
    def start(self, url):
        html = self.fetch_html(url)
        product_links = self.parse_item(html)

        logger.info(f"\nTotal extracted product URLs: {len(product_links)}")

        self.save_to_file(product_links)
        logger.info(f"All data saved to file successfully.")


    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        logger.info(f"Closing DB connection...")
        self.client.close()