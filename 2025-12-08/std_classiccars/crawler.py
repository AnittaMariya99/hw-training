from items import ProductUrlItem
import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, MONGO_COLLECTION_RESPONSE, BASE_URL


class Crawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        logging.info("Initializing..........................................")
        
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.mongo = self.client[DB_NAME]

    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------
    def start(self):
        page_number = 1
        logging.info(f"\nStarting Classic Cars Crawler...\n")


        #     construct url with current page number
        api_url = f"{BASE_URL}?p={page_number}"

        # start loop
        while True:
        #     fetch html
            logging.info(f"Fetching page from url: {api_url}")
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                last_page_number = self.parse_item(response)            

                if page_number >= last_page_number:
                    logging.info("Reached the last page. Ending crawl.") 
                    break

                page_number += 1
                api_url = f"{BASE_URL}?p={page_number}"
                logging.info(f"Moving to next page: {page_number}")
            else:
                logging.info("Failed to fetch response. Retrying...")
                break


    # ---------------------------------------------------------
    # PARSE ITEMS 
    # ---------------------------------------------------------
    def parse_item(self, response):
        """Extract property/car listing links and basic details.sel = Selector(html)"""

        sel = Selector(response.text)  

        PRODUCT_XPATH = "//div[contains(@class,'flexbox') and contains(@class,'panel-mod')]"
        PRODUCT_LINK_XPATH = ".//div[contains(@class,'fi-sritem-col-1')]//a/@href"
        PRODUCT_IMAGE_XPATH = ".//div[contains(@class,'fi-sritem-col-1')]//img/@data-src"
        PRODUCT_TITLE_XPATH = ".//div[contains(@class,'h-sri-car-title')]/text()"
        PRODUCT_PRICE_XPATH = ".//div[contains(@class,'mrg-b-sri-price')]//span/text()"   
        LAST_PAGE_XPATH = "//div[@class='b w100 mrg-b-lg text-center']/span[@class='red'][3]/text()"

        # Select all listing containers
        product_list = sel.xpath(PRODUCT_XPATH)

        for product in product_list:

            # product URL
            product_link = product.xpath(PRODUCT_LINK_XPATH).get()
            if product_link:
                product_link = "https://classiccars.com" + product_link.strip() # complete URL
            else:
                product_link = None


            # image URL (data-src preferred over src)
            image_url = product.xpath(PRODUCT_IMAGE_XPATH).get()
            # title
            title = product.xpath(PRODUCT_TITLE_XPATH).get()
            if title:
                title = title.strip()
            # price
            price = product.xpath(PRODUCT_PRICE_XPATH).get()
            if price:
                price = price.strip()

            item = {
                "url": product_link,
                "image_url": image_url,
                "title": title,
                "price": price
            }
            try:
                product_item = ProductUrlItem(**item)
                self.mongo.process(product_item,collection=MONGO_COLLECTION_RESPONSE)  # Mongo insert using items

                # self.collection.insert_one(product_item)
                print(product_item)

            except Exception as e:
                logging.exception(f"Failed to insert item into MongoDB: {e}")

        last_page_number = sel.xpath(LAST_PAGE_XPATH).get()
        last_page_number = int(last_page_number.replace(".", "").strip())

        
        return last_page_number  

        

    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        """Close function for all module object closing"""
        
        logging.info(f"Closing DB connection...")
        self.client.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
