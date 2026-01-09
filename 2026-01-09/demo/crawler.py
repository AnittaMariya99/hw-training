import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, BASE_URL


class Crawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]

        # ✅ FIX: track already-seen URLs
        self.seen_urls = set()

    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------
    def start(self):
        page_number = 1
        logging.info("\nStarting Classic Cars Crawler...\n")

        api_url = f"{BASE_URL}?p={page_number}"

        while True:
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
                logging.error("Failed to fetch response. Stopping crawler.")
                break

    # ---------------------------------------------------------
    # PARSE ITEMS
    # ---------------------------------------------------------
    def parse_item(self, response):
        """Extract car listing links and basic details"""

        sel = Selector(response.text)

        PRODUCT_XPATH = "//div[contains(@class,'flexbox') and contains(@class,'panel-mod')]"
        PRODUCT_LINK_XPATH = ".//div[contains(@class,'fi-sritem-col-1')]//a/@href"
        PRODUCT_IMAGE_XPATH = ".//div[contains(@class,'fi-sritem-col-1')]//img/@data-src"
        PRODUCT_TITLE_XPATH = ".//div[contains(@class,'h-sri-car-title')]/text()"
        PRODUCT_PRICE_XPATH = ".//div[contains(@class,'mrg-b-sri-price')]//span/text()"
        LAST_PAGE_XPATH = "//div[@class='b w100 mrg-b-lg text-center']/span[@class='red'][3]/text()"
        DESCRIPTION_XPATH = "//div[@class='fs-12 height-rw h-sri-desc-text mrg-b-xs no-overflow']/text()"

        product_list = sel.xpath(PRODUCT_XPATH)

        for product in product_list:

            # ---------------- URL ----------------
            product_link = product.xpath(PRODUCT_LINK_XPATH).get()
            if not product_link:
                continue

            if not product_link.startswith("https://"):
                product_link = "https://classiccars.com" + product_link.strip()
            else:
                product_link = product_link.strip()

            # skip duplicates
            if product_link in self.seen_urls:
                logging.info(f"Skipping duplicate URL: {product_link}")
                continue

            self.seen_urls.add(product_link)

            # ---------------- DATA ----------------
            image_url = product.xpath(PRODUCT_IMAGE_XPATH).get()

            title = product.xpath(PRODUCT_TITLE_XPATH).get()
            title = title.strip() if title else None

            price = product.xpath(PRODUCT_PRICE_XPATH).get()
            price = price.strip() if price else None

            description = product.xpath(DESCRIPTION_XPATH).get()
            description = description.strip() if description else None

            item = {
                "url": product_link,
                "image_url": image_url,
                "title": title,
                "price": price,
                "description": description,
            }

            try:
                self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)
            except Exception as e:
                logging.exception(f"Failed to insert item into MongoDB: {e}")

        last_page_number = sel.xpath(LAST_PAGE_XPATH).get()
        return int(last_page_number.replace(".", "").strip())

    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        logging.info("Closing DB connection...")
        self.mongo_client.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(message)s"
    )

    crawler = Crawler()
    crawler.start()
    crawler.close()
