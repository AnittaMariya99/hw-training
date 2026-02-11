from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, BASE_PRODUCT_URL
from pymongo import MongoClient
import logging
import requests
session = requests.Session()
from items import ProductUrlItem
from parsel import Selector
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")
        


    def start(self):
        """Iterate through categories and fetch products"""

        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Loaded {len(categories)} categories from DB")

        for category in categories:
            category_sub_name=category.get("sub_name", "")
            category_sub_link=category.get("sub_link", "")

            if not category_sub_name or not category_sub_link:
                continue

            response = session.get(category_sub_link)
            if response.status_code == 200:
                self.parse(response)
            else:
                logging.error(f"Failed to fetch category: {category_sub_name}")
                continue



    def parse(self, response):
        """Extract product details and save to DB"""    
        sel=Selector(response.text)
        script_data=sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        data = json.loads(script_data)
        algolia_results = data.get("props", {}).get("pageProps", {}).get("algoliaState" , {}).get("initialResults", {})
        product_urls = []
        for index in algolia_results.values():
            hits = index.get("results", [{}])[0].get("hits", [])
            for hit in hits:
                # Construct the full URL using the product slug
                slug = hit.get("productSlug")
                if slug:
                    product_id = hit.get("objectID")
                    product_title = hit.get("name")
                    product_link = f"{BASE_PRODUCT_URL}{slug}.html"
                    
                    product_urls.append(product_link)
                    item={}
                    item["product_id"] = str(product_id)
                    item["link"] = product_link
                    item["title"] = product_title
                    logging.info(f"{product_id} : {product_title} - {product_link}")
                    product_item = ProductUrlItem(**item)
                    product_item.validate()
                    self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)



    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")
        session.close()
        logging.info("Session closed.")

if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()

    

              

        

            
          
                