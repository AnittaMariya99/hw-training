import requests
import logging
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, CATEGORY_URL, MONGO_COLLECTION_CATEGORY, BASE_URL, CATEGORY_HEADERS
from items import CategoryUrlItem

class CategoryCrawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]

    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        response = requests.get(CATEGORY_URL, headers=CATEGORY_HEADERS)
        logging.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            self.parse(response)

    def parse(self, response):
        """Extract category links and basic details"""
        data = response.json()
        nav_items = data["navigation"]["children"]

        categories = []
        stack = [(nav_items, "")]

        while stack:
            items, parent = stack.pop()
            for item in reversed(items):
                if item.get("hidden") or item.get("externalLink"):
                    continue

                name = item.get("title", "")
                link = item.get("link", "")
                url = BASE_URL + link if link and link.startswith("/") else link if link else ""
                children = item.get("children", [])
                path = f"{parent} > {name}" if parent else name
                category_id = item.get("id", "")

                if not children:
                    categories.append({"path": path, "name": name, "url": url, "category_id": category_id, "link":link})
                else:
                    stack.append((children, path))

        logging.info(f"Found {len(categories)} visible leaf categories")

        for cat in categories:                              # ✅ loop over all categories
            item = {}
            item["name"] = cat["name"]
            item["slug"] = cat["link"]
            item["link"] = cat["url"]
            item["category_id"] = cat["category_id"]
            product_item = CategoryUrlItem(**item)
            product_item.validate()
            self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)

    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()