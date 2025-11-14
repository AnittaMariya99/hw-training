import requests
from parsel import Selector
from urllib.parse import urljoin
from pymongo import MongoClient
from fetch_product_url_list import fetch_products_url_with_pagination


# Base URL
url = "https://www.lidl.co.uk"

# Headers to simulate a browser request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.lidl.co.uk/c/food-drink/s10068374',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
}
# Fetch page
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}, Length: {len(response.text)}")
sel = Selector(response.text)

subcategory_htmls = sel.xpath("//ol[@class='n-header__main-navigation n-header__main-navigation--sub']/li/a")

consolidated = []
current_parent = None
base_url = "https://www.lidl.co.uk"

# Extracting all categories & subcategories
for subcategory_html in subcategory_htmls:
    link = subcategory_html.xpath("./@href").get()
    category_name = subcategory_html.xpath("./span/text()").get()
    last_part = link.split("/")[-1] if link else None
    category_id = last_part.replace("h", "") if last_part else None

    # If this is a main category (starts with /c)
    if link and link.startswith("/c"):
        current_parent = {
            "category_name": category_name,
            "category_link": link
        }

    # If this is a subcategory (starts with /h)
    elif link and link.startswith("/h") and current_parent:
        subcategory_data = {
            "category_name": current_parent["category_name"],
            "category_link": urljoin(base_url, current_parent["category_link"]),
            "subcategory_name": category_name,
            "subcategory_link": urljoin(base_url, link),
            "subcategory_id": category_id
        }

        consolidated.append(subcategory_data)

        print(f" Saved: {subcategory_data['subcategory_name']}")

        # Optional — fetch product URLs for that subcategory
        fetch_products_url_with_pagination(subcategory_data)

print("\n====== All Subcategories Saved Successfully ======\n")
print(f"Total saved: {len(consolidated)}")
