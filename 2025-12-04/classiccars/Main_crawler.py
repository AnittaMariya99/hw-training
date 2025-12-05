import json
import requests
from parsel import Selector
from pymongo import MongoClient
from logger import get_logger
from settings import  HEADERS, MONGO_URI, DB_NAME, COLLECTION
from exceptions import DataMiningError

logger = get_logger("main_crawler")


# ---------------------------------------------------------
# CRAWLER CLASS
# ---------------------------------------------------------
class classiccarscrawler:
    def __init__(self):
        """Initialize crawler, DB, logs."""
        logger.info("Initializing.........................................")

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]




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

            return html

        except Exception as err:
            logger.error(f"Connection error: {err}")


    # ---------------------------------------------------------
    # PARSE HTML
    # ---------------------------------------------------------
    def create_selector(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"Parsing failed: {err}")



    # ---------------------------------------------------------
    # PARSE ITEMS 
    # ---------------------------------------------------------
    def parse_item(self, sel):
        """Extract property/car listing links and basic details.sel = Selector(html)"""

        product_list = []   

    # Select all listing containers
        listings = sel.xpath("//div[contains(@class,'flexbox') and contains(@class,'panel-mod')]")

        for item in listings:

            # product URL
            product_link = item.xpath(".//div[contains(@class,'fi-sritem-col-1')]//a/@href").get()
            if product_link:
                product_link = "https://classiccars.com" + product_link.strip() # complete URL
            else:
                product_link = None


            # image URL (data-src preferred over src)
            image_url = item.xpath(".//div[contains(@class,'fi-sritem-col-1')]//img/@data-src").get()
            

            # title
            title = item.xpath(".//div[contains(@class,'h-sri-car-title')]/text()").get()
            if title:
                title = title.strip()

            # price
            price = item.xpath(".//div[contains(@class,'mrg-b-sri-price')]//span/text()").get()
            if price:
                price = price.strip()

            product_list.append({
                "product_link": product_link,
                "image_url": image_url,
                "title": title,
                "price": price
            
            })

        return product_list  





    # ---------------------------------------------------------
    # SAVE CLEANED URLS TO MONGO
    # ---------------------------------------------------------
    def save_data_to_mongo(self, extracted_records):
        for extracted_record in extracted_records:
            self.collection.update_one(
                {"product_link": extracted_record["product_link"]},
                {"$set": extracted_record},
                upsert=True
                )

    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------

    def start(self, url):
        page_number = 1
        logger.info(f"\nStarting Classic Cars Crawler...\n")

        # start loop
        while True:
        #     construct url with current page number
            full_url = f"{url}?p={page_number}"
        #     fetch html
            html = self.fetch_html(full_url)
        #     create selector using html
            sel = self.create_selector(html)
        #     get product list using selector : call parse_items()
            product_list = self.parse_item(sel)
        #     save to mongoDB
            self.save_data_to_mongo(product_list)
        #     get last page number using selector
        
            last_page_number = sel.xpath("//div[@class='b w100 mrg-b-lg text-center']/span[@class='red'][3]/text()").get()
        #     check the current page number equal to the last page number from the selector
            page_number = int(page_number)
            last_page_number = int(last_page_number.replace(".", "").strip())

            if page_number >= last_page_number:
    
                logger.info("Reached the last page. Ending crawl.") 
        #         break
                break
        #     increment page number by 1
            page_number += 1
            logger.info(f"Moving to next page: {page_number}")
    



    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        logger.info(f"Closing DB connection...")
        self.client.close()