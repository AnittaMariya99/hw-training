from parsel import Selector
import json
import time
import html as html_module
import math
import logging
from curl_cffi import requests
from urllib.parse import urljoin
from mongoengine import connect
from settings import (BASE_URL, API_URL, HEADERS, PAGE_SIZE, MONGO_DB, MONGO_HOST, MONGO_PORT)
from items import ProductResponseItem

class Crawler:
    """Crawler for Allie Beth Agents"""

    def __init__(self):
        logging.info("Initializing crawler...")

        # MongoEngine connection
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, alias="default")

    def start(self):
        page_number = 1
        
        while True:
            logging.info(f"Fetching page {page_number}...")

            params = {
                "layoutID": 1081,
                "pageSize": PAGE_SIZE,
                "pageNumber": page_number,
                "sortBy": "firstname-asc",
            }

            response = requests.get(API_URL, headers=HEADERS, params=params, impersonate="chrome", timeout=60)

            if response.status_code == 200:
                # Parse items
                total_pages = self.parse_item(response)
                
                if total_pages is None or total_pages < page_number:
                    break

                page_number += 1
                # Small delay to be polite
                time.sleep(1)
            else:
                logging.error(f"API failed {response.status_code} - {response.text}")
                break
                    
        logging.info("Completed fetching agents")

    def parse_item(self, response):
        """parse item urls, save to DB and calculate total pages and returns total pages"""
        URLS_XPATH ='//a[@class="site-roster-card-image-link"]/@href'

        # Double JSON decoding might be needed as per Reliance Network standard quirks
        data = json.loads(response.text)
        if isinstance(data, str):
            data = json.loads(data)

        html_content = html_module.unescape(data.get("Html", ""))
        total_count = data.get("TotalCount", 0)

        if not html_content:
            logging.warning("No HTML content in response")
            return 0

        sel = Selector(html_content)
        # The individual agent links are in h2 tags within articles or cards
        urls = sel.xpath(URLS_XPATH).getall()
        
        # Deduplicate URLs
        urls = list(set(urls))
        #use simple conditional statement to join base url with urls
        urls = [BASE_URL + u if u.startswith("/") else u for u in urls]

        new_urls_count = 0
        for u in urls:
            ProductResponseItem(url=u).save()
            new_urls_count += 1
          
        logging.info(f"Parsed {len(urls)} URLs ({new_urls_count} new) from page. Total count: {total_count}")

        if PAGE_SIZE == 0:
            return 0
            
        return math.ceil(total_count / PAGE_SIZE)

    def close(self):
        logging.info("Crawler finished.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
