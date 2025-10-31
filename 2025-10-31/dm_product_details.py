import requests
from pymongo import MongoClient
import time

# --- Headers from your curl command ---
headers = {
    'sec-ch-ua-platform': '"Android"',
    'Referer': 'https://www.dm.at/',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'x-dm-version': '2025.1029.56893-x',
    'sec-ch-ua-mobile': '?1'
}

# --- Connect to MongoDB ---
client = MongoClient("mongodb://localhost:27017/")
db = client["dm_products"]
collection = db["product_urls"]

# --- Read all documents having gtin field ---
products = collection.find({"gtin": {"$exists": True, "$ne": None}})

print(f" Total products found with GTIN: {collection.count_documents({'gtin': {'$exists': True, '$ne': None}})}")

# --- Loop through each product and fetch details ---
for product in products:
    gtin = product.get("gtin")
    if not gtin:
        continue

    api_url = f"https://products.dm.de/product/products/detail/AT/gtin/{gtin}"
    print(f"\n Fetching details for GTIN: {gtin}")
    print(f" API: {api_url}")

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extract selected fields (you can expand as needed)
        details = {
            "gtin": gtin,
           
            "brand": data.get("brand", {}).get("name"),
           "breadcrumbs":data.get("breadcrumbs", []),
        }

        # Print details (for debugging)
        print(details)

        # --- Save new fields into same MongoDB document ---
        collection.update_one(
            {"gtin": gtin},
            {"$set": details},
            upsert=True
        )

    except Exception as e:
        print(f" Error fetching details for {gtin}: {e}")

    # Small polite delay between requests
    time.sleep(2)

print("\n All product details fetched and stored successfully!")
