# phaser_product_parser.py

import json
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from .settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION, BASE_URL
from .utils.logger import get_logger
logger = get_logger("product_parser")

# -----------------------
# Custom Exception
# -----------------------
class DataMiningError(Exception):
    """Raised for errors during product parsing."""
    pass


# ------------------------------------------------------
# OOP Class for Product Detail Extraction (Task 1)
# ------------------------------------------------------
class MarksAndSpencerProductParser:
    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

        self.raw_file = "product_raw.html"
        self.cleaned_file = "product_cleaned.txt"

    # --------------------------------------------------
    # 1. Fetch HTML with safe exception handling (Task 4)
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
    # 2. Parse HTML (Mock BeautifulSoup using parsel) (Task 1)
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
             # Example regex patterns for upc or strokeId
            upc_match = re.search(r'"upc"\s*:\s*"(\d+)"', html)
            stroke_match = re.search(r'"strokeId"\s*:\s*"([^"]+)"', html)
            upc = upc_match.group(1) if upc_match else None
            strokeId = stroke_match.group(1) if stroke_match else None
            # print("unique_id:", upc or strokeId)


            brand = sel.xpath(
                "//p[contains(@class,'brand-title_title')]/text()"
            ).get()

             # Fix 1: Correct XPath syntax - use @type instead of @class
            script = sel.xpath("//script[@type='application/ld+json']//text()").get()
            # Fix 2: Use json.loads() to parse the JSON string
            data = json.loads(script)
            # Fix 3: Get the name from the parsed data
            product_name = data.get("name")
            print("Product_Name:",product_name)

            price = sel.xpath(
                "//p[contains(@class,'headingSm')]/text()"
            ).get()

            # Color selected
            color_list = sel.xpath(
                "//p[contains(@class,'selector-group_legend')]//span/text()"
            ).getall()
            selected_color = (
                color_list[1] if len(color_list) > 1 else None
            )

            # Available colors with list comprehension (Task 6)
            available_colors = [
                c.replace(" colour option", "")
                for c in sel.xpath(
                    "//label[contains(@aria-label,'colour option')]/@aria-label"
                ).getall()
            ]

            # Description
            description_list = sel.xpath(
                "//p[contains(@class,'media-0_textSm')]//text()"
            ).getall()
            description = (
                description_list[1] if len(description_list) >= 2 else None
            )

            review_count = sel.xpath(
                "//span[contains(@class,'strong')]/text()"
            ).get()

            return {
                "unique_id:": upc or strokeId,
                "Brand_name": brand,
                "Product_name": product_name,
                "Price": price,
                "select_color": selected_color,
                "Discription": description,
                "review_count": review_count,
                "available_colors": available_colors
            }

        except Exception as err:
            raise DataMiningError(f"Failed to parse product {url}: {err}")

    # --------------------------------------------------
    # 4. Save cleaned data to file (Task 2)
    # --------------------------------------------------
    def save_to_file(self, cleaned_data):
        with open(self.cleaned_file, "w", encoding="utf-8") as file:
            for key, value in cleaned_data.items():
                file.write(f"{key}: {value}\n")

    # --------------------------------------------------
    # 5. Generator to iterate product URLs one-by-one (Task 3)
    # --------------------------------------------------
    def yield_product_urls(self):
        cursor = self.collection.find({"unique_id": {"$exists": False}})
        for document in cursor:
            
            yield document["_id"], document.get("url")


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logger.info(f"\nStarting Marks & Spencer Product Detail Scraper...\n")


        for doc_id, product_url in self.yield_product_urls():
            
            logger.info(f"\nProcessing: {product_url}")

            try:
                details = self.parse_product(product_url)

                # Save to cleaned file (only last product)
                self.save_to_file(details)

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
