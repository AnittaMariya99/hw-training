from items import ProductItem
from mongoengine import connect
import logging
import requests
import json
import re
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS_2, MONGO_URI,MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED,MONGO_HOST,MONGO_PORT


class Parser:
    """parser"""

    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection_response = self.db[MONGO_COLLECTION_RESPONSE]
        self.collection_data = self.db[MONGO_COLLECTION_DATA]
        self.collection_failed = self.db[MONGO_COLLECTION_URL_FAILED]
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, alias="default", port=MONGO_PORT)


  
    def start(self):
        """start"""
        logging.info(f"\nStarting Classic Cars Product Detail Scraper...\n")

        product_items = list(self.collection_response.find())
        print(len(product_items))

        for document in product_items:
            
            product_url = document.get("url")
            
            # Skip if product_url is None or empty
            if not product_url:
                logging.warning(f"Skipping document with missing product_link: {document.get('_id')}")
                continue

            logging.info(f"\nProcessing: {product_url}")

            try:

                response = requests.get(product_url, headers=HEADERS_2)
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

    def parse_product(self, document, response):
        """Extract product details (main logic)"""
        sel = Selector(response.text)

        # XPATH
        TABLE_XPATH = '//table[@id="leaders"]/tbody/tr'
        
        # EXTRACT
    
        def get_table_value(header_name):
            # Finds the <td> text in the same row where <th> contains the header_name
            val = sel.xpath(f'{TABLE_XPATH}[th[contains(text(), "{header_name}")]]/td/text()').get()
            return val.strip() if val else None
        
        make = get_table_value('Make')
        model = get_table_value('Model')
        year = get_table_value('Year')
        color = get_table_value('Color')
        
        # --- 2. Extract VIN from Script Tag ---
        # VIN is inside a script tag that contains "vehicleIdentificationNumber"
        # The content is like: script.text = JSON.stringify({ ... });
        script_content = sel.xpath('//script[contains(text(), "vehicleIdentificationNumber")]/text()').get()
        vin = None

        if script_content:
        

            # Regex to capture the JSON object inside JSON.stringify(...)
            # We use DOTALL to match across lines and non-greedy .*? to find the closing parentheses
            match = re.search(r'JSON\.stringify\((\{.*?\})\);', script_content, re.DOTALL)
           
            if match:
                try:
                    json_str = match.group(1)
                    # Remove trailing commas which are valid in JS but not JSON
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    data = json.loads(json_str)
                    
                    vin = data.get('vehicleIdentificationNumber')
           
                except json.JSONDecodeError as e:
                    logging.info(f"JSON decode error: {e}") 
                    pass
       
        # ITEM YEILD
        item = {}
        item["website"] = "BeverlyHillscarClub"
        item["url"] = document.get("url")
        item["image_url"] = document.get("image_url")
        item["price"] = document.get("price")
        item["description"] = document.get("description")
        item["model"] = model
        item["make"] = make
        item["year"] = year
        item["color"] = color
        item["vehicleIdentificationNumber"] = vin
     
        product_item = ProductItem(**item)
        # self.mongo.process(product_item,collection=MONGO_COLLECTION_DATA)  # Mongo insert using items

        try:
            # self.collection_data.insert_one(product_item)
            product_item.save()
        except Exception as err:    
            logging.error(f"Failed to insert document: {product_item}")
            print(err)
            pass


    
    def close(self):
        """connection close"""
        
        logging.info(f"Closing MongoDB connection...")
        self.client.close()


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()

