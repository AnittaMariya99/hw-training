
import json
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION
from logger import get_logger
logger = get_logger("product_parser")

# -----------------------
# Custom Exception
# -----------------------
class DataMiningError(Exception):
    """Raised for errors during product parsing."""
    pass


# ------------------------------------------------------
# OOP Class for Product Detail Extraction 
# ------------------------------------------------------
class EvrealestateProductParser:
    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]


    # --------------------------------------------------
    # 1. Fetch HTML with safe exception handling 
    # --------------------------------------------------
    def fetch_html(self, url):
        try:
            
            logger.info(f"Fetching product page ::: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} for {url}"
                )

            # Save raw HTML (Task 2)
            with open(self.raw_file, "w", encoding="utf-8") as file:
                file.write(response.text)

            return response.text

        except requests.RequestException as err:
            raise DataMiningError(f"Connection failed: {err}")

    # --------------------------------------------------
    # 2. Parse HTML 
    # --------------------------------------------------
    def parse_data(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"HTML parsing failed: {err}")

    # --------------------------------------------------
    # 3. Extract product details (main logic)
    # --------------------------------------------------
    def parse_product(self, url):
        html = self.fetch_html(url)
        sel = self.parse_data(html)
        
        

        description=sel.xpath("//meta[@property='og:description']/@content").get()        

        return {
                
                
            "description": description,
                
            
        }

    # --------------------------------------------------
    # 5. Generator to iterate product URLs one-by-one 
    # --------------------------------------------------
    def yield_product_urls(self):
        cursor = self.collection.find({"description": {"$exists": False}})
        for document in cursor:
            
            yield document["_id"], document.get("profile_url")


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logger.info(f"\nStarting Marks & Spencer Product Detail Scraper...\n")


        for doc_id, profile_url in self.yield_product_urls():
            
            logger.info(f"\nProcessing: {profile_url}")

            try:
                details = self.parse_product(profile_url)

                # Save to cleaned file (only last product)
                self.save_to_file(details)

                # Update database
                self.collection.update_one(
                    {"_id": doc_id},
                    {"$set": details}
                )

                
                logger.info(f"Updated product: {profile_url}\n")


            except DataMiningError as err:
               logger.info(f"Error: {err}")

    # --------------------------------------------------
    # Close DB connection (Destructor)
    # --------------------------------------------------
    def close(self):
        
        logger.info(f"Closing MongoDB connection...")
        self.client.close()

    # --------------------------------------------------
    # parse a single product (for testing)
    # --------------------------------------------------
    def parse_single_product(self, url):
        try:
            details = self.parse_product(url)
            logger.info("Extracted Product Details:")
            for key, value in details.items():
                logger.info(f"{key}: {value}")
            logger.info(f"Product details saved to {self.cleaned_file}")
        except DataMiningError as err:
            logger.error(f"{err}")