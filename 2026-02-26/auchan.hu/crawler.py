import requests
import json
import re
import unicodedata
import logging
from pymongo import MongoClient
from items import ProductUrlItem
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_PRODUCTS, CRAWLER_API_URL


class ProductCrawler:

    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB") 

    def start(self):
        logging.info("Fetching leaf categories from MongoDB...")
        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Found {len(categories)} leaf categories.")
        
        total_products_count = 0
        for i, category_doc in enumerate(categories):
            logging.info(f"Processing category {i+1}/{len(categories)}: {category_doc.get('name')} (ID: {category_doc.get('category_id')})")

            category_id = category_doc.get("category_id")
            category_name = category_doc.get("name")
            main_category = category_doc.get("main_category")
            
            cat_products_count = 0
            page = 1
            items_per_page = 16
            
            headers = {
                'accept': 'application/json',
                'accept-language': 'hu',
                'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI4cG1XclQzWmxWMUFJbXdiMUhWYWE5T1BWSzkzcjhIcyIsImp0aSI6IjU0NDQ4N2RlOTM3N2FmODhjYTNiZTAzOTRiYmMwNDBjZmZiYzE0YTllZjA4YTI0ZTAyNDA3MTMwZjE5Y2M1ZjVhNTUxODRlNjMyOWQ3OGQyIiwiaWF0IjoxNzcyMzk4NDcxLjE1MDExMiwibmJmIjoxNzcyMzk4NDcxLjE1MDExNSwiZXhwIjoxNzcyNDg0ODcxLjEyMzYyNSwic3ViIjoiYW5vbl82OWUyMjlmMS1kODZlLTQ3MDAtYTVlNC0yMjFmZDk3ZDFlYzQiLCJzY29wZXMiOltdfQ.SuHMpJraccCj8gIvdvJHLr7RbnWTVFpzQOrHCdocSI5Qu8bNopNV47ULpgilMVuP9j4pkucpL4C6nEeBkGNGmUP5MpZPdYOhZe3o_8QDaVKpmIt8o_gKlw04ncl7j2qBF_IqB_ZO0wOxBT96Rsf7TEIE1BzPjG3PgLSJmNwAWYHyqnwAMK0uj2GZs4LOoTD6TzZPVWiafVSEli_AFOZ_-YV0XiZmltRq1apKWHgsqlUWQo0zFQcD3K5m7NG0ZAUINDax9X3Ke93QpZQNoLN5lKJRgBIozfmLAJu-ZwN4giWqziAsjzzFFu898A-wxhbDicl6ITfs3hLT4c6e6zprIw',
                'if-none-match': 'W/"db42749904b65fd22033b76fe0ef017d"',
                'priority': 'u=1, i',
                'referer': 'https://auchan.hu/',
                'sec-ch-ua': '"Chromium";v="145", "Not:A-Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            }
            
            while True:
                params = {
                    'categoryId': category_id,
                    'itemsPerPage': items_per_page,
                    'page': page,
                    'cacheSegmentationCode': 'DS',
                    'hl': 'hu'
                }
                
                try:
                    response = requests.get(CRAWLER_API_URL, headers=headers, params=params)
                    if response.status_code != 200:
                        logging.error(f"Error fetching products for category {category_id}: {response.status_code}")
                        break
                        
                    results, page_products_count, page_count = self.parse(response, category_id, category_name, main_category)
                    if not results:
                        break
                    cat_products_count += page_products_count
                    if page >= page_count:
                        break
                        
                    page += 1
                except Exception as e:
                    logging.error(f"Exception during product fetching for category {category_id}: {e}")
                    break

            logging.info(f"Extracted {cat_products_count} products for this category.")
            total_products_count += cat_products_count
            
        logging.info(f"Finished. Total products processed: {total_products_count}")       

    def parse(self, response, category_id, category_name, main_category):
        data = response.json()
        results = data.get('results', [])
        
        products_count = 0
        for item in results:
            variant = item.get('selectedVariant', {})
            name = variant.get('name')
            sku = variant.get('sku')
            
            if name and sku:
                value = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
                value = re.sub(r'[^\w\s-]', '', value).strip().lower()
                slug = re.sub(r'[-\s]+', '-', value)
                url = f"https://auchan.hu/shop/{slug}.p-{sku}"
                
                product_item = {
                    "name": name,
                    "url": url,
                    "sku": sku,
                    "category_id": category_id,
                    "category_name": category_name,
                    "main_category": main_category
                }
                
                productUrlItem = ProductUrlItem(**product_item)
                productUrlItem.validate()
                self.mongo[MONGO_COLLECTION_PRODUCTS].insert_one(product_item)
                products_count += 1
        
        page_count = data.get('pageCount', 1)
        return results, products_count, page_count

    def close(self):
        self.mongo_client.close()
        logging.info("Closed MongoDB connection")

if __name__ == "__main__":
    crawler = ProductCrawler()
    crawler.start()
    crawler.close()
