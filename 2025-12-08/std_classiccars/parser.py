import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, DataMiningError


class Parser:
    """parser"""

    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection_response = self.db[MONGO_COLLECTION_RESPONSE]
        self.collection_data = self.db[MONGO_COLLECTION_DATA]
        self.collection_failed = self.db[MONGO_COLLECTION_URL_FAILED]

    # --------------------------------------------------
    # 1. Fetch HTML with safe exception handling 
    # --------------------------------------------------
    def fetch_html(self, url):
        try:
            
            logging.info(f"Fetching product page ::: {url}")
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
        cursor = self.collection_response.find({"listing_id": {"$exists": False}})
        for document in cursor:
            
            yield document


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logging.info(f"\nStarting Classic Cars Product Detail Scraper...\n")


        for document in self.yield_product_urls():
            
            product_url = document.get("product_link")
            
            # Skip if product_url is None or empty
            if not product_url:
                logging.warning(f"Skipping document with missing product_link: {document.get('_id')}")
                continue
                
            logging.info(f"\nProcessing: {product_url}")

            try:
                # Parse product details
                parsed_details = self.parse_product(product_url)

                # Merge crawler data with parsed data
                complete_data = {**document, **parsed_details}
                
                # Remove MongoDB _id from the data to be inserted
                if "_id" in complete_data:
                    del complete_data["_id"]
               
                # Save to MONGO_COLLECTION_DATA
                try:
                    self.collection_data.update_one(
                        {"product_link": product_url},
                        {"$set": complete_data},
                        upsert=True
                    )
                except Exception as db_err:
                    logging.error(f"Database error saving to data collection: {db_err}")
                    raise DataMiningError(f"Database save failed: {db_err}")

                # Mark as processed in MONGO_COLLECTION_RESPONSE
                try:
                    self.collection_response.update_one(
                        {"_id": document["_id"]},
                        {"$set": {"listing_id": parsed_details.get("listing_id", "processed")}}
                    )
                except Exception as db_err:
                    logging.error(f"Database error updating response collection: {db_err}")
                
                logging.info(f"Saved product to data collection: {product_url}\n")


            except DataMiningError as err:
                logging.error(f"DataMiningError: {err}")
                
                # Save failed URL to MONGO_COLLECTION_URL_FAILED
                try:
                    failed_data = {
                        "product_link": product_url,
                        "error": str(err),
                        "document_data": document
                    }
                    self.collection_failed.update_one(
                        {"product_link": product_url},
                        {"$set": failed_data},
                        upsert=True
                    )
                    logging.info(f"Saved failed URL to failed collection: {product_url}\n")
                except Exception as db_err:
                    logging.error(f"Failed to save to failed collection: {db_err}")
                    
            except Exception as err:
                logging.error(f"Unexpected error processing {product_url}: {err}")
                
                # Save unexpected errors to failed collection
                try:
                    failed_data = {
                        "product_link": product_url,
                        "error": f"Unexpected error: {str(err)}",
                        "document_data": document
                    }
                    self.collection_failed.update_one(
                        {"product_link": product_url},
                        {"$set": failed_data},
                        upsert=True
                    )
                    logging.info(f"Saved failed URL (unexpected error) to failed collection: {product_url}\n")
                except Exception as db_err:
                    logging.error(f"Failed to save unexpected error to failed collection: {db_err}")

    # --------------------------------------------------
    # Close DB connection (Destructor)
    # --------------------------------------------------
    def close(self):
        """connection close"""
        
        logging.info(f"Closing MongoDB connection...")
        self.client.close()

    # --------------------------------------------------
    # parse a single product (for testing)
    # --------------------------------------------------
    def parse_single_product(self, url):
        try:
            details = self.parse_product(url)
            logging.info("Extracted Product Details:")
            for key, value in details.items():
                logging.info(f"{key}: {value}")
                
        except DataMiningError as err:
            logging.error(f"{err}")


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()

