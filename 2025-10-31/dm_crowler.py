import requests
import random
from pymongo import MongoClient
import time
import requests

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.dm.at',
    'priority': 'u=1, i',
    'referer': 'https://www.dm.at/',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    'x-dm-product-search-tags': 'presentation:grid;search-type:editorial;channel:web',
    'x-dm-product-search-token': '47566286405181',
}


response = requests.get('https://product-search.services.dmtech.com/at/search/static', headers=headers)

def extract_and_store_urls(api_base_url):
    """
    Extracts product URLs from paginated API results and stores them in MongoDB.
    """
    print("inside the function done")
    # Step 1: Connect to MongoDB
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["dm_products"]
        collection = db["product_urls"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f" MongoDB connection error: {e}")
        return
    
    print("db conection established")
    page = 0
    total_links = 0

    while True:
        api_url = f"{api_base_url}&currentPage={page}"
        print(f"api_url is={api_url}")
        print(f"\n Fetching Page {page} ...")

        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Failed to fetch API data (Page {page}): {e}")
            break

        # Step 2: Extract product data
        products = data.get("products", [])
        
        if not products:
            print(f" No more products found. Stopping at page {page}.")
            break

    
        product_details = []

        for product in products:
            tile_data = product.get("tileData", {})
            gtin = product.get("gtin", None)
            brand_name = product.get("brandName", None)
            title = product.get("title", None)
            self_link = tile_data.get("self", None)
            value= tile_data.get("price", {}).get("price", {}).get("current", {}).get("value", None)

            if self_link:
                product_url = f"https://www.dm.at/product{self_link}"
# insert many kodukum,sprrd kootan ,insert one  
                # Store all data in one dictionary
                product_info = {
                    "url": product_url,
                    "brandName": brand_name,
                    "title": title,
                    "gtin": gtin,
                    "price": value
                }
                product_details.append(product_info)

        if not product_details:
            print(f" No valid products found on page {page}.")
            break

        print(f" Found {len(product_details)} products on page {page}")

        # Step 4: Store product details in MongoDB
        for item in product_details:
            # instet
            collection.update_one(  
                {"url": item["url"]},     # unique identifier
                {"$set": item},           # store all product fields 

                upsert=True
            )

        total_links += len(product_details)


        # Step 5: Check if next page exists
        finalout = data.get("totalPages",page)
        
        if page >=finalout :
            print(" Reached last page.")
            break

        # Delay to be polite to the server
          # Step 6: Apply random delay between 2–3 seconds
        delay = random.uniform(2, 3)
        print(f"Waiting {delay:.2f} seconds before next page...")
        time.sleep(delay)
        
        page += 1

    print(f"\n Completed! Total product URLs saved: {total_links}")
    print(" MongoDB Database: dm_products | Collection: product_urls")


print("before function call")    
base_api_url = "https://product-search.services.dmtech.com/at/search/static?isNew=true&popularFacet=Neu&pageSize=10&searchType=editorial-search&sort=new&type=search-static"
extract_and_store_urls(base_api_url)
print("extracted methode is completed")
