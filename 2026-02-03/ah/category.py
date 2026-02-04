from settings import MONGO_URI,MONGO_DB,CATEGORY_URL,MONGO_COLLECTION_CATEGORY, BASE_URL
import hrequests     
import logging
from urllib.parse import urljoin,urlparse
from pymongo import MongoClient
from parsel import Selector
session = hrequests.Session()

class CategoryCrawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        


    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        # .........................................................................
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.ah.nl/producten',
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

        response=session.get(CATEGORY_URL,headers=headers)
        logging.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            self.parse_item(response)
    
    def parse_item(self, response):
        """Extract category links and basic details"""
        sel=Selector(response.text)
        category_blocks=sel.xpath('//a[@class="taxonomy-card_titleLink__pdmR+"]')
        for category_block in category_blocks:
            name = category_block.xpath('./text()').get()
            relative_link = category_block.xpath('./@href').get()
            # Convert relative URL to absolute
            link = urljoin(BASE_URL, relative_link)

            parsed = urlparse(link)
            path_parts = parsed.path.strip("/").split("/")

            
            if (
                len(path_parts) < 3 or
            path_parts[0] != "producten" or
            not path_parts[1].isdigit() ):
                logging.info(f"Skipping non-category URL: {link}")
                continue

            category_id = path_parts[1]
            category_slug = path_parts[2] if len(path_parts) > 2 else None

            logging.info(f"{name} | ID: {category_id} | Slug: {category_slug}")


            item={}
            item["name"]=name
            item["link"]=link
            item["category_id"]=category_id
            item["category_slug"]=category_slug
            self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)



    def close(self):
        """Close resources"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

        
if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()




