import requests
import json
from parsel import Selector
from settings import MONGO_URI,MONGO_DB,CATEGORY_URL,MONGO_COLLECTION_CATEGORY,HEADERS,BASE_URL
import logging
from pymongo import MongoClient
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
        response=requests.get(CATEGORY_URL,headers=HEADERS)
        logging.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            self.parse_item(response)
    
    def parse_item(self, response):
        """Extract category links and basic details"""
        sel=Selector(response.text)
        script_tag=sel.xpath("//script[contains(text(),'topmenuparsedData')]/text()").get()
        script_tag = script_tag[script_tag.find(":") + 1: script_tag.rfind("\\n\"])")]
        script_tag = script_tag.replace("\\\"", "\"")


        data = json.loads(script_tag)

        top_menu = None
        search_stack = [data]
        while search_stack:
            current = search_stack.pop()
            if isinstance(current, dict):
                if "topmenuparsedData" in current:
                    potential_menu = current["topmenuparsedData"]
                    # Important: Ensure we found the actual data dictionary, not a string reference
                    if isinstance(potential_menu, dict) and "content" in potential_menu:
                        top_menu = potential_menu
                        break
                # Continue searching nested dictionaries
                for val in current.values():
                    search_stack.append(val)
            elif isinstance(current, list):
                # Continue searching nested lists
                for item in current:
                    search_stack.append(item)

        if top_menu and "content" in top_menu:
            # 1. Find the "Women" entry in the top-level menu list
            women_cat = None
            for item in top_menu["content"]:
                if isinstance(item, dict) and item.get("name") == "Women":
                    women_cat = item
                    break
            
            if women_cat:
                logging.info(f"Leaf categories for: {women_cat['name']}")
                
                # 2. Extract and print only leaf categories iteratively
                items_to_process = []
                
                # Start with the immediate children of "Women"
                if "children" in women_cat and isinstance(women_cat["children"], dict):
                    initial_content = women_cat["children"].get("content", [])
                    for i in range(len(initial_content) - 1, -1, -1):
                        items_to_process.append(initial_content[i])
                    
                while items_to_process:
                    current_item = items_to_process.pop()
                    if not isinstance(current_item, dict):
                        continue
                        
                    # Check if this category has sub-categories
                    sub_content = []
                    if "children" in current_item and isinstance(current_item["children"], dict):
                        sub_content = current_item["children"].get("content", [])
                    
                    # If sub_content is empty, it's a leaf category
                    if not sub_content:
                        name = current_item.get("name")
                        link = current_item.get("link")
                        link=BASE_URL+link
                        id=current_item.get("id")
                        # Print valid leaf names
                        if name and name != "Menu Item":
                            logging.info(f"Name: {name}, Link: {link}, ID: {id}")
                            item={}
                            item["category_name"]=name
                            item["category_url"]=link
                            item["category_id"]=id
                            product_item = CategoryUrlItem(**item)
                            product_item.validate()
                            self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
                    else:
                        # If it has sub-categories, add them to the stack to find their leaves
                        for i in range(len(sub_content) - 1, -1, -1):
                            items_to_process.append(sub_content[i])
            else:
                logging.info("Could not find 'Women' category")
        else:
            logging.info("Could not find topmenuparsedData with content")

    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

        
if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()




