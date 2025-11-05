import requests
from parsel import Selector
url="https://content.services.dmtech.com/rootpage-dm-shop-de-at?view=navigation&mrclx=false"
from pymongo import MongoClient
import random
import time

import requests

def extract_and_store_urls(api_base_url, category_title):
    """
    Extracts product URLs from paginated API results and stores them in MongoDB.
    """
    print("inside the function done")
    # Step 1: Connect to MongoDB
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["dm_products"]
        collection = db["cat_product_details"]
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
                    "price": value,
                    "category": category_title
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

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://www.dm.at',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.dm.at/',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
}

data = requests.get(url).json()

# Step 1: Go to navigation → children
nav_children = data["navigation"]["children"]

# Step 2: Get the 1st category (Make-up)
makeup_category = nav_children[2]

# Step 3: Get sub-category (Augen Make-up)
eye_makeup_category = makeup_category["children"][0]

# Step 4: Get 1st child from that list
target_item = eye_makeup_category["children"][0]  # (0 = first, 1 = second)
category_list = []

# Step 4: Loop through ALL children and fetch title, link, id
print("\n Extracting Categories....")
for category in eye_makeup_category.get("children", []):
    title = category.get("title")
    link = category.get("link")
    id_ = category.get("id")
    category_list.append({
        "title": title,
        "link": link,
        "id": id_
    })

#  Step II: Get all category id for each category
print("\n Extracting category ids ......")
for category in category_list:
    # Step II.1 Construct URL to get category id
    #https://content.services.dmtech.com/rootpage-dm-shop-de-at/make-up/augen-make-up/lidschatten-primer-und-base?mrclx=false
    cat_url=f"https://content.services.dmtech.com/rootpage-dm-shop-de-at{category['link']}?mrclx=false"
    # Step II.2 Call this URL
    cat_response = requests.get(cat_url).json()
    # Step II.3 Extract category id from the response
    category_id = next(item["query"]["filters"].split(":")[1] for item in cat_response["mainData"] if item.get("type") == "DMSearchProductGrid")
    # Step II.4 save in a list
    category["categoryId"] = category_id

print("\n Getting product list for each categories....")
# Step III: Get the product list for each category id
for category in category_list:
    print(f"\n Getting product list for category '{category["title"]}'....")
    #Step III.1 Construct URL to get product list
    #https://product-search.services.dmtech.com/at/search/static?allCategories.id=010102&pageSize=30&searchType=editorial-search&sort=editorial_relevance&type=search-static
    product_link = f"https://product-search.services.dmtech.com/at/search/static?allCategories.id={category["categoryId"]}&pageSize=30&searchType=editorial-search&sort=editorial_relevance&type=search-static"
    #Step III.2 Call the product url 
    extract_and_store_urls(product_link, category["title"])


# Step IV : Save the product list for each category to DB 

