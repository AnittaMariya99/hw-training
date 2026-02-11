from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE
from pymongo import MongoClient
import logging
from curl_cffi import requests
session = requests.Session()
from items import ProductUrlItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")
        


    def start(self):
        """Iterate through categories and fetch products"""
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.ah.nl/producten',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }
        
        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Loaded {len(categories)} categories from DB")

        for category in categories:
            category_id=category.get("category_id", "")
            category_slug=category.get("category_slug", "")
           

            if not category_id or not category_slug:
                continue

            page = 1
            PAGE_SIZE = 36
            total_pages = 1
            while page <= total_pages:
                logging.info(f"Fetching page {page} for {category_slug}")
                PLP_API_URL = f"https://www.ah.nl/zoeken/api/products/search?page={page}&size={PAGE_SIZE}&taxonomySlug={category_slug}&taxonomy={category_id}"
                response = session.get(PLP_API_URL, headers=headers, impersonate="firefox")
                
                logging.info(response.status_code)

                if response.status_code == 200:
                    total_pages = self.parse_item(response)

                if page > total_pages:
                    break

                page += 1   


    def parse_item(self, response):
        """Extract product details and save to DB"""
        
        response_json = response.json()
        total_pages = response_json.get('page', {}).get('totalPages', 1)
    
        for card in response_json.get('cards', []):
            products = card.get("products", [])
            if not products:
                continue
            product = products[0]

            product_id = product.get('id')
            product_link = product.get('link')
            product_title = product.get('title')

            logging.info(f"{product_id} : {product_title} - {product_link}")
            item={}
            item["product_id"] = str(product_id)
            item["link"] = product_link
            item["title"] = product_title
            logging.info(f"{product_id} : {product_title} - {product_link}")

            product_item = ProductUrlItem(**item)
            product_item.validate()
            try
            self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)

        return total_pages

    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")
        session.close()
        logging.info("Session closed.")

if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()


