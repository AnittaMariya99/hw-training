from items import ProductItem
import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI,MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED,MONGO_HOST,MONGO_PORT


class Parser:
    """parser"""

    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection_response = self.db[MONGO_COLLECTION_RESPONSE]
        self.collection_data = self.db[MONGO_COLLECTION_DATA]
        self.collection_failed = self.db[MONGO_COLLECTION_URL_FAILED]
        self.mongo = self.client[MONGO_DB]


    # --------------------------------------------------
    #  Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logging.info(f"\nStarting Classic Cars Product Detail Scraper...\n")

        product_items = self.collection_response.find()

        for document in product_items:
            
            product_url = document.get("url")
            
            # Skip if product_url is None or empty
            if not product_url:
                logging.warning(f"Skipping document with missing product_link: {document.get('_id')}")
                continue
                
            logging.info(f"\nProcessing: {product_url}")

            try:

                response = requests.get(product_url, headers=HEADERS, timeout=10)
                if response.status_code != 200:
                    raise Exception(
                        f"Invalid response {response.status_code} for {product_url}"
                    )
                # Parse product details
                self.parse_product(document, response)

            except Exception as err:
                logging.error(f"Unexpected error processing {product_url}: {err}")
                
                # Save failed URL to MONGO_COLLECTION_URL_FAILED
                failed_data = {
                    "product_link": product_url,
                    "error": str(err),
                }
                self.collection_failed.insert_one(failed_data)
                logging.info(f"Saved failed URL to failed collection: {product_url}\n")

    # --------------------------------------------------
    # Extract product details (main logic)
    # --------------------------------------------------
    def parse_product(self, document, response):

        sel = Selector(response.text)

        # XPATH
        LISTING_ID_XPATH = "//li[@class='border-btm p-productID']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        LOCATION_XPATH = "//li[@class='border-btm p-address']//span[@class='w40 d-inline-block b fs-14 gray']/text()"
        YEAR_XPATH = "//li[@class='border-btm dt-start']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        MAKE_XPATH = "//li[@class='border-btm p-manufacturer']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        MODEL_XPATH = "//li[@class='border-btm p-model']//span[@class='w40 d-inline-block b fs-14 gray']/text()"
        EXTERIOR_COLOR_XPATH = "//li[@class='border-btm p-color']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        INTERIOR_COLOR_XPATH = "//span[contains(@class,'p-interiorColor')]/following-sibling::span/text()"
        TRANSMISSION_XPATH = "//li[@class='border-btm p-transmission']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        ENGINE_XPATH = "//li[@class='border-btm p-engine']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
        MILEAGE_XPATH = "//li[@class='border-btm p-odometer']//span[@class='w50 d-inline-block b fs-14 gray']/text()"
       
        # EXTRACT
        listing_id = sel.xpath(LISTING_ID_XPATH).get("")
        location = sel.xpath(LOCATION_XPATH).get("")
        year = sel.xpath(YEAR_XPATH).get("")
        make = sel.xpath(MAKE_XPATH).get("")
        model = sel.xpath(MODEL_XPATH).get("")
        exterior_color = sel.xpath(EXTERIOR_COLOR_XPATH).get("")
        interior_color = sel.xpath(INTERIOR_COLOR_XPATH).get("")
        transmission = sel.xpath(TRANSMISSION_XPATH).get("")
        engine = sel.xpath(ENGINE_XPATH).get("")
        mileage = sel.xpath(MILEAGE_XPATH).get("")

        # ITEM YEILD
        item = {}
        item["website"] = "ClassicCars"
        item["url"] = document.get("url")
        item["image_url"] = document.get("image_url")
        item["title"] = document.get("title")
        item["price"] = document.get("price")
        item["listing_id"] = listing_id
        item["make"] = make
        item["model"] = model
        item["location"] = location
        item["exterior_color"] = exterior_color
        item["interior_color"] = interior_color
        item["mileage"] = mileage
        item["transmission"] = transmission
        item["engine"] = engine

       

        product_item = ProductItem(**item)
        # self.mongo.process(product_item,collection=MONGO_COLLECTION_DATA)  # Mongo insert using items

        logging.info(item)
        try:
            self.collection_data.insert_one(product_item)
        except:
            pass


    # --------------------------------------------------
    # Close DB connection (Destructor)
    # --------------------------------------------------
    def close(self):
        """connection close"""
        
        logging.info(f"Closing MongoDB connection...")
        self.client.close()


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()

