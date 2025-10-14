import requests
from parsel import Selector


def extract_carbon38_site_data(url):
    headers = {
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'accept-language': 'en-US,en;q=0.9',
        # 'cache-control': 'max-age=0',
        # 'if-none-match': '"cacheable:fff51e5e9f133d585bdfb565e244a2a8"',
        # 'priority': 'u=0, i',
        # 'referer': 'https://carbon38.com/en-in/collections/shoes',
        # 'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
        # 'sec-ch-ua-mobile': '?1',
        # 'sec-ch-ua-platform': '"Android"',
        # 'sec-fetch-dest': 'document',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'same-origin',
        # 'sec-fetch-user': '?1',
        # 'upgrade-insecure-requests': '1',
        # 'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    
    }
    response = requests.get(url, headers=headers)

    response.status_code
    response.text
    print(f"Status: {response.status_code}, Length: {len(response.text)}")

    sel = Selector(response.text)

    # === Extract fields ===
    name = sel.xpath("//h1[@class='ProductMeta__Title Heading u-h3']/text()").get()
    price = sel.xpath("//span[@class='ProductMeta__Price Price']/text()").get()
    colour = sel.xpath("//div[@class='ProductForm__Option ProductForm__Option--labelled']/div/span/span/text()").get()
    # dictionary extraction
    faq_items = sel.xpath('//div[contains(@class,"Faq__Item")]')

    data = {}  # dictionary to store key-value pairs

    for item in faq_items:
        # Get question title (key)
        question = item.xpath('.//button[contains(@class,"Faq__Question")]/text()').get()
        # Get all text lines from the answer
        answer_lines = item.xpath('.//div[contains(@class,"Faq__Answer")]//text()').getall()
        
        # Clean up and join the text parts
        if question:
            key = question.strip()
            value = " ".join([line.strip() for line in answer_lines if line.strip()])
            # print(f"key: {key}, value: {value}")
            data[key] = value

    # === Convert to key-value pair dictionary ===
    result = {
        "Product Name": name.strip() if name else None,
        "Price": price.strip() if price else None,
        "Colour": colour.strip() if colour else None,
        "editor's Note": data.get("Editor's Notes"),
        "size_fit":data.get("Size & Fit"),
        "Fabric & Care":data.get("Fabric & Care") ,
    }

    # === Print neatly ===
    print("\n--- Extracted Data ---")
    # for key, value in result.items():
        # print(f"{key}: {value}")

    return result

import time

# Step 1: Read all URLs
with open("carbon38_product_links.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total URLs to process: {len(urls)}")

# # Step 2: Open output file
with open("carbon38_product_details.txt", "w", encoding="utf-8") as out:
    for i, url in enumerate(urls, start=1):
        print(f"\n🔹 Processing {i}/{len(urls)}: {url}")
        
        data = extract_carbon38_site_data(url)
        if data:
            out.write(f"--- Product {i} ---\n")
            for k, v in data.items():
                out.write(f"{k}: {v}\n")
            out.write("\n")
            print(" Data saved.")
        else:
            print(" Skipped (no data found).")
        
        # Optional: Delay to be polite to the server
        time.sleep(1)

print("\n All product details saved to 'carbon38_product_details.txt'")
