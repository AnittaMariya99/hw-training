from parsel import Selector
import json
import time
import html as html_module
import math
import logging
from curl_cffi import requests
from lxml import html
from urllib.parse import urljoin
# from mongoengine import connect
from settings import (BASE_URL,API_URL,HEADERS,PAGE_SIZE,MONGO_DB,MONGO_URI,MONGO_COLLECTION_RESPONSE)
from items import ProductResponseItem
from pymongo import MongoClient

class Crawler:
    """Crawler for FirstWeber Agents"""

    def __init__(self):
        logging.info("Initializing crawler...")

        # MongoEngine connection
        # self.mongo=connect(db=MONGO_DB,host=MONGO_HOST,port=MONGO_PORT,alias="default")
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]


    
    def start(self):

        page_number = 1

        while True:

            logging.info(f"Fetching page {page_number}...")

            params = {
                "layoutID": 1126,
                "pageSize": PAGE_SIZE,
                "pageNumber": page_number,
                "sortBy": "firstname",
            }

            response = requests.get(API_URL,headers=HEADERS,params=params,impersonate="chrome")

            if response.status_code == 200:
                # Parse items
                total_pages = self.parse_item(response)
                
                if (total_pages < page_number):
                    break

                page_number += 1
                
            else:
                logging.error(f"Category API failed {response.status_code} - {response.text}")
                break
                    
        logging.info("Completed fetching agents")


    def parse_item(self, response):
        """parse item urls, save to DB and calculate total pages and returns total pages"""
        # Double JSON decoding (API quirk)
        data = json.loads(response.text)
        if isinstance(data, str):
            data = json.loads(data)

        html_content = html_module.unescape(data.get("Html", ""))
        total_count = data.get("TotalCount", 0)

        sel = Selector(html_content)
        urls = sel.xpath('//a[@class="button hollow"]/@href').getall()
        urls = [urljoin(BASE_URL, u) for u in urls]

        for u in urls:
            # ProductResponseItem(url=u).save()
            item = {
                "url": u
            }
            self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)

        return math.ceil(total_count / PAGE_SIZE)


    def close(self):
        logging.info("Crawler finished.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
