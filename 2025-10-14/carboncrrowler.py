import requests
from parsel import Selector
url="https://carbon38.com/en-in/collections/clothing?filter.p.m.custom.available_or_waitlist=1"
host_url="https://carbon38.com"
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': '"cacheable:fff51e5e9f133d585bdfb565e244a2a8"',
    'priority': 'u=0, i',
    'referer': 'https://carbon38.com/en-in/collections/clothing?filter.p.m.custom.available_or_waitlist=1',
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
response = requests.get(url, headers=headers)

response.status_code
response.text
print(f"Status: {response.status_code}, Length: {len(response.text)}")

sel = Selector(response.text)

links = sel.xpath('//a[contains(@class,"ProductItem__ImageWrapper")]/@href').getall()
# print(f"url: {links}")


# === Step 5: Clean and convert to absolute URLs ===
full_links = []
for link in links:
    link = link.strip()
    if link.startswith("//"):
        link = "https:" + link
    elif link.startswith("/"):
        link = host_url + link
    full_links.append(link)

# # Remove duplicates (optional)
full_links = list(set(full_links))

# # === Step 6: Print summary ===
print(f"\nTotal product links found: {len(full_links)}")
for i, link in enumerate(full_links[:5], start=1):
    print(f"{i}. {link}")

# # === Step 7: Save to a text file ===
output_file = "carbon38_product_links.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for link in full_links:
        f.write(link + "\n")

print(f"\n Saved all {len(full_links)} links to '{output_file}'")