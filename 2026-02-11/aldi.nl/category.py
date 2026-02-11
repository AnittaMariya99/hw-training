import requests
from settings import MONGO_URI,MONGO_DB,CATEGORY_URL,MONGO_COLLECTION_CATEGORY, BASE_URL
import logging
from pymongo import MongoClient
from parsel import Selector
from items import CategoryUrlItem
session = requests.Session()
import json


class CategoryCrawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
       

    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")
        response = session.get(CATEGORY_URL)
        if response.status_code == 200:
            self.parse(response)
        else:
            logging.error("Failed to fetch homepage")   



    def parse(self, response):
        """Parsing response to extract category names."""
        logging.info("Parsing response to extract category names...")
        sel=Selector(response.text)
        script_data=sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        data = json.loads(script_data)
        side_drawer = data.get("props",{}).get("pageProps",{}).get("page",{}).get("header",{}).get("0",{}).get("sideDrawerNavigation",[])
        for item in side_drawer:
            for key, value in item.items():
                if isinstance(value, dict) and "children" in value:
                    categories = value.get("children", [])
                    for cat in categories:
                        cat_label = cat.get("label")
                        cat_path = cat.get("path")
                        cat_full_url = BASE_URL + cat_path if cat_path else ""
                        
                        sub_categories = cat.get("children", [])
                        if sub_categories:
                            for sub_cat in sub_categories:
                                sub_label = sub_cat.get("label")
                                sub_path = sub_cat.get("path")
                                sub_full_url = BASE_URL + sub_path if sub_path else ""
                                print(f'category "{cat_label}", url: "{cat_full_url}", sub category "{sub_label}", url: "{sub_full_url}"')  


                                item={}
                                item["name"] = cat_label
                                item["link"] = cat_full_url
                                item["sub_name"] = sub_label
                                item["sub_link"] = sub_full_url    
                                product_item = CategoryUrlItem(**item)
                                product_item.validate()
                                self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
                                logging.info(f"Saved category: {product_item}") 


    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

        
if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()

        
