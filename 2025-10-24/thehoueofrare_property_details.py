import requests
from parsel import Selector
import time

# === Configuration ===
input_file = "the_house_of_rare_product_links.txt"
output_file = "the_house_of_rare_product_details.txt"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': '"cacheable:619e34cf332efbf9b97b671f92297262"',
    'priority': 'u=0, i',
    'referer': 'https://thehouseofrare.com/collections/rare-rabbit-all-product?page=8',
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


# === Read all URLs from the saved file ===
with open(input_file, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total URLs to scrape: {len(urls)}")

# Clear the output file before writing
open(output_file, "w", encoding="utf-8").close()

# === Loop through each URL ===
for index, url in enumerate(urls, start=1):
    print(f"\n🔹 Processing {index}/{len(urls)}: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}, Length: {len(response.text)}")

        if response.status_code != 200:
            print(" Failed to fetch page")
            continue

        sel = Selector(text=response.text)

        # === Extract product details ===
        name = sel.xpath("//h1[@class='main-title']/span/text()").get(default="").strip()
        colour = sel.xpath("//h2[@class='sub-title']/text()").get(default="").strip()
        reguler_price = sel.xpath("//div[@class='product-items price-wrapper']//span[@class='compare-price']/span[@class='money']/text()").get(default="").strip()
        selling_price = sel.xpath("//div[@class='product-items price-wrapper']//span[@class='regular-price']/span[@class='money']/text()").get(default="").strip()
        discount = sel.xpath("//span[4]/text()").get(default="").strip()
        savings = sel.xpath("//p[@class='gst-price-text']/text()").get(default="").strip()
        size_available = sel.xpath("//span[@class='size-title']/text()").getall()
        size_available = ", ".join([s.strip() for s in size_available if s.strip()])

        # Description
        description = sel.xpath("//div[@class='content-wrapper']//p//text()").getall()
        description = " ".join([text.strip() for text in description if text.strip()])

        # Manufacturer details
        manufacturer_details = sel.xpath("//div[@class='accordion-content']//div[@class='content-wrapper']//text()").getall()
        manufacturer_details = "\n".join([text.strip() for text in manufacturer_details if text.strip()])

        # === Save data ===
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"--- Product {index} ---\n")
            f.write(f"URL: {url}\n")
            f.write(f"Name: {name}\n")
            f.write(f"Colour: {colour}\n")
            f.write(f"Regular Price: {reguler_price}\n")
            f.write(f"Selling Price: {selling_price}\n")
            f.write(f"Discount: {discount}\n")
            f.write(f"Savings: {savings}\n")
            f.write(f"Available Sizes: {size_available}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Manufacturer Details:\n{manufacturer_details}\n")
            f.write("-" * 60 + "\n\n")

        print(f" Saved details for: {name if name else 'Unnamed Product'}")

        # Short delay between requests to avoid blocking
        time.sleep(2)

    except Exception as e:
        print(f" Error while scraping {url}: {e}")
        continue

print(f"\n All product details saved in '{output_file}'")
