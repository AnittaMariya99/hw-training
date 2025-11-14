import requests
from parsel import Selector
from pymongo import MongoClient
import time

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["lidl"]
source_collection = db["lidl_products"]         # URLs collection

# Headers (simulate a browser)
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.lidl.co.uk/',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}

def extract_product_details(url):
    """Scrape product details from a Lidl product page."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f" Failed ({response.status_code}): {url}")
            return None

        sel = Selector(response.text)

        brand = sel.xpath("//a[@class='heading__brand']/text()").get()
        name = sel.xpath("//h1[@class='heading__title']/text()").get()
        price = sel.xpath("//div[@class='ods-price__value']/text()").get()
        price_per_unit = sel.xpath("//div[@class='ods-price__footer']/text()").get()
        product_id = sel.xpath("//span[@class='product-id__number']/text()").get()
        

        product_data = {
            "url": url,
            "brand": brand.strip() if brand else None,
            "name": name.strip() if name else None,
            "price": price.strip() if price else None,
            "price_per_unit": price_per_unit.strip() if price_per_unit else None,
            "product_id": product_id.strip() if product_id else None,
       
        }

        return product_data

    except Exception as e:
        print(f" Error scraping {url}: {e}")
        return None


def scrape_all_products():
    """Fetch all URLs from DB, scrape details, and store results."""
    all_urls = source_collection.find({ "product_id": { "$exists": False } }, {"product_url": 1, "_id": 0})
    total = source_collection.count_documents({})
    print(f"\n Found {total} product URLs to process.\n")

    count = 0
    for item in all_urls:
        url = item["product_url"]

        print(f"🔹 Scraping: {url}")
        details = extract_product_details(url)

        if details:
            source_collection.update_one(
                {"product_url": url},
                {"$set": details},
                upsert=True
            )
            print(f" Saved: {details['name'] or 'Unnamed Product'}")
        else:
            print(f" Failed to scrape: {url}")

        count += 1
        time.sleep(1)  # avoid rate limit

    print(f"\n Completed! Total processed: {count}\n")


if __name__ == "__main__":
    scrape_all_products()

