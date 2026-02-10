

#__________________________________________________________category________________________________________________

import requests
session=requests.Session()
from parsel import Selector
import json
base_url = "https://www.aldi.nl"

url="https://www.aldi.nl/producten.html"
response = session.get(url)
sel=Selector(response.text)
script_data=sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()
data = json.loads(script_data)
side_drawer = data.get("props",{}).get("pageProps",{}).get("page",{}).get("header",{}).get("0",{}).get("sideDrawerNavigation",[])

for item in side_drawer:
    for key, value in item.items():
        if isinstance(value, dict) and "children" in value:
            categories = value.get("children", [])
            for cat in categories:
                cat_label = cat.get("label")
                cat_path = cat.get("path")
                cat_full_url = base_url + cat_path if cat_path else ""
                
                sub_categories = cat.get("children", [])
                if sub_categories:
                    for sub_cat in sub_categories:
                        sub_label = sub_cat.get("label")
                        sub_path = sub_cat.get("path")
                        sub_full_url = base_url + sub_path if sub_path else ""
                        print(f'category "{cat_label}", url: "{cat_full_url}", sub category "{sub_label}", url: "{sub_full_url}"')

#__________________________________________________________crawler_________________________________________________

                        url = "https://www.aldi.nl/producten/aardappels-groente-fruit/aardappelen.html"
                        response = session.get(url)

# Parse the JSON data from the script tag
sel = Selector(response.text)
script_json = sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()
data = json.loads(script_json)
    
algolia_results = data.get("props", {}).get("pageProps", {}).get("algoliaState", {}).get("initialResults", {})
    

product_urls = []
for key, value in algolia_results.items():
    hits = value.get("hits", [])
    for hit in hits:
        product_url = hit.get("url")
        if product_url:
            full_product_url = base_url + product_url
            product_urls.append(full_product_url)
            print(full_product_url) 


#__________________________________________________________parser_________________________________________________

url = "https://www.aldi.nl/product/aardappelpartjes-gekruid-1226110.html"
response = session.get(url)
print(f"Status code: {response.status_code}")

sel = Selector(response.text)
script_json = sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()

if script_json:
    data = json.loads(script_json)
    api_data_string = data.get("props", {}).get("pageProps", {}).get("apiData", "[]")
    api_data = json.loads(api_data_string)
    
    product_data = {}
    for item in api_data:
        if isinstance(item, list) and len(item) > 1 and item[0] == "PRODUCT_DETAIL_GET":
            res = item[1].get("res", {})
            products = res.get("products", [])
            if products:
                product = products[0]
                product_name = product.get("name", "")
                product_id = product.get("objectID", "")
                brand_name = product.get("brandName", "")

                sales_unit = product.get("salesUnit", "")
                # split into 2 parts gramage quantity and unit
                sales_unit_array= sales_unit.split(" ")
                gramage = sales_unit_array[0]
                unit = sales_unit_array[1]

                base_price_info = product.get("currentPrice",{}).get("basePrice",[])[0]
                base_price_value = base_price_info.get("basePriceValue","")
                base_price_scale = base_price_info.get("basePriceScale","")
                price_per_unit = base_price_scale + " = " + str(base_price_value)

                long_description_description = product.get("longDescription", "")
                short_description = product.get("shortDescription", "")
                product_description = short_description + " " + long_description_description

                # Price logic
                current_price = product.get("currentPrice", {})
                price = current_price.get("priceValue", "")
                
                # Image logic
                assets = product.get("assets", [])
                image = ""
                for asset in assets:
                    if asset.get("type") == "primary":
                        image = asset.get("url", "")
                        break
                
                product_data = {}
                
                product_data["unique_id"] = product_id
                product_data["pdp_url"] = url
                product_data["product_name"] = product_name
                product_data["brand"] = brand_name
                product_data["product_description"] = product_description
                product_data["price_per_unit"] = price_per_unit
                product_data["selling_price"] = price
                product_data["image"] = image
                product_data["site_shown_uom"] = sales_unit
                product_data["grammage_quantity"] = gramage
                product_data["grammage_unit"] = unit

                
                
                # Cleanup: remove placeholder strings if empty
                for k, v in product_data.items():
                    if v == "[]" or v == "{}" or v == "None":
                        product_data[k] = ""
                break

    if product_data:
        for key, value in product_data.items():
            print(f"{key}: {value}")
    else:
        print("Product data not found in apiData.")
else:
    print("__NEXT_DATA__ script tag not found.")