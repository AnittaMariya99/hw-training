import logging
import json
from curl_cffi import requests
# from items import ProductCategoryUrlItem
from settings import BASE_URL, HEADERS, MONGO_DB, API_URL,MONGO_URI,MONGO_COLLECTION_CATEGORY
# from mongoengine import connect
from pymongo import MongoClient


class Crawler:
    def __init__(self):
        """Initialize MongoDB connection"""
        
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]


    def start(self):
        """Fetch categories and begin parsing"""
        logging.info("Fetching homepage to extract categories...")
        response = requests.get(API_URL,headers=HEADERS,impersonate="chrome120",timeout=20)
        logging.error(f"Category API request failed: {response.status_code}")
        if response.status_code == 200:
            # Parse items
            self.parse_item(response)
        else:
            logging.error(f"Category API failed {response.status_code} - {response.text}")
    
        logging.info("Category crawling completed")

    def parse_item(self, response):
        """Convert flat menu list → nested hierarchy and save"""

        data = response.json()
    
        menu = data.get("menu", [])
        if not isinstance(menu, list):
            logging.error("Menu format invalid")
        logging.info("Fetched category menu (%d items)", len(menu))

        nodes = {}
        roots = []

        # Create nodes dictionary
        for item in menu:
            pk = item.get("pk")
            if pk is None:
                continue  # skip invalid items

            nodes[pk] = {
                "label": item.get("label", ""),
                "url": item.get("url"),
                "level": item.get("level"),
                "parent_pk": item.get("parent_pk"),
                "children": []
            }

        # Link parent → children
        for pk, node in nodes.items():
            parent = node["parent_pk"]
            if parent in nodes:
                nodes[parent]["children"].append(node)
            else:
                roots.append(node)

        # Save hierarchy
        for cat in roots:
            url_path = cat.get("url")

            # Save only if URL exists
            if url_path:
                full_url = BASE_URL.rstrip("/") + url_path

                try:
                    # ProductCategoryUrlItem(
                    #     url=full_url,
                    #     label=cat.get("label"),
                    #     level=str(cat.get("level")),
                    # ).save()

                    self.mongo[MONGO_COLLECTION_CATEGORY].insert_one({
                        "url": full_url,
                        "label": cat.get("label"),
                        "level": str(cat.get("level")),
                    })

                    logging.info(
                        "Saved category URL: %s (level %s)",
                        full_url,
                        cat.get("level"),
                    )
                except Exception as e:
                    logging.error(f"Mongo save failed for {full_url}: {e}")

            # # Recursively save children
            # if cat.get("children"):
            #     self.save(cat["children"], indent + 4)
        

    def close(self):
        logging.info("MongoDB connection closed")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()