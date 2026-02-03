import hrequests
from parsel import Selector
session = hrequests.Session()


url="https://www.ah.nl/producten"


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.ah.nl/',
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
#__________________________________________________________category________________________________________________

response=session.get(url,headers=headers)
sel=Selector(response.text)
category_blocks=sel.xpath('//a[@class="taxonomy-card_titleLink__pdmR+"]')

for category_block in category_blocks:
    name = category_block.xpath('./text()').get()
    link = category_block.xpath('./@href').get()
    print(f"{name} - {link}")

#__________________________________________________________crawler_________________________________________________


from curl_cffi import requests
from parsel import Selector
session = requests.Session()

url="https://www.ah.nl/producten/6401/groente-aardappelen"
page = 1
PAGE_SIZE = 36
category_slug = 'groente-aardappelen'
category_id = 6401

while True:
    print(f"Fetching page {page}...")
    PLP_API_URL = f"https://www.ah.nl/zoeken/api/products/search?page={page}&size={PAGE_SIZE}&taxonomySlug={category_slug}&taxonomy={category_id}"
    response = session.get(PLP_API_URL, headers=headers, impersonate="chrome")
    response_json = response.json()
    total_pages = response_json['page']['totalPages']
    
    for product in response_json['cards']:
        product = product.get("products", [])[0]
        id = product.get('id')
        link = product.get('link')
        title = product.get('title')

        print(f"{id} : {title} - {link}")

    if page > total_pages:
        break

    page += 1

#__________________________________________________________product_________________________________________________

import httpx
response=httpx.get(url,headers=headers)
sel=Selector(response.text)


import json
import re

product = {}

product_details = sel.xpath("//script[@type='application/ld+json']/text()").getall()

    json_data = json.loads()
    product["unique_id"] = json_data.get("sku", "")
    product["image_url"] = json_data.get("image", "")
    product["brand"] = json_data.get("brand", {}).get("name", "")

    offers = json_data.get("offers", {})
    selling_price = offers.get("price")
    product["selling_price"] = float(selling_price) if selling_price else ""
    product["currency"] = offers.get("priceCurrency", "")

    instock_raw = offers.get("availability")
    product["instock"] = instock_raw.split("/")[-1].lower() if instock_raw else ""

    product["competitor_name"] = offers.get("seller", {}).get("name", "")

    raw_grammage = json_data.get("weight", "")
    if raw_grammage == "per stuk":
        product["grammage_quantity"] = 1
        product["grammage_unit"] = "stuk"
    elif raw_grammage:
        parts = raw_grammage.split()
        product["grammage_quantity"] = int(parts[0]) if parts[0].isdigit() else ""
        product["grammage_unit"] = parts[1] if len(parts) > 1 else ""
    else:
        product["grammage_quantity"] = ""
        product["grammage_unit"] = ""

product["servings_per_pack"] = sel.xpath(
    "//dt[normalize-space()='Aantal porties:']/following-sibling::dd/text()"
).get(default="")

promotion_description = sel.xpath(
    "//div[@data-key='pdp-shield-discount']//span/text()"
).get(default="")

product["promotion_description"] = promotion_description
match = re.search(r"\d+\s*%", promotion_description)
product["percentage_discount"] = match.group(0) if match else ""

product["ingredients"] = sel.xpath(
    "//div[@data-testid='pdp-ingredients-list']//text()"
).get(default="").strip()

alcohol_percentage = sel.xpath(
    "//dt[normalize-space()='Alcoholpercentage:']/following-sibling::dd/text()"
).get(default="")
product["alcohol_percentage"] = alcohol_percentage.replace("%", "").strip()

product["distributor_address"] = " ".join(
    t.strip()
    for t in sel.xpath("//address//p//text()").getall()
    if t.strip()
)

features = sel.xpath(
    "//div[@data-testid='pdp-logos']//ul//li//span//text()"
).getall()
product["features"] = [f.strip() for f in features if f.strip()]

nutrition = {}
for row in sel.xpath("//tbody//tr"):
    key = " ".join(t.strip() for t in row.xpath("./td[1]//text()").getall() if t.strip())
    value = " ".join(t.strip() for t in row.xpath("./td[2]//text()").getall() if t.strip())
    if key and value:
        nutrition[key] = value
product["nutrition"] = nutrition

allergens = {}
for item in sel.xpath("//div[@data-testid='pdp-ingredients-allergens']//dl//span"):
    key = " ".join(t.strip() for t in item.xpath(".//dt//text()").getall() if t.strip()).replace(":", "")
    value = " ".join(t.strip() for t in item.xpath(".//dd//text()").getall() if t.strip())
    if key and value:
        allergens[key] = value
product["allergens"] = allergens

product["country_of_origin"] = sel.xpath(
    "//div[@data-testid='pdp-origin-info']//p//text()[normalize-space()]"
).get(default="")

product["instruction_for_use"] = sel.xpath(
    "//div[@data-testid='pdp-usage-info']//dd//text()[normalize-space()]"
).get(default="")

product["storage_instructions"] = sel.xpath(
    "//div[@data-testid='pdp-storage-info']//p//text()[normalize-space()]"
).get(default="")
