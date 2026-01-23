import requests
import time
import json
#__________________________________________________________category________________________________________________


url = "https://www.acehardware.com/graphql"
cookies = {
    '_mzvr': 'El86kucya0W-vuEZpB1MLA',
    '_mzvs': 'nn',
    'gbi_visitorId': 'cmknl4i2600012v74im6w95ta',
    'sb-sf-at-prod-s': 'at=JClUQ6%2FCXGGCrKE91q%2FghDqYc19xzArk7283wXtGqvdiRsb6HjTl0CYU4%2F9AToQSQQ5%2FFLZHuHiftAdAzrhvWgZ8htBVqUl%2BepX2JLhXtapJjNUF8pPO1fL0fOFZ%2FZnwtYxeiAOFvY4sV00qhatZPd%2FuEDAdG6UO5V2OPucnsus78wYLHuJJ5QDQKD1bcldwCef0MBelbuCptJdzrFAoU7AxrDYVRhF0GshPRWaYJclLxwg2WUS9iTFVSYIooqzVTB%2BwF%2Bv0PU1DNQKk4ipTNp8srbNB2UAL4XpJK%2BXPtyJh6pYHhcmOEG0h3f3Ihq6Z7w6OMvbPw1W6SKLOuwgRDQ%3D%3D&dt=2026-01-21T05%3A31%3A01.0299343Z',
    'sb-sf-at-prod': 'at=JClUQ6%2FCXGGCrKE91q%2FghDqYc19xzArk7283wXtGqvdiRsb6HjTl0CYU4%2F9AToQSQQ5%2FFLZHuHiftAdAzrhvWgZ8htBVqUl%2BepX2JLhXtapJjNUF8pPO1fL0fOFZ%2FZnwtYxeiAOFvY4sV00qhatZPd%2FuEDAdG6UO5V2OPucnsus78wYLHuJJ5QDQKD1bcldwCef0MBelbuCptJdzrFAoU7AxrDYVRhF0GshPRWaYJclLxwg2WUS9iTFVSYIooqzVTB%2BwF%2Bv0PU1DNQKk4ipTNp8srbNB2UAL4XpJK%2BXPtyJh6pYHhcmOEG0h3f3Ihq6Z7w6OMvbPw1W6SKLOuwgRDQ%3D%3D',
    '_cs_c': '0',
    '_ga': 'GA1.1.1583728991.1768973463',
    '_gcl_au': '1.1.520664314.1768973463',
    'mt.v': '5.1801804501.1768973459538',
    'closestStoreCode': '16606',
    'IR_gbd': 'acehardware.com',
    'irclid': '%7B%22clickid%22%3A%22%7E95W17c4XUQPHIyCHGHxEvlmomipqleahmsjfg8960XRNHAxwupmd%22%2C%22utm_medium%22%3Anull%2C%22utm_source%22%3Anull%2C%22utm_campaign%22%3Anull%2C%22utm_keyword%22%3Anull%7D',
    'FPID': 'FPID2.2.UFWWN4l1m2mMtQw%2FjjAI1bOq20icnDGyMrB0bQsc%2B00%3D.1768973463',
    '_fbp': 'fb.1.1768973465852.351324207786278282',
    '_pin_unauth': 'dWlkPU9ERXpNR014TjJJdFptTTRZeTAwTW1OaExXRmtOMlV0TWpVMk5HSmlZVGd6TVRFMQ',
    'FPLC': 'oRCWJVjmObBEFSuZu5NIJv2w0uyvP8U03uKtrndguHVcMWEG%2FMUmdj815QGr9xg95dlCQy0JMWrfqJSrSIp4vBW8KLByZWI4taKbspXAaERN8HFK865COGg3Kds0%2BQ%3D%3D',
    'myStoreText': '||---||',
    'cartCount': '0',
    'uws_storage': '%22cookie%22',
    'uws_rate_comparators': '%7B%22global%22%3A49462703%7D%7Csession_timeout',
    'uws_story_an3b8qk3_step': '%7B%22step%22%3A1%7D%7Csession_timeout',
    'OptanonAlertBoxClosed': '2026-01-21T05:31:32.565Z',
    'mt.ac': '3',
    'salsify_session_id': '476625c3-d54f-4110-bcf4-1728d65468e9',
    'BVBRANDID': 'c7cb7a93-2998-4072-b5ba-357290517c9f',
    'userBehaviors': '[1014]',
    '_cs_s_ctx': '%7B%22firstViewTime%22%3A1768985659166%2C%22firstViewUrl%22%3A%22https%3A%2F%2Fwww.acehardware.com%2F%22%2C%22sessionReferrer%22%3A%22https%3A%2F%2Fwww.acehardware.com%2F%22%7D',
    'IR_9988': '1768989186610%7C0%7C1768989186610%7C%7C',
    'IR_PI': '61edf635-f68a-11f0-9dc0-297730fed169%7C1768989186610',
    '_uetsid': '60b1a2b0f68a11f092f047cd5411a7f2',
    '_uetvid': '60b1bff0f68a11f085b15107376db9fc',
    '_derived_epik': 'dj0yJnU9elZBQmFjS1lKX3hZanVRWmhtbEFVNnF2Z0N6Z3FyVTImbj1yRGRUY1lIWDZsS0pBcnRsaWc3dEp3Jm09MSZ0PUFBQUFBR2x3b2dvJnJtPTEmcnQ9QUFBQUFHbHdvZ28mc3A9Mg',
    '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%223vZmHc9k55ceFDHxTNRm%22%2C%22expiryDate%22%3A%222027-01-21T09%3A53%3A16.529Z%22%7D',
    '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%223f5c6d766d27452c81f554d5d25661be%22%2C%22expiryDate%22%3A%222027-01-21T09%3A53%3A16.539Z%22%7D',
    'uws_session': '%7B%22start%22%3A1768973467827%2C%22count%22%3A44%2C%22referrer%22%3A%22%22%7D%7Csession_timeout',
    'uws_visitor': '%7B%22vid%22%3A%22176897346783754169%22%2C%22start%22%3A1768973467827%2C%22count%22%3A44%7D%7C1776765196722',
    '__cf_bm': 'akIDtow3ZN4GZwvBZiyg2tTs_.TIVMgMD0mKGPW0LVE-1768991317-1.0.1.1-8vS3Ak1zYCDvBHzeDQBG8dnjkMC5.UXDI2ehqKvpEUFtZiw3DZTIIKZnBx38BtMiKCwxCodfdreUe2egWVpTXcPvu4HTSI8jph6Wg15fM.Q',
    '_ga_KQ8PQ6JEPH': 'GS2.1.s1768991322$o6$g0$t1768991322$j60$l0$h0',
    '_ga_CRGJ6H77X9': 'GS2.1.s1768991322$o6$g0$t1768991322$j60$l0$h335845295',
    'gbi_sessionId': 'cmknvrcmg00002v749xotj7ha',
    '_mzvt': 'YvlNL0WoeU-i2GKDGaUcFg',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Jan+21+2026+15%3A58%3A44+GMT%2B0530+(India+Standard+Time)&version=202503.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1&geolocation=%3B&AwaitingReconsent=false',
    'cf_clearance': '1h9AO6SxjqM7_mghfqfOKSWNTK_eLkrLcggIdrOIxKM-1768991325-1.2.1.1-gk5sgXHj4DfDB1VajDRsJDvOZlHVi07Y0cq2jJLHyxT4oTmc300HA9ndpvfSxGsuKpmPfKES_ueixVFqquXcw1XzWE9pWuF0Epfs51T4PhYsuvk8qF4gZB7gFpsa1_xnNYaLmRDH6sNcOTcekCuZggt.Bs6jiF5dGk3K04FUitdoWZDd62LXzCZ10jl1bAMNwDvs3SdeSpXJ8p.FW4RnO2mAvvOH3MGmaugQyVIByNk',
    '_cs_id': '7122c9ad-8efa-a6e0-e0ba-da2691b5ddeb.1768973461.2.1768991325.1768985659.1754653897.1803137461721.1.x',
    '_cs_s': '11.5.U.9.1768993126425',
    'myStore': '{%22name%22:%22Ace%20Hardware%20-%20Top%20of%20the%20World%22%2C%22address%22:{%22address1%22:%221611%20B%20Okpik%20Street%22%2C%22address2%22:%22%22%2C%22address3%22:%22%22%2C%22address4%22:%22%20%22%2C%22cityOrTown%22:%22Barrow%22%2C%22stateOrProvince%22:%22AK%22%2C%22postalOrZipCode%22:%2299723%22%2C%22countryCode%22:%22US%22%2C%22addressType%22:%22Commercial%22%2C%22isValidated%22:false}%2C%22delivery%22:%22unknown%20delivery%20date%22%2C%22code%22:%2216606%22%2C%22normalizedStoreHours%22:{%22open%22:true%2C%22openUntil%22:%226:00%20PM%22%2C%22closeTime%22:%222026-01-21T12:30:00.878Z%22%2C%22tomorrowDate%22:%2222%22%2C%22todayDate%22:21%2C%22nextOpenDay%22:{%22isoString%22:%222026-01-22T02:30:46.878Z%22%2C%22date%22:22%2C%22openTime%22:%228:00%20AM%22%2C%22day%22:%22Thursday%22%2C%22earlyMorning%22:false%2C%22notTomorrow%22:false}}%2C%22geo%22:{%22lat%22:71.288332%2C%22lng%22:-156.783654}%2C%22curbsideFl%22:%22N%22%2C%22limitationFl%22:%22N%22%2C%22nearestLocations%22:%22%22%2C%22storeNameOverride%22:%22Barrow%20-%20B%20Okpik%20Street%22%2C%22fulfillmentTypes%22:[{%22code%22:%22SP%22%2C%22name%22:%22In%20Store%20Pickup%22}]}',
    '_mzPc': 'eyJjb3JyZWxhdGlvbklkIjoiMTdjZjUzZWVjM2JlNGQwNGEzN2UwNjAxMTBiZmJhMzIiLCJpcEFkZHJlc3MiOiIyNDAzOmEwODA6ODIyOjdmMzpmYWY2OmRmOWI6YzhlNzpjZTQwIiwiaXNEZWJ1Z01vZGUiOmZhbHNlLCJpc0NyYXdsZXIiOmZhbHNlLCJpc01vYmlsZSI6ZmFsc2UsImlzVGFibGV0IjpmYWxzZSwiaXNEZXNrdG9wIjp0cnVlLCJ1c2VyIjp7ImlzQXV0aGVudGljYXRlZCI6ZmFsc2UsInVzZXJJZCI6IjNmNWM2ZDc2NmQyNzQ1MmM4MWY1NTRkNWQyNTY2MWJlIiwiZmlyc3ROYW1lIjoiIiwibGFzdE5hbWUiOiIiLCJlbWFpbCI6IiIsImlzQW5vbnltb3VzIjp0cnVlLCJiZWhhdmlvcnMiOlsxMDE0XSwiaXNTYWxlc1JlcCI6ZmFsc2V9LCJ1c2VyUHJvZmlsZSI6eyJ1c2VySWQiOiIzZjVjNmQ3NjZkMjc0NTJjODFmNTU0ZDVkMjU2NjFiZSIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWxBZGRyZXNzIjoiIiwidXNlck5hbWUiOiIifSwicHVyY2hhc2VMb2NhdGlvbiI6eyJjb2RlIjoiMTY2MDYifSwiaXNFZGl0TW9kZSI6ZmFsc2UsImlzQWRtaW5Nb2RlIjpmYWxzZSwibm93IjoiMjAyNi0wMS0yMVQxMDoyODo0Ny44MDM0MTc3WiIsImNyYXdsZXJJbmZvIjp7ImlzQ3Jhd2xlciI6ZmFsc2V9LCJjdXJyZW5jeVJhdGVJbmZvIjp7fX0%3D',
    '_dd_s': 'rum=0&expire=1768992224977',
}


payload = {"operationName":"CategoryTree","variables":{},"query":"query CategoryTree {\ncategoriesTree(includeAttributes: true){\ntotalCount\nitems{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\n}\n}\n}\n}\n}\n}\n}\n}"}

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

