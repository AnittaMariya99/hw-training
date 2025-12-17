import logging
from mongoengine import connect
from curl_cffi import requests
from parsel import Selector
from items import CategoryUrlItem
from settings import HOMEPAGE_HEADERS, MONGO_DB, BASE_HOMEPAGE, CATEGORY_URL


class Crawler:
    """Crawling Urls"""

    def __init__(self):
        self.mongo = connect(db=MONGO_DB, host="localhost", alias="default")

    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        response = requests.get(CATEGORY_URL, headers=HOMEPAGE_HEADERS,impersonate='chrome')

        logging.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            self.parse_item(response)

    def parse_item(self, response, meta=None):
        """item part"""
        import json
        sel = Selector(response.text)
        
        # Extract JSON data
        data_json = sel.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if not data_json:
            logging.error("Could not find __NEXT_DATA__ script tag.")
            return

        data = json.loads(data_json)
            
        # Navigate to the relevant slot
        # props > initialState > appReducer > data > slots
        slots = data.get("props", {}).get("initialState", {}).get("appReducer", {}).get("data", {}).get("slots", [])
        
        nav_slot = None
        for slot in slots:
            if slot.get("slotId") == "NavigationBarV2Slot":
                nav_slot = slot
                break
        
        if not nav_slot:
            logging.error("NavigationBarV2Slot not found.")
            return

        # components > [0] > homeMainNavNodes > navNodes
        components = nav_slot.get("components", [])
        if not components:
            logging.error("No components in NavigationBarV2Slot.")
            return

        nav_nodes = components[0].get("homeMainNavNodes", {}).get("navNodes", [])
        
        count = 0
        for main_node in nav_nodes:
            main_link = main_node.get("link", {})
            main_category = main_link.get("linkName")
            main_url = main_link.get("url") # Not used for saving but good to know

            child_nodes = main_node.get("childNavigationNodes", [])
            
            for child in child_nodes:
                links = child.get("links", [])
                if not links:
                    continue
                
                # First element is the Parent Category (Sub Category)
                parent_link = links[0]
                parent_category = parent_link.get("linkName")
                
                # Rest are Sub-Sub Categories -> The actual 'Category' we want
                for sub_link in links[1:]:
                    category_name = sub_link.get("linkName")
                    partial_url = sub_link.get("url")
                    
                    if not category_name or not partial_url:
                        continue

                    # Construct full URL
                    # Ensure we don't have double slashes if partial_url starts with /
                    if partial_url.startswith("/"):
                        # Check if it includes locale or not. Assuming we prepend base if needed.
                        # User example: /c/furniture-bedroom-beds
                        # We want: https://www.homecentre.com/ae/en/c/furniture-bedroom-beds
                        # But we should be careful about double /ae/en if it's there.
                        if partial_url.startswith("/ae/en"):
                            full_url = f"https://www.homecentre.com{partial_url}"
                        else:
                            full_url = f"https://www.homecentre.com/ae/en{partial_url}"
                    elif partial_url.startswith("https"):
                        full_url = partial_url
                    else:
                        full_url = f"https://www.homecentre.com/ae/en/{partial_url}"

                    item = {
                        "category": category_name,
                        "url": full_url,
                        "parent_category": parent_category,
                        "main_category": main_category
                    }
                    
                    print(f"Saving: {item['category']}")
                    
                    
                    # Using save() blindly might fail if duplicates exist based on model constraints
                    # But we handled mongo items update previously.
                    CategoryUrlItem(**item).save()
                    count += 1
                    

        logging.info(f"Categories extraction completed. Saved {count} items.")
        return True

    def close(self):
        """Close function for all module object closing"""

        self.mongo.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()