import requests
from parsel import Selector

url = "https://bahrainfinder.bh/en/sale/"
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
    url,
    headers=headers,
)


response.status_code
response.text
print(f"Status: {response.status_code}, Length: {len(response.text)}")

sel = Selector(response.text)


links = sel.xpath('//a[@class="listing-featured-thumb hover-effect"]/@href').getall()
print(f"Total links found: {len(links)}")



#  Convert relative links to full URLs 
full_links = []
for link in links:
    if link.startswith("http"):
        full_links.append(link)
    else:
        full_links.append("https://bahrainfinder.bh" + link)


print(f"Found {len(full_links)} product URLs:\n")
for l in full_links:
    print(l)

# Save 
with open("product_links.txt", "w", encoding="utf-8") as f:
    for link in full_links:
        f.write(link + "\n")

print(" All links saved to 'product_links.txt'")