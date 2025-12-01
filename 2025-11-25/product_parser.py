
import json
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION, BASE_URL
from logger import get_logger
logger = get_logger("product_parser")

# -----------------------
# Custom Exception
# -----------------------
class DataMiningError(Exception):
    """Raised for errors during product parsing."""
    pass


# ------------------------------------------------------
# OOP Class for Product Detail Extraction (Task 1)
# ------------------------------------------------------
class BayutProductParser:
    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

        self.raw_file = "product_raw.html"
        self.cleaned_file = "product_cleaned.txt"

    # --------------------------------------------------
    # 1. Fetch HTML with safe exception handling (Task 4)
    # --------------------------------------------------
    def fetch_html(self, url):
        try:
            
            logger.info(f"Fetching product page ::: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} for {url}"
                )

            # Save raw HTML (Task 2)
            with open(self.raw_file, "w", encoding="utf-8") as file:
                file.write(response.text)

            return response.text

        except requests.RequestException as err:
            raise DataMiningError(f"Connection failed: {err}")

    # --------------------------------------------------
    # 2. Parse HTML (Mock BeautifulSoup using parsel) (Task 1)
    # --------------------------------------------------
    def parse_data(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"HTML parsing failed: {err}")

    # --------------------------------------------------
    # 3. Extract product details (main logic)
    # --------------------------------------------------
    def parse_product(self, url):
        html = self.fetch_html(url)
        sel = self.parse_data(html)
        
        try:
            Refencenumber = sel.xpath("//ul[@class='aff52d8a']/li[3]/span[@class='_249434d2']/text()").get()
            
            raw_id = sel.xpath("//ul[@class='aff52d8a']/li[3]/span[@class='_249434d2']/text()").get()
            if raw_id:
                id = raw_id.replace("Bayut - ", "")  # takes "ID105066590" Bayut - ID105066590
                
            purpose=sel.xpath("//span[@aria-label='Purpose']/text()").get()

            title=sel.xpath("//h1[@class='_4bbafa79 fontCompensation']/text()").get()

            description=sel.xpath("//span[@class='_812d3f30']/text()").get()    

            location=sel.xpath("//div[@aria-label='Property header']/text()").get() 

            furnished=sel.xpath("//span[@aria-label='Furnishing']/text()").get()

        
            Amenities_list = sel.xpath("//span[@class='c0327f5b']/text()").getall()

            details=sel.xpath("//span[@aria-label='Area']/span/span/text()").get()

            agent_name=sel.xpath("//span[@aria-label='Agent name']/text()").get()

            property_image_urls=sel.xpath("//div[@class='e1f8277c']/img/@src").getall()

            price_per=sel.xpath("//span[@aria-label='Frequency']/text()").get()

            breadcrumb=sel.xpath("//span[@class='b05b8cca']/text()").getall()

            script=sel.xpath("//script[@type='application/ld+json']/text()").get()
            data = json.loads(script)
            property_image_urls= data.get("@graph", [{}])[0].get("mainEntity", {}).get("image", [])
            number_of_photos=len(property_image_urls)  
            price=data.get("@graph", [{}])[0].get("mainEntity", {}).get("priceSpecification", {}).get("price")
            currency=data.get("@graph", [{}])[0].get("mainEntity", {}).get("priceSpecification", {}).get("priceCurrency")
            
            property_type=sel.xpath("//span[@aria-label='Type']/text()").get()

            return {
                
                
                "Refencenumber": Refencenumber,
                "id": id,
                "url": url,
                "purpose": purpose,
                "title":title,
                "description": description,
                "location": location,
                "price": price, 
                "currency": currency,
                "price_per": price_per,
                "furnished": furnished,
                "Amenities_list": Amenities_list,
                "details": details,
                "agent_name": agent_name,
                "number_of_photos": number_of_photos,
                "breadcrumb": breadcrumb,   
                "property_image_urls": property_image_urls,
                "property_type": property_type,
                
                


            
            }

        except Exception as err:
            raise DataMiningError(f"Failed to parse product {url}: {err}")

    # --------------------------------------------------
    # 4. Save cleaned data to file (Task 2)
    # --------------------------------------------------
    def save_to_file(self, cleaned_data):
        with open(self.cleaned_file, "w", encoding="utf-8") as file:
            for key, value in cleaned_data.items():
                file.write(f"{key}: {value}\n")

    # --------------------------------------------------
    # 5. Generator to iterate product URLs one-by-one (Task 3)
    # --------------------------------------------------
    def yield_product_urls(self):
        cursor = self.collection.find({"unique_id": {"$exists": False}})
        for document in cursor:
            
            yield document["_id"], document.get("url")


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logger.info(f"\nStarting Marks & Spencer Product Detail Scraper...\n")


        for doc_id, product_url in self.yield_product_urls():
            
            logger.info(f"\nProcessing: {product_url}")

            try:
                details = self.parse_product(product_url)

                # Save to cleaned file (only last product)
                self.save_to_file(details)

                # Update database
                self.collection.update_one(
                    {"_id": doc_id},
                    {"$set": details}
                )

                
                logger.info(f"Updated product: {product_url}\n")


            except DataMiningError as err:
               logger.info(f"Error: {err}")

    # --------------------------------------------------
    # Close DB connection (Destructor)
    # --------------------------------------------------
    def close(self):
        
        logger.info(f"Closing MongoDB connection...")
        self.client.close()

    # --------------------------------------------------
    # parse a single product (for testing)
    # --------------------------------------------------
    def parse_single_product(self, url):
        try:
            details = self.parse_product(url)
            logger.info("Extracted Product Details:")
            for key, value in details.items():
                logger.info(f"{key}: {value}")
            logger.info(f"Product details saved to {self.cleaned_file}")
        except DataMiningError as err:
            logger.error(f"{err}")