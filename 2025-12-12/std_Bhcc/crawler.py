from items import ProductUrlItem
from mongoengine import connect
import logging
import requests
from parsel import Selector
from settings import HEADERS, MONGO_URI,MONGO_DB, MONGO_COLLECTION_RESPONSE, BASE_URL,MONGO_HOST,MONGO_PORT


class Crawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        logging.info("Initializing..........................................")
        self.seen_urls = set()
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, alias="default", port=MONGO_PORT)

   
    def start(self):
        """Starts the crawler."""
        offset= 0
        logging.info(f"\nStarting Classic Cars Crawler...\n")


        #     construct url with current page number
        
        # start loop
        while True:
            api_url = f"{BASE_URL}offset={offset}"

        # fetch html
            logging.info(f"Fetching page from url: {api_url}")
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                total_nbr = self.parse_item(response)            

                offset += 60
                if (offset > total_nbr):
                    logging.info("Reached the last page. Ending crawl.") 
                    break
                logging.info(f"Moving to next page: {offset}")
            else:
                logging.info("Failed to fetch response. Retrying...")
                break


    def parse_item(self, response):
        """Extract property/car listing links and basic details.sel = Selector(html)"""

        sel = Selector(response.text)  

        PRODUCT_XPATH = "//div[@class='car-col']"
        PRODUCT_LINK_XPATH = ".//a/@href"
        PRODUCT_PRICE_XPATH = ".//div[@class='price']/a/text()"   
        DISCRIPTION_XPATH = "//div[@class='info']/text()"

        # Select all listing containers
        product_list = sel.xpath(PRODUCT_XPATH)

        for product in product_list:

            # product URL
            product_link = product.xpath(PRODUCT_LINK_XPATH).get()
            if product_link:
                # if already starts with https:// dont add the host address
                if not product_link.startswith("https://"):
                    product_link = "https://www.beverlyhillscarclub.com" + product_link.strip() # complete URL
                else:
                    product_link = product_link.strip()

            else:
                product_link = None

            # skip if url already captured
            if product_link in self.seen_urls:
                logging.info(f"Skipping duplicate URL: {product_link}")
                continue

            self.seen_urls.add(product_link)

            # price
            price = product.xpath(PRODUCT_PRICE_XPATH).get()
            if price:
                price = price.strip()
            # description
            description = product.xpath(DISCRIPTION_XPATH).get()
            if description:
                description = description.strip()
            

            item = {}
            item['url'] = product_link
            item['price'] = price
            item['description'] = description
            
            product_item = ProductUrlItem(**item)
            product_item.save()

        total_nbr = response.text.strip().split('\n')[0].split()[0]
        total_nbr = int(total_nbr)
        return total_nbr  

    def close(self):
        """Close function for all module object closing"""
        
        logging.info(f"Closing DB connection...")
        self.mongo.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
