import requests
import time
from pymongo import MongoClient

# Base URL for Lidl UK
base_url = "https://www.lidl.co.uk"

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["lidl"]
collection = db["lidl_products"]  # new collection for product URLs


def fetch_products_url_with_pagination(subcategory):
    """
    Fetch product URLs for a given Lidl subcategory using pagination,
    and save them into MongoDB.
    """
    category_id = subcategory["subcategory_id"]
    base_api_url = "https://www.lidl.co.uk/q/api/search"

    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.lidl.co.uk/",
    }

    product_links = []
    offset = 0
    fetchsize = 12
    page = 1

    print(f"\n🔍 Fetching products for: {subcategory['subcategory_name']} (ID: {category_id})\n")

    while True:
        url = f"{base_api_url}?category.id={category_id}&offset={offset}&fetchsize={fetchsize}&locale=en_GB&assortment=GB&version=2.1.0"

        response = requests.get(url, headers=headers)
        print(f"Page {page} - Status: {response.status_code}")

        if response.status_code != 200:
            print(" Request failed — stopping.")
            break

        data = response.json()
        items = data.get("items", [])

        if not items:
            print(" No more products found. Pagination complete.")
            break

        for item in items:
            canonical_url = item["gridbox"]["data"]["canonicalUrl"]
            full_url = base_url + canonical_url

            product_data = {
                "product_url": full_url,
                "subcategory_name": subcategory["subcategory_name"],
                "category_id": subcategory["subcategory_id"],
                "category_name": subcategory["category_name"],
            }

            # Avoid duplicates — upsert by product_url
            collection.update_one(
                {"product_url": full_url},
                {"$set": product_data},
                upsert=True
            )

            product_links.append(full_url)
            print(f" Saved: {full_url}")

        offset += fetchsize
        page += 1
        time.sleep(1)  # polite delay to avoid being blocked

    print(f"\n🔹 Total Products Saved for {subcategory['subcategory_name']}: {len(product_links)}\n")
    return product_links
