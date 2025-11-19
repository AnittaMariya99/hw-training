import requests
from parsel import Selector
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["marksandspencer_db"]
db_collection = db["marksandspencer_products"]

def fetch_product_details(product_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.marksandspencer.com/l/women',
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

    try:
        response = requests.get(product_url, headers=headers,)
    except Exception as e:
        print(f" Error fetching url: {e}\n")
        return None

    print(f"Status: {response.status_code}, Length: {len(response.text)}")

    sel = Selector(response.text)
    unique_id = sel.xpath("//p[@style='--typography-gutter-bottom:0.5rem']/text()").getall()[2]
    # print("unique_id:",unique_id)
    Brand_name = sel.xpath("//p[@class='media-0_textSm__Q52Mz brand-title_title__u6Xx5 media-0_strong__aXigV']/text()").get()
    # print("Brand_name:",Brand_name)
    Product_name = sel.xpath("//h1[@class='media-0_headingSm__aysOm']/text()").get()
    # print("Product_name:",Product_name)
    Price = sel.xpath("//p[@class='media-0_headingSm__aysOm']/text()").get()
    # print("Price:",Price)
    select_color = sel.xpath("//p[@class='selector-group_legend__eLGaG']//span/text()").getall()
    select_color = select_color[1] if len(select_color) > 1 else None
    # print("select_color:",select_color)
    Discription = sel.xpath("//p[(@class='media-0_textSm__Q52Mz')]//text()").getall()[1]
    # print("Discription:",Discription)
    review_count = sel.xpath("//div[@class='product-intro_wrapper__hY8v6']//span[@class='media-0_textSm__Q52Mz media-0_strong__aXigV']/text()").get()
    # print("review_count:",review_count)

    return {
        "unique_id": unique_id,
        "Brand_name": Brand_name,
        "Product_name": Product_name,
        "Price": Price,
        "select_color": select_color,
        "Discription": Discription,
        "review_count": review_count
    }

# Fetch all the product urls from mongo DB where unique id is not present
products_to_update = db_collection.find({"unique_id": {"$exists": False}})
for product in products_to_update:
    product_url = product["product_url"]
    print(f"Fetching details for product URL: {product_url}")
    product_details = fetch_product_details(product_url)
    
    # Update the product document with fetched details
    if product_details:
        db_collection.update_one(
            {"_id": product["_id"]},
            {"$set": product_details}
        )
        print(f"Updated product {product_url} with details \n")