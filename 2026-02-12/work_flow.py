#__________________________________________________________category________________________________________________
import requests
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
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
url="https://www.matalanme.com/ae_en/category/womens"
response=requests.get(url,headers=headers)
print(response.status_code)
print(response.text)


#__________________________________________________________crawler_________________________________________________

import requests
import base64
import json
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.matalanme.com',
    'priority': 'u=1, i',
    'referer': 'https://www.matalanme.com/',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'source': 'matalan_city_centre_deira',
    'store': 'matalan_ae_en',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'website': 'matalan',
}
BASE_URL = "https://api.bfab.com/graphql"
PRODUCT_VERSION = "1717"

# Category ID (example: 193)
category_id = "193"

# Encode to base64 (Magento category_uid format)
category_uid = base64.b64encode(category_id.encode()).decode()

PAGE_SIZE = 40

# GraphQL Query (must be single string for GET)
query = """
query GetProductList($filter: ProductAttributeFilterInput,
                     $pageSize: Int,
                     $currentPage: Int,
                     $sort: ProductAttributeSortInput) {
  products(
    filter: $filter
    pageSize: $pageSize
    currentPage: $currentPage
    sort: $sort
  ) {
    total_count
    page_info {
      current_page
      page_size
      total_pages
    }
    items {
      id
      sku
      name
      categories {
        id
        name
      }
    }
  }
}
"""


current_page = 1
total_pages = 1

while current_page <= total_pages:

    variables = {
        "filter": {
            "category_uid": {
                "in": [category_uid]
            }
        },
        "pageSize": PAGE_SIZE,
        "currentPage": current_page,
        "sort": {}
    }

    params = {
        "product_version": PRODUCT_VERSION,
        "query": query,
        "operationName": "GetProductList",
        "variables": json.dumps(variables)
    }

    response = requests.get(BASE_URL, params=params, headers=headers)
    data = response.json()

    products = data["data"]["products"]
    total_pages = products["page_info"]["total_pages"]

    print(f"\nPage {current_page} of {total_pages}")

    for item in products["items"]:
        print(item["id"], item["name"])

    current_page += 1

#__________________________________________________________parser_________________________________________________
import requests
import json
import re
from datetime import datetime


headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.matalanme.com',
    'priority': 'u=1, i',
    'referer': 'https://www.matalanme.com/',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'source': 'matalan_city_centre_deira',
    'store': 'matalan_ae_en',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'website': 'matalan',
}

BASE_URL = "https://api.bfab.com/graphql"
PRODUCT_VERSION = "1717"
# Example url_key
url_key = "et-vous-wiggle-print-mini-dress-brown"


query = """
query GetProductDetailVariants($url_key: String!) {
  products(filter: {url_key: {eq: $url_key}}) {
    items {
      id
      name
      description {
        html
      }
      categories {
        name
        url_path
        breadcrumbs {
          category_name
          category_url_path
        }
      }
      ... on ConfigurableProduct {
        variants {
          product {
            id
            url_key
            name
            sku
            stock_status
            qty_left_in_stock
            swatch_image
            media_gallery {
              url
              label
            }
            product_custom_attributes
            price_range {
              minimum_price {
                regular_price {
                  value
                  currency
                }
                final_price {
                  value
                  currency
                }
                discount {
                  amount_off
                  percent_off
                }
              }
            }
          }
          attributes {
            label
            code
            value_index
            uid
          }
        }
      }
    }
  }
}
"""

payload = {
    "operationName": "GetProductDetailVariants",
    "variables": {
        "url_key": url_key
    },
    "query": query
}
response = requests.post(BASE_URL,params={"product_version": PRODUCT_VERSION},json=payload,headers=headers)
data = response.json()
print(response.status_code)
print(data)
if "data" in data and data["data"]["products"]["items"]:
    item_main = data["data"]["products"]["items"][0]
    print(item_main)
    
