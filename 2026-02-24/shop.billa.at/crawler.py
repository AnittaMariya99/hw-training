from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_PRODUCTS, CRAWLER_HEADERS, BASE_URL
from pymongo import MongoClient
import logging
from curl_cffi import requests
from items import ProductUrlItem
from parsel import Selector


class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        self.total_saved = 0
        logging.info("Connected to MongoDB")

    def start(self):
        """Load all category URLs from MongoDB and crawl each one for product URLs."""
        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find({}, {"_id": 0, "url": 1, "name": 1}))
        logging.info(f"Found {len(categories)} categories to crawl.")
        for cat in categories:
            category_url  = cat["url"]
            category_name = cat.get("name", "")
            logging.info(f"Scraping category: {category_name!r} → {category_url}")

            # Fetch page 1
            response = requests.get(category_url, headers=CRAWLER_HEADERS, impersonate="chrome")
            logging.info(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                logging.warning(f"  Skipping – unexpected status {response.status_code}")
                continue

            # Detect total pages inline
            sel = Selector(response.text)
            total_pages = 1
            for href in sel.xpath('//a[contains(@href, "?page=")]/@href').getall():
                try:
                    page_num = int(href.split("?page=")[-1].split("&")[0])
                    if page_num > total_pages:
                        total_pages = page_num
                except ValueError:
                    pass
            logging.info(f"  Detected {total_pages} page(s).")

            # Parse page 1
            products = self.parse_item(response, category_name=category_name, category_url=category_url)
            logging.info(f"  Page 1....{len(products)} products")

            # Parse pages 2..N
            for page in range(2, total_pages + 1):
                paged_url = f"{category_url}?page={page}"
                response  = requests.get(paged_url, headers=CRAWLER_HEADERS, impersonate="chrome")

                if response.status_code != 200:
                    logging.warning(f"  Page {page} returned {response.status_code} – stopping pagination.")
                    break

                page_products = self.parse_item(response, category_name=category_name, category_url=category_url)
                logging.info(f"  Page {page} → {len(page_products)} products")

                if not page_products:
                    logging.info("  No products on this page – stopping pagination.")
                    break

                products.extend(page_products)

            logging.info(f"   Total unique products saved for this category: {len(products)}")

        logging.info(f"Done – {self.total_saved} product URLs saved to MongoDB.")

    def parse_item(self, response, category_name: str, category_url: str) -> list:
        """
        Parse a category page response, save each product to MongoDB,
        and return a list of product dicts.
        """
        sel       = Selector(response.text)
        products  = []
        seen_urls = set()

        for a in sel.xpath('//a[starts-with(@href, "/produkte/")]'):
            href = a.xpath("./@href").get("")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            url = BASE_URL + href
            if self.mongo[MONGO_COLLECTION_PRODUCTS].find_one({"url": url}):
                continue

            name = a.xpath(".//h3/text()").get("").strip()
            if not name:
                name = a.xpath("normalize-space(.)").get("").strip()
            if not name:
                continue

            item = {}
            item["name"] = name
            item["url"]  = url
            item["slug"] = href.replace("/produkte/", "")
            item["category_name"] = category_name
            item["category_url"]  = category_url

            product_item = ProductUrlItem(**item)
            product_item.validate()
            self.mongo[MONGO_COLLECTION_PRODUCTS].insert_one(item)
            self.total_saved += 1
            logging.info(f"    Saved: {item['name']} -> {item['url']}")

            products.append(item)

        return products

    def close(self):
        """Close the MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
