import requests
from parsel import Selector
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["marksandspencer_db"]
db_collection = db["marksandspencer_products"] 

   
def scrape_marksandspencer(url):

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.marksandspencer.com/l/women',
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

    sel = Selector(response.text)
    links = sel.xpath('//a[@class="circular-navigation_circularNavigationLink__IbVNd"]/@href').getall()
    print(f"Total links found: {len(links)}")

    category_links = []
    for extracted in links:
        if extracted.startswith("http"):
            category_links.append(extracted)
        else:
            category_links.append("https://www.marksandspencer.com" + extracted)

    ppd_list_fulllinks = []   

    for category_link in category_links:

        print(f"Processing category link... : {category_link}")

        categeory_pages_links = []

# .........................................
        while category_link and category_link not in categeory_pages_links:
            print(f"Fetching page... : {category_link}")
            categeory_pages_links.append(category_link)

            
            ppd_list_response = requests.get(category_link, headers=headers)
            sel = Selector(ppd_list_response.text)
            ppd_list_links = sel.xpath("//a[@class='product-card_cardWrapper__GVSTY']/@href").getall()
            print(f"** Found {len(ppd_list_links)} product links in {category_link}")

            if len(ppd_list_links) == 0:
                print("  No more products → ending pagination")
                break

            for pl in ppd_list_links:
                if pl.startswith("http"):
                    ppd_list_fulllinks.append(pl)
                else:
                    ppd_list_fulllinks.append("https://www.marksandspencer.com" + pl)

            next_page = sel.xpath('//a[@aria-label="Next page"]/@href').get()
            category_link = f"https://www.marksandspencer.com{next_page}" if next_page else None

    print(f"Found Total {len(ppd_list_fulllinks)} product URLs:\n")
    for product_link in ppd_list_fulllinks:
        print(product_link)        
        
    print(f"\nSaving {len(ppd_list_fulllinks)} product links to MongoDB...\n") 
    for product_link in ppd_list_fulllinks:
        db_collection.update_one(
            {"product_url": product_link},
            {"$set": {"product_url": product_link}},
            upsert=True
        )
    print("Done saving product links to MongoDB.")


# # RUN FUNCTION
# scrape_marksandspencer("https://www.marksandspencer.com/c/women")
