#__________________________________________________________category________________________________________________
import requests
category_api = "https://content.services.dmtech.com/rootpage-dm-shop-sl-si?view=navigation&mrclx=false"
BASE_URL = "https://www.dm.si"

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://www.dm.si',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.dm.si/',
    'sec-ch-ua': '"Chromium";v="145", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}
data = requests.get(category_api, headers=headers).json()
nav_items  = data["navigation"]["children"]
for item in items:
        if item.get("hidden"):       # skip hidden items
            continue

        name     = item.get("title", "")
        link     = item.get("link", "")
        url      = BASE_URL + link if link else ""
        children = item.get("children", [])
        path     = f"{parent} > {name}" if parent else name
for cat in categories:
    print(f"  {cat['path']}")
    print(f"    → {cat['url']}\n")



#__________________________________________________________crawler_________________________________________________

BASE_URL    = "https://www.dm.si"
PRODUCT_URL = "https://product-search.services.dmtech.com/si/search/static"
PAGE_SIZE   = 80

headers = {
    'sec-ch-ua-platform': '"Linux"',
    'x-dm-product-search-token': '47858176076976',
    'Referer': 'https://www.dm.si/',
    'sec-ch-ua': '"Chromium";v="145", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'x-dm-product-search-tags': 'presentation:grid;search-type:editorial;channel:web',
}

params = {
    'isNew': 'true',
    'popularFacet': 'Novo',
    'pageSize': PAGE_SIZE,
    'searchType': 'editorial-search',
    'sort': 'new',
    'type': 'search-static',
    'currentPage': 0,
}

all_products = []
page = 0

while True:
    params['currentPage'] = page
    response = requests.get(PRODUCT_URL, headers=headers, params=params)
    data = response.json()

    products = data.get("products", [])
    total    = data.get("count", 0)

    print(f"Page {page + 1} — fetched {len(products)} products (total: {total})")

    for p in products:
        name = p.get("title") or ""
        link = p.get("tileData").get("self")
        
        url  = BASE_URL + link if link and not link.startswith("http") else link
        all_products.append({"name": name, "url": url})

    # stop if we've collected everything
    if len(all_products) >= total or len(products) == 0:
        break

    page += 1


    #__________________________________________________________parser_________________________________________________

    pasere_api = "https://products.dm.de/product/products/detail/SI/gtin/4051395562167"
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.dm.si',
    'referer': 'https://www.dm.si/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-dm-version': '2026.303.65788-1',
}

response = requests.get(pasere_api, headers=headers)
print("Status:", response.status_code)

data = response.json()

product     = d.get("product") or d  # some APIs wrap in "product"
price_info  = get(product, "price") or {}
promo       = get(product, "promotion") or {}
hierarchy   = get(product, "categoryHierarchy") or get(product, "breadcrumb") or []
images      = get(product, "images") or get(product, "imageURLs") or []
nutrients   = get(product, "nutrients") or get(product, "nutritionFacts") or []
variants    = get(product, "variants") or []

