import requests
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, BASE_URL,CRAWLER_URL
from pymongo import MongoClient
import logging
from items import ProductUrlItem
import re


class Crawler:
    """Crawling Product Urls from Categories"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")

    def start(self):
        """Iterate through categories and fetch products"""

        categories = list(self.mongo[MONGO_COLLECTION_CATEGORY].find())
        logging.info(f"Loaded {len(categories)} categories from DB")

        for category in categories:
            category_name = category.get("name", "")
            category_link = category.get("link", "")
            category_slug = category.get("slug", "")

            print(f"Fetching Category: {category_name}")

            if not category_name or not category_link:
                continue

            connection_url=f"https://content.services.dmtech.com/rootpage-dm-shop-sl-si{category_slug}?mrclx=false"

            response = requests.get(connection_url)
            logging.info(f"Status: {response.status_code} | Category: {category_name}")

            if response.status_code != 200:
                continue

            data = response.json()
            mainData = data.get("mainData", [])
            queryModule = next((obj.get("query") for obj in mainData if obj.get("type") == "DMSearchProductGrid"), {})

            params = {
                'pageSize': queryModule.get("numberOfProducts", {}).get("desktop",""),
                'searchType': 'editorial-search',
                'sort': queryModule.get("sort", ""),
                'type': 'search-static',
                'currentPage': 0,
            }


            query = queryModule.get("queryTerms", "")
            if query:
                params['query'] = query

            if not queryModule.get("queryTerms", ""):
               filters = queryModule.get("filters", "")
               #split with : and take first 2 values
               pattern = r'(\w+):(?:"([^"]+)"|(\S+))'
               matches = re.findall(pattern, filters)

               if not matches:
                   print('no matches')
                   continue
               for key, quoted, unquoted in matches:
                   params[key] = quoted if quoted else unquoted
               
            headers = {
                'sec-ch-ua-platform': '"Linux"',
                'x-dm-product-search-token': '47861029051254',
                'Referer': 'https://www.dm.si/',
                'sec-ch-ua': '"Chromium";v="145", "Not:A-Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'x-dm-product-search-tags': 'presentation:grid;search-type:editorial;channel:web',
            }

            page = 0
            all_products = []                               # ✅ reset per category

            while True:
                params['currentPage'] = page
                response = requests.get(CRAWLER_URL, headers=headers, params=params)
                logging.info(f"Status: {response.status_code} | Category: {category_name} | Page: {page + 1}")

                if response.status_code == 200:
                    total = self.parse(response, all_products)

                    if len(all_products) >= total or total == 0:
                        break

                    page += 1
                else:
                    break                                   

    def parse(self, response, all_products):
        """Extract product details and save to DB"""
        data = response.json()

        products = data.get("products", [])
        total    = data.get("count", 0)

        logging.info(f"Fetched {len(products)} products (total: {total})")

        for p in products:
            name = p.get("title") or ""
            link = p.get("tileData", {}).get("self", "")   
            gtin = p.get("gtin") or ""
            url  = BASE_URL + link if link and not link.startswith("http") else link

            all_products.append({"name": name, "url": url})

            item = {}
            item["name"] = name
            item["url"]  = url
            item["gtin"] = str(gtin)

            product_item = ProductUrlItem(**item)
            product_item.validate()
            self.mongo[MONGO_COLLECTION_RESPONSE].insert_one(item)  

        return total                                       
    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()