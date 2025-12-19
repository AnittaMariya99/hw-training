import logging
import re
import time
from curl_cffi import requests
from mongoengine import connect
from items import ProductCategoryUrlItem, ProductUrlItem, ProductFailedItem
from settings import BASE_URL, HEADERS, MONGO_DB, MONGO_HOST

ABS_URL_RE = r'\\"absolute_url\\"\s*:\s*\\"([^"]+)\\"'
NEXT_RE = r'<a[^>]+href="([^"]+)"[^>]*>\s*<span class="me-4 hidden lg:inline-block">Next'


class ProductCrawler:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, alias="default")
        logging.info("MongoDB connected")

    def start(self):
        """Iterate over category URLs and crawl products"""
        metas = [{"url": item.url} for item in ProductCategoryUrlItem.objects()]

        for meta in metas:
            page_url = meta.get("url")
            logging.info(f"Crawling category: {page_url}")

            while True:
                
                response = requests.get(page_url, headers=HEADERS, impersonate="chrome120", timeout=25)
                if response.status_code != 200:
                    logging.error(f"FAILED: {page_url} (fetch_failed,not_200)")
                    ProductFailedItem(url=page_url, reason="fetch_failed").save()
                    break

                html = response.text
                has_next, next_href = self.parse_item(html)

                if not has_next:
                    break

                page_url = BASE_URL.rstrip("/") + next_href
                time.sleep(1)

                
        logging.info("Product crawling completed")

    def parse_item(self, html):
        """Extract product URLs and detect pagination"""
        matches = re.findall(ABS_URL_RE, html)
        urls = [BASE_URL.rstrip("/") + u for u in matches]

        for u in urls:
            ProductUrlItem(url=u).save()
            logging.info(f"Saved product URL: {u}")
            

        nxt = re.search(NEXT_RE, html)
        if not nxt:
            return False, None

        next_href = nxt.group(1).replace("&amp;", "&")
        return True, next_href

    def close(self):
        logging.info("MongoDB connection closed")

if __name__ == "__main__":
    crawler = ProductCrawler()
    crawler.start()
    crawler.close()