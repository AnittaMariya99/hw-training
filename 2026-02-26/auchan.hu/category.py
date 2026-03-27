import requests
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, CATEGORY_URL, MONGO_COLLECTION_CATEGORY, BASE_URL
import logging
from items import CategoryUrlItem

# Setup logging
logging.basicConfig(level=logging.INFO)

class CategoryCrawler:
    """Crawling Category URLs"""

    def __init__(self):
        """Initialize crawler, DB connection."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        

    def start(self):
        """Fetch category JSON."""
        logging.info(f"Fetching categories from {CATEGORY_URL}")

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        try:
            response = requests.get(CATEGORY_URL, headers=headers)
            logging.info(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                self.parse(response)
            else:
                logging.error(f"Failed to fetch categories: {response.status_code}")
        except Exception as e:
            logging.error(f"Error during category fetching: {e}")

    def parse(self, response):
        """Extract and save all leaf categories to MongoDB."""
        data = response.json()

        def extract(node, path, main_category):
            categories = []
            name = node.get("name", "")
            cat_id = str(node.get("id", ""))
            slug = node.get("slug", "")
            level = node.get("level", -1)

            if level == 0:
                main_category = name

            current_path = f"{path} > {name}" if path else name
            children = node.get("children", [])
            is_leaf = len(children) == 0

            if level != -1 and is_leaf:
                link = f"{BASE_URL}/shop/{slug}.c-{cat_id}" if slug else f"{BASE_URL}/shop/c-{cat_id}"
                categories.append({
                    "name": name,
                    "category_id": cat_id,
                    "category_slug": slug,
                    "link": link,
                    "path": current_path,
                    "is_leaf": is_leaf,
                    "main_category": main_category
                })

            for child in children:
                categories.extend(extract(child, current_path, main_category))

            return categories

        all_categories = extract(data, "", None)
        logging.info(f"Extracted {len(all_categories)} categories.")

        count = 0
        for item in all_categories:
            categoryUrlItem = CategoryUrlItem(**item)
            categoryUrlItem.validate()
            self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
            count += 1

        logging.info(f"Successfully saved/updated {count} categories in MongoDB.")

    def close(self):
        """Close MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()