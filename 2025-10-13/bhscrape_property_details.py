import requests
from parsel import Selector
import time

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://bahrainfinder.bh/en/sale/',
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

response = requests.get(
    'https://bahrainfinder.bh/en/property/apartment-for-sale-in-amwaj-island-461/',
    headers=headers,
)


# === Read all URLs from product_links.txt ===
with open("product_links.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total URLs to scrape: {len(urls)}")


open("property_details.txt", "w", encoding="utf-8").close()

# === Loop through each URL ===
for index, url in enumerate(urls, start=1):
    print(f"\n🔹 Processing {index}/{len(urls)}: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}, Length: {len(response.text)}")

        if response.status_code != 200:
            print(" Failed to fetch page")
            continue

        sel = Selector(response.text)

        
        name = sel.xpath("//div[@class='page-title']/h1/text()").get()
        flat = sel.xpath("//div[@class='page-title']//span/text()").get()
        price = sel.xpath("//ul[@class='item-price-wrap hide-on-list']//strong/text()").get()
        person_name = sel.xpath("normalize-space(//li[@class='agent-name']/text())").get()
        agency_name = sel.xpath("//li[@class='agent-list-position']/a/text()").get()

       
        call_number = sel.xpath("//a[starts-with(@href, 'tel:')]/@href").get()

        data = {
            "URL": url,
            "Name": name.strip() if name else None,
            "Flat": flat.strip() if flat else None,
            "Price": price.strip() if price else None,
            "Agent Name": person_name.strip() if person_name else None,
            "Agency Name": agency_name.strip() if agency_name else None,
            "Call Number": call_number.replace("tel:", "") if call_number else None,
        }

        #  Property Overview Section 
        overview = sel.xpath("//div[@class='d-flex property-overview-data']/ul")
        for ul in overview:
            key = ul.xpath("li[2]/text()").get()
            value = ul.xpath("li/strong//text()").get()
            if key and value:
                data[key.strip()] = value.strip()

      
        classification = sel.xpath("//strong/a[contains(@href, '/en/label/')]/text()").get()
        if classification:
            data["Classification"] = classification.strip()

        #  Save results to file 
        with open("property_details.txt", "a", encoding="utf-8") as f:
            f.write(f"--- Property {index} ---\n")
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
            f.write("\n")

        print(" Data saved for:", url)

       
        time.sleep(1)

    except Exception as e:
        print(" Error while scraping:", e)
        continue

print("\n Data saved in 'property_details.txt'")
