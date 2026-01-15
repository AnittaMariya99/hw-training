import hrequests
from parsel import Selector
from urllib.parse import urljoin
import time
import json
import re
# from curl_cffi import requests
# --- CONFIGURATION ---
BASE_URL = "https://www.academy.com"

# Simplified headers for resilience
main_page_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"dff29-dB/dPs7TFcYEu9jWHZnt2L2ejXw:dtagent10325251103172537A5Uv"',
    'priority': 'u=0, i',
    # 'referer': 'https://www.academy.com/c/mens?&page_173',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

plp_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'priority': 'u=0, i',
    'referer': 'https://www.academy.com/c/mens/mens-apparel/mens-hoodies-and-sweatshirts',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}
pdp_headers ={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"1fbcd8-dnvWtAwgyUv4YvdDY2MXu5SKn/o:dtagent10325251103172537A5Uv"',
    'priority': 'u=0, i',
    'referer': 'https://www.academy.com/c/mens/mens-apparel/mens-hoodies-and-sweatshirts',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}


def fetch_page(url,header = main_page_headers):
    print(f"Fetching: {url}...")
    try:
        # Avoid aggressive scraping checks
        time.sleep(2)
        # resp = session.get(url, timeout=15)
        resp = hrequests.get(url, headers=header, timeout=15)
        if resp.status_code == 200:
            # print(resp.text)
            if "access to this page has been denied" in resp.text.lower():
                print(f"Access Denied. {resp.text}")
                return None
            return resp
        elif resp.status_code == 403:
            print(f"403 Forbidden. {resp}")
            return None
        else:
            print(f"ERROR: Status {resp.status_code}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


################  CATEGORY CRAWLER #################

print(f"--- CATEGORY CRAWLER ---")
response = fetch_page(BASE_URL, header=main_page_headers)
category_count = 0
if response:
    selector = Selector(text=response.text)
    category_items = selector.xpath("//ul/li/a[contains(@class, 'categoryItemLink')]")
    for item in category_items:
        name = "".join(item.xpath(".//text()").getall()).strip()
        url = item.xpath("./@href").get("")
        if name and url:
            if not url.startswith("http"): url = BASE_URL + url
            print(f"Found Category: {name} : {url}")
            category_count += 1

    print(f"Total categories found: {category_count}")

#################  PRODUCT CRAWLER #################
category_url = "https://www.academy.com/c/mens/mens-apparel/mens-jackets--outerwear"
page_count = 1
product_count = 0
next_page_url = category_url

while next_page_url:
    print(f"Scraping page {page_count}: {next_page_url}")

    response = fetch_page(next_page_url, header=plp_headers)
    if not response:
        break
        
    print("Status:", response.status_code)

    sel = Selector(text=response.text)

    product_links = sel.xpath(
            '//div[@data-auid="product-details-container"]/a/@href'
        ).getall()

    if not product_links:
        print("No products found — stopping pagination.")
        break

    product_links = [urljoin(BASE_URL, link) for link in product_links]
    # print product links
    for link in product_links:
        print(link)
    
    product_count += len(product_links)

    print(f"Products found: {len(product_links)}")
    
    # Pagination logic
    next_page = sel.xpath("//a[@class='asoPageElement asoPageBtn prevNext' and .//div[normalize-space()='next page']]/@href").get()
    if next_page:
        next_page_url = urljoin(BASE_URL, next_page)
        page_count += 1
    else:
        next_page_url = None

print(f"\nTotal products collected: {product_count}")

            

#################  PARSER #################
product_link = "https://www.academy.com/p/nike-mens-club-pullover-fleece-hoodie-153319266?sku=pinksicle-pinksicle-white-medium"

p_response = fetch_page(product_link, header=pdp_headers)
# save response to html file
with open("p_response.html", "w", encoding="utf-8") as f:
    f.write(p_response.text)
if p_response.status_code == 200:
    p_selector = Selector(text=p_response.text)
    
    
    name = "".join(p_selector.xpath('//h1[@data-auid="PDP_ProductName"]//text()').getall()).strip()
    if not name: name = p_selector.xpath('//title/text()').get('').split('|')[0].strip()
    
    price = "".join(p_selector.xpath('//span[contains(@class, "nowPrice")]//text()').getall()).strip()
    was_price = "".join(p_selector.xpath('//span[contains(@class, "wasPrice")]//text()').getall()).strip()
    
    description = " ".join([d.strip() for d in p_selector.xpath("//div[@class='contents']//div[contains(@class, 'textBodyLg')]//text()").getall() if d.strip()])
    # size = "".join(p_selector.xpath('//span[@class="swatchName--KWu4Q"]/text()').getall()).strip()
    # LD+JSON Fallback
    ld_json = p_selector.xpath('//script[@type="application/ld+json" and contains(text(), "Product")]/text()').get()
    if ld_json:
        try:
            data = json.loads(ld_json)
            if isinstance(data, list): data = data[0]
            if not name: name = data.get('name')
            if not description: description = data.get('description')
            if not price and 'offers' in data:
                o = data['offers']
                price = str(o[0].get('price')) if isinstance(o, list) else str(o.get('price'))
        except: pass
    
    # Images and Specs from internal state
    app_state_script = p_selector.xpath('//script[contains(text(), "descriptiveAttributes")]/text()').get()
    specs = []
    if app_state_script:
        match = re.search(r'"descriptiveAttributes":({.*?})', app_state_script)
        if match:
            try:
                attr_data = json.loads(match.group(1))
                for k, v in attr_data.items():
                    v_str = ", ".join(v) if isinstance(v, list) else str(v)
                    clean_k = k.replace('attribute_', '').replace('_', ' ').capitalize()
                    if v_str and v_str not in ['0', 'NA']: specs.append(f"{clean_k}: {v_str}")
            except: pass
    
    image_urls = p_selector.xpath('//div[contains(@class, "sliderImage")]//img/@src').getall()
    if not image_urls: image_urls = p_selector.xpath('//img/@src').getall()

    # Parse ASOData as JSON for higher accuracy
    color, size = None, None
    script_texts = p_selector.xpath('//script[contains(text(), "window.ASOData")]/text()').getall()
    decoder = json.JSONDecoder()
    for script_text in script_texts:
        # Match window.ASOData['...'] = { ... };
        matches = re.finditer(r"window\.ASOData\['(comp-.*?)'\]\s*=\s*", script_text, re.DOTALL)
        for match in matches:
            try:
                start_idx = match.end()
                comp_data, _ = decoder.raw_decode(script_text[start_idx:])
                
                # 1. Primary: Check for selectedIdentifier (exact match for current page)
                p_item = comp_data.get('api', {}).get('productItem', {})
                sel_id = p_item.get('selectedIdentifier', {})
                if sel_id:
                    raw_color = sel_id.get('Color')
                    raw_size = sel_id.get('Size')
                    
                    # Clean prefixes
                    color = raw_color[5:] if raw_color and raw_color.startswith('Color') else raw_color
                    size = raw_size[4:] if raw_size and raw_size.startswith('Size') else raw_size
                    
                    if color and size: break

                # 2. Secondary: Match skuId
                target_sku_id = p_item.get('skuId')
                product_info = comp_data.get('api', {}).get('product-info', {}).get('productinfo', {})
                skus = product_info.get('sKUs', [])
                
                if target_sku_id and skus:
                    for sku in skus:
                        if str(sku.get('skuId')) == str(target_sku_id):
                            attr = sku.get('descriptiveAttributes', {})
                            color = attr.get('Color')
                            size = attr.get('Size')
                            break
                    if color and size: break

                # 3. Fallback: First SKU
                if not skus:
                    skus = comp_data.get('productinfo', {}).get('sKUs', [])
                if not skus:
                    skus = comp_data.get('sKUs', [])

                if skus and not color:
                    first_sku = skus[0]
                    attr = first_sku.get('descriptiveAttributes', {})
                    color = attr.get('Color')
                    size = attr.get('Size')
                    if color and size: break
            except: continue
        if color and size: break

    print(f"URL: {product_link}")
    print(f"NAME: {name if name else 'N/A'}")
    print(f"PRICE: {price if price else 'N/A'}")
    print(f"WAS PRICE: {was_price if was_price else 'N/A'}")
    print(f"DESCRIPTION: {description if description else 'N/A'}")
    print(f"COLOR: {color if color else 'N/A'}")
    print(f"SIZE: {size if size else 'N/A'}")
    print(f"IMAGES: ")
    for image in image_urls:
        print(image)
    print(f"SPECS: ")
    review_count = 0
    rating = 0
    for spec in specs:
        print(spec)
        specs_splited = spec.split(':')
        if specs_splited[0].strip() == 'Reviewcount': review_count = specs_splited[1].strip()
        if specs_splited[0].strip() == 'Averagerating': rating = specs_splited[1].strip()

    print(f"NO. OF REVIEWS: {review_count}")
    print(f"RATING: {rating}")
