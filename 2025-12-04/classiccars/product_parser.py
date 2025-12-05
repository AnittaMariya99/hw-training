
import json
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION, BASE_URL
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
class classiccarsProductParser:
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
        

        try:
            

            listing_id = sel.xpath(
                "//li[@class='border-btm p-productID']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            location = sel.xpath(
                "//li[@class='border-btm p-address']//span[@class='w40 d-inline-block b fs-14 gray']/text()"
            ).get("")

            year = sel.xpath(
                "//li[@class='border-btm dt-start']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            make = sel.xpath(
                "//li[@class='border-btm p-manufacturer']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            model = sel.xpath(
                "//li[@class='border-btm p-model']//span[@class='w40 d-inline-block b fs-14 gray']/text()"
            ).get("")

            exterior_color = sel.xpath(
                "//li[@class='border-btm p-color']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            interior_color = sel.xpath(
                "//span[contains(@class,'p-interiorColor')]/following-sibling::span/text()"
            ).get("")

            transmission = sel.xpath(
                "//li[@class='border-btm p-transmission']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            engine = sel.xpath(
                "//li[@class='border-btm p-engine']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            mileage = sel.xpath(
                "//li[@class='border-btm p-odometer']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
            ).get("")

            drive_train = sel.xpath(
                "//span[contains(@class,'p-driveTrain')]/following-sibling::span/text()"
            ).get("")

            # Description (placeholder until you provide exact HTML)
            description = sel.xpath("//div[@class='p-description font-hostile-takeover readmore is-clamped expanded']/p").get()
            


            

            return {
                
                "listing_id": listing_id,
                "year": year,
                "make": make,
                "model": model,
                "location": location,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "mileage": mileage,
                "transmission": transmission,
                "engine": engine,
                "drive_train": drive_train,
                "description": description,
                
            }

        except Exception as err:
            raise DataMiningError(f"Failed to parse product {url}: {err}")



        
    # --------------------------------------------------
    # 5. Generator to iterate product URLs one-by-one 
    # --------------------------------------------------
    def yield_product_urls(self):
        cursor = self.collection.find({"listing_id": {"$exists": False}})
        for document in cursor:
            
            yield document["_id"], document.get("product_link")


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logger.info(f"\nStarting Marks & Spencer Product Detail Scraper...\n")


        for doc_id, product_url in self.yield_product_urls():
            
            logger.info(f"\nProcessing: {product_url}")

            try:
                details = self.parse_product(product_url)

               
                # Update database
                self.collection.update_one(
                    {"_id": doc_id},
                    {"$set": details}
                )

                
                logger.info(f"Updated product: {product_url}\n")


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
                
        except DataMiningError as err:
            logger.error(f"{err}")