from settings import PLP_URL, MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, UA
from pymongo import MongoClient
import logging
import hrequests
import time
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")
        
        # Initialize hrequests session with chrome browser impersonation
        self.session = hrequests.Session(browser='chrome')
        self.tokens = {"user": "__mzrpt__", "app": "__mzrpt__"}
        logging.info("Initialized hrequests session with Chrome impersonation")

    def establish_session(self):
        """Visit homepage to get cookies and extract session tokens"""
        logging.info("Visiting homepage to establish session and tokens...")
        try:
            response = self.session.get('https://www.acehardware.com', timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # Extract x-vol claims from the apicontext script tag
                match = re.search(r'<script type="text/json" id="data-mz-preload-apicontext">(.*?)</script>', html, re.DOTALL)
                if match:
                    api_context = json.loads(match.group(1))
                    headers = api_context.get("headers", {})
                    self.tokens["user"] = headers.get("x-vol-user-claims", "__mzrpt__")
                    self.tokens["app"] = headers.get("x-vol-app-claims", "__mzrpt__")
                    logging.info(f"Extracted tokens: user={self.tokens['user'][:10]}..., app={self.tokens['app'][:10]}...")
                else:
                    logging.warning("Could not find apicontext script tag. Using default tokens.")
                
                logging.info("Session established successfully")
                return True
            else:
                logging.error(f"Failed to load homepage. Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to establish session: {e}")
        return False

    def start(self):
        """Iterate through categories and fetch products"""
        if not self.establish_session():
            logging.error("Could not establish valid session. Exiting.")
            return

        # Fetching categories from MongoDB
        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Loaded {len(categories)} categories from DB")

        for category in categories:
            category_name = category.get('category_name', 'N/A')
            category_id = category.get("category_id")
            
            if not category_id:
                continue

            logging.info(f"Processing category: {category_name} ({category_id})...")

            page_size = 30
            start_index = 0
            page_count = 1
            current_page = 0

            while current_page < page_count:
                logging.info(f"Fetching page {current_page + 1} for category {category_id}...")
                
                filter_str = f"categoryId req {category_id} and tenant~hide-from-search-flag ne Y"

                params = {
                    "query": "",
                    "filter": filter_str,
                    "facetTemplate": f"categoryId:{category_id}",
                    "pageSize": page_size,
                    "startIndex": start_index
                }
                
                headers = {
                    'accept': 'application/json',
                    'accept-language': 'en-US,en;q=0.9',
                    'x-vol-tenant': '24645',
                    'x-vol-site': '37138',
                    'x-vol-user-claims': self.tokens["user"],
                    'x-vol-app-claims': self.tokens["app"],
                    'referer': f'https://www.acehardware.com/search?query={category_id}'
                }

                try:
                    response = self.session.get(PLP_URL, params=params, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if current_page == 0:
                            page_count = data.get("pageCount", 1)
                            total_count = data.get("totalCount", 0)
                            logging.info(f"Category {category_id}: Found {total_count} products across {page_count} pages")

                        items = data.get("items", [])
                        if not items:
                            break

                        self.parse_item(items, category_name)

                        current_page += 1
                        start_index += page_size
                        time.sleep(1) # Delay between pages
                    elif response.status_code in [401, 403]:
                        logging.error(f"Auth error {response.status_code} for category {category_id}. Trying to refresh session...")
                        if self.establish_session():
                            continue # Retry current page with new tokens
                        else:
                            break # Give up on this category if session can't be refreshed
                    else:
                        logging.error(f"Failed to fetch page. Status: {response.status_code}")
                        break
                except Exception as e:
                    logging.error(f"Error fetching products for category {category_id}: {e}")
                    break

    def parse_item(self, items, category_name):
        """Extract product details and save to DB"""
        for product_data in items:
            product_id = product_data.get("productCode", "")
            if not product_id:
                continue

            content = product_data.get("content", {})
            product_name = content.get("productName", "")

            url = f"https://www.acehardware.com/departments/{product_id}"

            item = {
                "url": url,
                "product_id": product_id,
                "product_name": product_name,
                "category_name": category_name,
                "scraped_at": time.time()
            }

            
            self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)
           

    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":

    crawler = Crawler()
    
    crawler.start()
   
    crawler.close()
