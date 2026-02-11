import requests
import logging
from pymongo import MongoClient
import re
import json 
from parsel import Selector
from urllib.parse import urljoin
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, BASE_URL
from items import ProductItem
session = requests.Session()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser:
    """Ace Hardware Product Parser"""

    def __init__(self):
        """Initialize parser, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")

        self.mongo[MONGO_COLLECTION_DATA].create_index("pdp_url", unique=True)
        logging.info("Index on 'pdp_url' field created successfully.")
       

    def start(self):
        """Start parsing products"""
        products = list(self.mongo[MONGO_COLLECTION_RESPONSE].find().limit(400))


        total = len(products)

        logging.info(f"Parser started – total urls: {total}")

        for product in products:
            link = product.get('link')
            if not link:
                continue
            response = session.get(link)
            logging.info(f"Status code: {response.status_code}")
            if response.status_code == 200:
                self.parse_item(response,link)

    def parse_item(self, response, link):
        # Initializing utilized variables
        product_id = ""
        product_name = ""
        brand_name = ""
        grammage_quantity = ""
        grammage_unit = ""
        regular_price = ""
        percentage_discount = ""
        promotion_description = ""
        price_per_unit = ""
        breadcrumb = ""
        product_description = ""
        image_url_1 = ""
        file_name_1 = ""
        image_url_2 = ""
        file_name_2 = ""
        image_url_3 = ""
        file_name_3 = ""
        sales_unit = ""
        product_unique_key = ""
        
        sel = Selector(response.text)
        script_json = sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        if script_json:
            data = json.loads(script_json)
            api_data_string = data.get("props", {}).get("pageProps", {}).get("apiData", "[]")
            api_data = json.loads(api_data_string)
            
            for item in api_data:
                if isinstance(item, list) and len(item) > 1 and item[0] == "PRODUCT_DETAIL_GET":
                    res = item[1].get("res", {})
                    current_category_name = res.get("parentCategory", {}).get("data", {}).get("current", {}).get("categoryName", "")
                    parent_category_name = res.get("parentCategory", {}).get("data", {}).get("parent", {}).get("categoryName", "")
                    

                    products = res.get("products", [])
                    if products:
                        product = products[0]
                        product_name = product.get("name", "")
                        breadcrumb = f"ALDI Supermarkten > Product > {parent_category_name} > {current_category_name} > {product_name}"
                        product_id = product.get("objectID", "")
                        product_unique_key = product_id + "P"
                        brand_name = product.get("brandName", "")
                        

                    

        #  ..................................................................
                    

                        sales_unit = product.get("salesUnit", "").lower()
                
                        grammage_quantity = ""
                        grammage_unit = ""

                        handled = False

                        # 1. Fixed keyword cases
                        fixed_map = {
                            
                            "per piece": ("1", "piece"),
                            "per kilo": ("1", "kilo"),
                            "per stuk": ("1", "piece"),
                            "per tros": ("1", "tros"),
                            "per kg": ("1", "kg"),  
                            "per bos": ("1", "bos"),
                            "per bundel": ("1", "bundel"),
                            "per bundle": ("1", "bundle")
                        }

                        for key, (qty, unit) in fixed_map.items():
                            if key in sales_unit:
                                grammage_quantity = qty
                                grammage_unit = unit
                                handled = True
                                break

                        # 2. Range with unit (e.g. 5-20 stuks, 300-325 g)
                        if not handled:
                            range_match = re.search(
                                r'(\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)\s*'
                                r'(kg|g|ml|l|stuks|piece|bos|bundel|bundle)',
                                sales_unit
                            )
                            if range_match:
                                grammage_quantity = range_match.group(1).replace(" ", "")
                                grammage_unit = range_match.group(2)
                                handled = True

                        # 3. Multiplication (e.g. 12x100 g)
                        if not handled:
                            multi_match = re.search(
                                r'(\d+\s*x\s*\d+(?:\.\d+)?)\s*(kg|g|ml|l)',
                                sales_unit
                            )
                            if multi_match:
                                grammage_quantity = multi_match.group(1).replace(" ", "")
                                grammage_unit = multi_match.group(2)
                                handled = True

                        # 4. Pack cases (e.g. 2-pack)
                        if not handled:
                            pack_match = re.search(r'\b(\d+)\s*-?\s*pack\b', sales_unit)
                            if pack_match:
                                grammage_quantity = pack_match.group(1)
                                grammage_unit = "pack"
                                handled = True

                        # 5. Default extraction (LAST quantity–unit pair wins)
                        if not handled:
                            matches = re.findall(
                                r'(\d+(?:\.\d+)?(?:\s*\+\s*\d+(?:\.\d+)?)*)\s*'
                                r'(kg|g|ml|l|stuks|piece|bos|bundel|bundle)',
                                sales_unit
                            )
                            if matches:
                                grammage_quantity = matches[-1][0].replace(" ", "")
                                grammage_unit = matches[-1][1]

        #................................................................................

                        base_price_list = product.get("currentPrice", {}).get("basePrice", [])
                        base_price_info = base_price_list[0] if base_price_list else {}
                        base_price_value = base_price_info.get("basePriceValue", "")
                        base_price_scale = base_price_info.get("basePriceScale", "")
                        price_per_unit = f"{base_price_scale} = {base_price_value}" if base_price_scale and base_price_value else ""

                        long_description_description = product.get("longDescription", "")
                        short_description = product.get("shortDescription", "")
                        product_description = short_description + " " + long_description_description

                        # Price logic
                        current_price = product.get("currentPrice", {})
                        price = current_price.get("priceValue", "")
                        regular_price = current_price.get("strikePrice", {}).get("strikePriceValue", "")
                        promotion_description=current_price.get("priceTagLabels",{}).get("promoText1", "")
                        match = re.search(r'(\d+)\s*%', promotion_description)
                        percentage_discount = match.group(1) if match else ""
                        
                        # Image logic
                        assets = product.get("assets", [])
                        image_url_1 = ""
                        image_url_2 = ""
                        image_url_3 = ""
                        file_name_1 = ""
                        file_name_2 = ""
                        file_name_3 = ""
                        images = []
                        for asset in assets:
                            if asset.get("type") in ("primary", "gallery"):
                                img_url = asset.get("url")
                                if img_url:
                                    images.append(img_url)

                        # Remove duplicates
                        images = list(set(images))
                        images = images[:3]
                        # Assign images to local variables
                        if len(images) > 0:
                            image_url_1 = images[0]
                            file_name_1 = f"{product_id}_1"
                        if len(images) > 1:
                            image_url_2 = images[1]
                            file_name_2 = f"{product_id}_2"
                        if len(images) > 2:
                            image_url_3 = images[2]
                            file_name_3 = f"{product_id}_3"
                        
                        
                       

        item={}
        item["unique_id"] = product_id
        item["pdp_url"] = link
        item["product_name"] = product_name
        item["brand"] = brand_name
        item["product_description"] = product_description
        item["price_per_unit"] = price_per_unit
        item["selling_price"] = str(price)
        item["regular_price"] = str(regular_price)
        item["image_url_1"] = image_url_1
        item["image_url_2"] = image_url_2
        item["image_url_3"] = image_url_3
        item["file_name_1"] = file_name_1
        item["file_name_2"] = file_name_2
        item["file_name_3"] = file_name_3
        item["site_shown_uom"] = sales_unit
        item["grammage_quantity"] = grammage_quantity
        item["grammage_unit"] = grammage_unit
        item["promotion_description"] = promotion_description
        item["percentage_discount"] = percentage_discount
        item["product_unique_key"] = product_unique_key
        item["breadcrumb"] = breadcrumb

        product_item = ProductItem(**item)
        product_item.validate()
        self.mongo[MONGO_COLLECTION_DATA].update_one({"unique_id": item["unique_id"]}, {"$set": item}, upsert=True)




            

    def close(self):
        """Close MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()