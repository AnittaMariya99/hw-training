import requests
from parsel import Selector
from pymongo import MongoClient
from marksandspencercrawler import scrape_marksandspencer


client = MongoClient("mongodb://localhost:27017/")
db = client["marksandspencer_db"]
db_collection = db["marksandspencer_products"] 

url = "https://www.marksandspencer.com/"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.marksandspencer.com',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}

response = requests.get(url, headers=headers,)
print(f"Status: {response.status_code}, Length: {len(response.text)}")
with open("marksspencer.html", "w", encoding="utf-8") as f:
        f.write(response.text + "\n")

sel = Selector(response.text)
links = sel.xpath('//a[@class="media-0_body__yf6Z_ media-1280_textSm__V3PzB gnav_burgerItemHeading__8myW8 gnav_tabHeading__Qwe6W"]/@href').getall()
print(f"Total links found: {len(links)}")

#  Convert relative links to full URLs 
Main_category_links = []

for extracted in links:
    if extracted.startswith("http"):
        Main_category_links.append(extracted)
    else:
        Main_category_links.append("https://www.marksandspencer.com" + extracted)

    # print(Main_category_links)     

for main_category_link in Main_category_links:

    print(f"Processing main category link... : {main_category_link}")

    scrape_marksandspencer(main_category_link)