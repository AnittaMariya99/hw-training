from settings import (MONGO_URI,MONGO_DB,MONGO_COLLECTION_CATEGORY,MONGO_COLLECTION_RESPONSE,BASE_PRODUCT_URL,CRAWLER_HEADERS)
from pymongo import MongoClient
import logging
import requests
from items import ProductUrlItem
import base64
import json


# Required constants (were missing)
BASE_URL = BASE_PRODUCT_URL
PRODUCT_VERSION = "1717"
PAGE_SIZE = 40



logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")

    def start(self):

        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Loaded {len(categories)} categories from DB")

        for category in categories:

            category_name = category.get("category_name", "")
            category_id = category.get("category_id", "")

            if not category_name or not category_id:
                continue

            category_uid = base64.b64encode(category_id.encode()).decode()

            query = """
            query GetProductList($filter: ProductAttributeFilterInput,
                                $pageSize: Int,
                                $currentPage: Int,
                                $sort: ProductAttributeSortInput) {
              products(
                filter: $filter
                pageSize: $pageSize
                currentPage: $currentPage
                sort: $sort
              ) {
                total_count
                page_info {
                  current_page
                  page_size
                  total_pages
                }
                items {
                  id
                  sku
                  name
                  url_key
                  categories {
                    id
                    name
                  }
                }
              }
            }
            """

            current_page = 1
            total_pages = 1

            while current_page <= total_pages:

                variables = {
                    "filter": {
                        "category_uid": {
                            "in": [category_uid]
                        }
                    },
                    "pageSize": PAGE_SIZE,
                    "currentPage": current_page,
                    "sort": {}
                }

                params = {
                    "product_version": PRODUCT_VERSION,
                    "query": query,
                    "operationName": "GetProductList",
                    "variables": json.dumps(variables)
                }

                print(f"\nCategory: {category_name}")
                print(f"Page {current_page} of {total_pages}")

                response = requests.get(BASE_URL,params=params,headers=CRAWLER_HEADERS)
                if response.status_code == 200:
                    total_pages = self.parse_item(response)
                else:
                    logging.error(f"Failed to fetch category: {category_name}")
                    break

                if current_page > total_pages:
                    break

                current_page += 1

    def parse_item(self, response):

        data = response.json()
        products = data["data"]["products"]
        total_pages = products["page_info"]["total_pages"]
       
        


        for product in products["items"]:
            # print(product)

            item = {}
            item["product_id"] = str(product["id"])
            item["name"] = product["name"]
            item["url_key"] =product["url_key"]
            item["url"] = f"https://www.matalanme.com/ae_en/{product['url_key']}"
            

            product_item = ProductUrlItem(**item)
            product_item.validate()
            self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)
         

        return total_pages

    def close(self):
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
