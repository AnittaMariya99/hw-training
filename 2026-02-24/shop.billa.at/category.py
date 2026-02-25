from curl_cffi import requests
from settings import MONGO_URI,MONGO_DB,CATEGORY_URL,MONGO_COLLECTION_CATEGORY, BASE_URL,CATEGORY_HEADERS
import logging
from pymongo import MongoClient
from parsel import Selector
from items import CategoryUrlItem



class CategoryCrawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        self.total_saved = 0


    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        response = requests.get(CATEGORY_URL, headers=CATEGORY_HEADERS, impersonate="chrome")
        logging.info(f"Response status: {response.status_code}")

        if response.status_code != 200:
            logging.error("Failed to load the category page.......")
            return

        # Level 1 – top-level categories
        top_level = self.parse_item(response, parent_slug=None)
        logging.info(f"Found {len(top_level)} top-level categories.")

        for top_cat in top_level:

            # Level 2 – sub-categories
            res2 = requests.get(top_cat["url"], headers=CATEGORY_HEADERS, impersonate="chrome", timeout=15)
            subs = self.parse_item(res2, parent_slug=top_cat["slug"])
            

            if not subs:
                self._save(top_cat)
                continue

            for sub in subs:

                # Level 3 – sub-sub-categories
                res3 = requests.get(sub["url"], headers=CATEGORY_HEADERS, impersonate="chrome")
                sub_subs = self.parse_item(res3, parent_slug=sub["slug"])
                

                if not sub_subs:
                    self._save(sub)
                    continue

                for sub_sub in sub_subs:

                    # Level 4 – leaf categories
                    res4 = requests.get(sub_sub["url"], headers=CATEGORY_HEADERS, impersonate="chrome")
                    leaves = self.parse_item(res4, parent_slug=sub_sub["slug"])
                    

                    if not leaves:
                        self._save(sub_sub)
                    else:
                        for leaf in leaves:
                            self._save(leaf)

        logging.info(f"Done – {self.total_saved} leaf categories saved to MongoDB.")

    def parse_item(self, response, parent_slug=None):
        """
        Parse a category page and return a list of category dicts.
        Skips any link that points back to the parent (self-referencing links).
        """
        sel = Selector(response.text)
        categories = []
        seen_urls = set()

        for a in sel.xpath('//a[@class="ws-category-tree-navigation-button ws-btn ws-btn--secondary-link ws-btn--large"]'):
            href = a.xpath("./@href").get("")
            if not href.startswith("/kategorie/"):
                continue

            slug = href.replace("/kategorie/", "")

            # skip self-referencing link back to the parent
            if slug == parent_slug:
                continue

            url = BASE_URL + href
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # BILLA renders names like "Obst & Gemüse323" – strip the trailing count
            raw_text = a.xpath("normalize-space(.)").get("")
            i = len(raw_text)
            while i > 0 and raw_text[i - 1].isdigit():
                i -= 1
            name = raw_text[:i].strip()
            count_str = raw_text[i:].strip()
            count = int(count_str) if count_str.isdigit() else None

            if not name:
                continue

            item = {}
            item["name"] = name
            item["url"] = url
            item["slug"] = slug
            item["product_count"] = count
            item["parent_slug"] = parent_slug
            categories.append(item)

        return categories

    def _save(self, item):
        """Validate and insert a leaf category into MongoDB."""
        category_item = CategoryUrlItem(**item)
        category_item.validate()
        self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
        self.total_saved += 1
        logging.info(f"Saved: {item['name']} = {item['url']}")



    def close(self):
        """Close the MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()
    





