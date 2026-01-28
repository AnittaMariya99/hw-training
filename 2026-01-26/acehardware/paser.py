import logging
import json
import datetime 
import time

from pymongo import MongoClient
import hrequests
from parsel import Selector

from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, UA

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Parser:
    """Ace Hardware Product Parser"""

    def __init__(self):
        """Initialize parser, DB, and hrequests session."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.session = hrequests.Session(browser='chrome')
        logging.info("Connected to MongoDB and initialized hrequests session")

    def start(self):
        """Fetch URLs from DB and parse them."""
        # Load first 10 URLs found by the crawler
        products = list(self.db[MONGO_COLLECTION_RESPONSE].find().limit(100))
        total = len(products)

        logging.info(f"Parser started – total urls: {total}")

        for product in products:
            url = product.get('url')
            if not url:
                continue

            # Skip if already parsed (Optional, based on requirement. For now, we update)
            logging.info(f"Parsing → {url}")

                # Using hrequests for browser impersonation
            response = self.session.get(
                url,
                timeout=60
            )

            if response.status_code == 200:
                self.parse_item(response, product)
            else:
                logging.warning(f"Failed URL: {url} | Status: {response.status_code}")
                self.db[MONGO_COLLECTION_URL_FAILED].insert_one(
                    {"url": url, "status": response.status_code, "timestamp": time.time()}
                )

            time.sleep(1) # Polite delay

    def parse_item(self, response, product):
        """Extract product details and save to DB."""
        sel = Selector(response.text)
        PRICE_XPATH = "//div[@class='price ']/text()"
        PRELOADED_PRODUCT_XPATH = "//script[@id='data-mz-preload-product']/text()"
        SCHEMA_XPATH = "//script[@type='application/ld+json' and @id='productSchema']/text()"
        PRODUCT_CODE_XPATH = "//div[@class='productCode']/text()"
        BREADCRUMBS_XPATH = "//div[@id='breadcrumbs']//a//text()"
        # -------------------------
        # BASIC INFO
        # -------------------------
        price = sel.xpath(PRICE_XPATH).get()
        price = price.replace("$", "").strip()
        # -------------------------
        # PRELOADED PRODUCT JSON
        # -------------------------
        preload_text = sel.xpath(PRELOADED_PRODUCT_XPATH).get()
        preload = json.loads(preload_text)
        upc = preload.get("upc")
        brand = None
        country_of_origin = None

        for prop in preload.get("properties", []):
            name = prop.get("attributeDetail", {}).get("name")
            values = prop.get("values", [])

            if values:
                value = values[0].get("value")

                if name == "Brand Name":
                    brand = value
                elif name == "Country Of Origin":
                    country_of_origin = value

        # -------------------------
        # JSON-LD SCHEMA
        # -------------------------
        schema_text = sel.xpath(SCHEMA_XPATH).get()
        schema = json.loads(schema_text)

        availability = schema.get("offers", {}).get("availability", "")
        availability = availability.split("/")[-1] if availability else ""

        description = schema.get("description")
        manufacturer_part_number = schema.get("mpn")

        # -------------------------
        # VENDOR PART NUMBER
        # -------------------------

        vendor_part_number = sel.xpath(PRODUCT_CODE_XPATH).get()
        vendor_part_number = vendor_part_number.replace("Item #", "").strip()


        # -------------------------
        # BREADCRUMBS
        # -------------------------
        breadcrumbs = " > ".join(
            t.strip()
            for t in sel.xpath(BREADCRUMBS_XPATH).getall()
            if t.strip()
        )

        
        # -------------------------
        # FINAL ITEM
        # -------------------------


        item = {
            "company_name": "acehardware",
            "brand": brand,
            "manufacturer_part_number": manufacturer_part_number,
            "vendor_part_number": vendor_part_number,
            "item_name": product.get("product_name"),
            "full_product_description": description,
            "price": price,
            "country_of_origin": country_of_origin,
            "upc": upc,
            "product_category": breadcrumbs,
            "url": product.get("url"),
            "availability": availability,
            "date_crawled": datetime.datetime.now(),
        }

        # Save result to Data collection
        self.db[MONGO_COLLECTION_DATA].insert_one(item)
        logging.info(f"Saved product details: {item['url']}")

    def close(self):
        """Close MongoDB connection."""
        self.client.close()
        logging.info("MongoDB connection closed.")

if __name__ == "__main__":
    parser = Parser()
    try:
        parser.start()
    finally:
        parser.close()
