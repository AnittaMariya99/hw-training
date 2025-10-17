import requests
from parsel import Selector
import time


input_file = "nextproduct_links.txt"     
output_file = "nextproduct_details.txt" 

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.next.co.uk/shop/gender-women-category-dresses-0?p=1',
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


with open(input_file, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total URLs to process: {len(urls)}")

with open(output_file, "w", encoding="utf-8") as f_out:
    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Scraping: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed: Status {response.status_code}")
                continue

            sel = Selector(response.text)

            # Extract data
            name = sel.xpath("//h1[@class='MuiTypography-root MuiTypography-h1 pdp-css-2mrs4v']/text()").get()
            price = sel.xpath("//div[@class='MuiTypography-root MuiTypography-h1 none pdp-css-rqnr2e']/span/text()").get()
            product_code = sel.xpath("//span[@data-testid='product-code']/text()").get()
            selected_color = sel.xpath("//span[@class='MuiTypography-root MuiTypography-body3 pdp-css-13hk9fz']/text()").get()
            fit_size = sel.xpath("//button[contains(@class,'pdp-css-1drodo6')]/text()").getall()
            available_colors = sel.xpath("//button[contains(@class,'round pdp-css-1c1nsg9')]/@aria-label").getall()
            description = sel.xpath("//p[@data-testid='item-description']/text()").getall()
            description_str = "\n".join(description).strip()

            
            product_info = f"""

URL: {url}
Name: {name}
Price: {price}
Product Code: {product_code}
Selected Colour: {selected_color}
Size Available: {fit_size}
Available Colours: {available_colors}

Description:
{description_str}

"""

           
            f_out.write(product_info + "\n")
            print("Saved product details.")

        except Exception as e:
            print(f" Error scraping {url}: {e}")

        
        time.sleep(2)

print(f"\n All product details saved to '{output_file}'")
