import requests
import time
import json
from playwright.sync_api import sync_playwright

cookies = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate to the website
    page.goto('https://www.acehardware.com')
    
    
    # Get all cookies
    for cookie in context.cookies():
        cookies[cookie['name']] = cookie['value']

    browser.close()


url = "https://www.acehardware.com/graphql"


payload = {"operationName":"CategoryTree","variables":{},"query":"query CategoryTree {\ncategoriesTree(includeAttributes: true){\ntotalCount\nitems{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\n}\n}\n}\n}\n}\n}\n}"}

response = requests.post(url,json=payload,cookies=cookies)


data = response.json()

#save to file
with open("categories_response.json", "w") as f:
    json.dump(data, f, indent=4)

categories_tree = data.get("data", {}).get("categoriesTree", {})
items = categories_tree.get("items", [])

stack = [(item, "https://www.acehardware.com") for item in items]

# add leaf categorie details to a text file
with open("categories.txt", "w") as f:
    while stack:
        curr, base_url = stack.pop()
        isDisplayed = curr.get("isDisplayed", False)
        content = curr.get("content", {})
        slug = content.get("slug", "")
        name = content.get("name", "")
        categoryId = curr.get("categoryId", "")

        if not isDisplayed:
            continue

        url = f"{base_url}/{slug}" if slug else base_url
        children = curr.get("childrenCategories", [])

        if not children:
            print(f"LEAF → {name} | {categoryId} | {url}")
            f.write(f"LEAF → {name} | {categoryId} | {url}\n")
        else:
            for child in reversed(children):
                stack.append((child, url))



#__________________________________________________________crawler_________________________________________________

import hrequests



urls ="https://www.acehardware.com/departments/outdoor-living/grills-and-smokers/gas-grills/propane-gas-grills"
response = hrequests.get(urls)
print(response.status_code)
print(response.text)
print(response.status_code)

# Configuration
CATEGORY_ID = "2217"  # Change this to any category ID you want to fetch
STORE_ID = "16606"  # Store location ID
PAGE_SIZE = 30

# API endpoint
BASE_URL = "https://www.acehardware.com/api/commerce/catalog/storefront/productsearch/search"

# Build the filter string
filter_str = f"categoryId req {CATEGORY_ID} and tenant~hide-from-search-flag ne Y and ((locationsInStock in [{STORE_ID}] and fulfillmentTypesSupported eq InStorePickup) or (locationsInStock in [WA03,NY01,TX03,OH02,WA01,CA01,CA02,IL01,VA01,FL02,FL01,AL01,AR01,WI01,GA01,GA02,PA01,CO01,AZ01,MO01,DS01,V68553,V54734,V52788,V41966,V36959,V35174,V17500,V53017,V56761,V63079,V52968,V01667,V62303,V63868,V34606,V01667,V63733,V62579,V63747,V63547] and fulfillmentTypesSupported eq DirectShip) or tenant~paint-code eq c or tenant~geo-facet-override eq Y)"

# # Initialize pagination
start_index = 0

page_count = 1
current_page = 0

while current_page < page_count:
    # Build query parameters
    params = {
        "query": "",
        "filter": filter_str,
        "facetTemplate": f"categoryId:{CATEGORY_ID}",
        "facet": "categoryCode",
        "facetValueFilter": "",
        "sortBy": "",
        "pageSize": PAGE_SIZE,
        "startIndex": start_index
    }

    response = hrequests.get(BASE_URL, params=params)
    data = response.json()

    if current_page == 0:
        page_count = data.get("pageCount", 1)
    
    current_page += 1
    start_index += PAGE_SIZE
#__________________________________________________________parser_________________________________________________
import requests
from parsel import Selector
import json
import re

headers = {
    'Referer': 'https://www.acehardware.com/departments/outdoor-living/grills-and-smokers/gas-grills/propane-gas-grills?pageSize=60',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}
product_link = "https://www.acehaware.com/departments/outdoor-living/grills-and-smokers/gas-grills/8061614"

response = requests.get(product_link, headers=headers)
# print(response.text)
# print(response.status_code)

selector = Selector(text=response.text)


Item_name=selector.xpath('//h1[@class="mz-pagetitle title"]/text()').get()
print(Item_name)

detailed_scripts=selector.xpath("//script[@type='text/json' and @id='data-mz-preload-product']/text()").getall()
brand_name = None
country_of_origin= None
upc= None

for script_str in detailed_scripts:
    script_json = json.loads(script_str)
upc = script_json.get('upc')
print(upc)
    
# Extract Brand Name from properties
if 'properties' in script_json:
    for prop in script_json['properties']:
    # print(f"Property: {prop} \n")
        if 'attributeDetail' in prop and prop['attributeDetail'].get('name') == 'Brand Name':
            if 'values' in prop and len(prop['values']) > 0:
                brand_name = prop['values'][0].get('value')

        if 'attributeDetail' in prop and prop['attributeDetail'].get('name') == 'Country Of Origin':
            if 'values' in prop and len(prop['values']) > 0:
                country_of_origin= prop['values'][0].get('value')   

print(brand_name)
print(country_of_origin)
        


price=selector.xpath("//div[@class='price ']//text()").get()
print(price)

detailed_scripts1=selector.xpath("//script[@type='application/ld+json' and @id='productSchema']/text()").get()
script_json1 = json.loads(detailed_scripts1)
mpn=None
discription=None
availability=None

availability = script_json1.get('offers', {}).get('availability')
availability = availability.split('/')[-1]
print(availability)

description = script_json1.get('description')
print(description)
manufacture_part_number=script_json1.get('mpn')
print( manufacture_part_number)


text = selector.xpath("//div[@class='productCode']/text()").get()
vendor_or_seller_Part_number = re.search(r"\d+", text).group()
print(vendor_or_seller_Part_number)

product_category = " > ".join(selector.xpath("//div[@id='breadcrumbs']//a/text()").getall()).strip()
print(product_category)

