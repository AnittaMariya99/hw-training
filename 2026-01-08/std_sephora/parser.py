import logging
import time
import requests
import re
from urllib.parse import urlparse
from settings import (HEADERS, BASE_API, INCLUDE_PARAMS, MONGO_DB, MONGO_HOST, MONGO_PORT, MONGO_COLLECTION_DATA)
from items import ProductUrlItem, ProductCategoryUrlItem, ProductDataItem, ProductFailedItem 
from mongoengine import connect

class Parser:
    """Sephora API Product Parser — Clean Working Version"""
    def __init__(self):
        self.mongo = connect(db=MONGO_DB,host=MONGO_HOST,port=MONGO_PORT, alias="default")

    def start(self):
        total = ProductUrlItem.objects().count()
        logging.info(f"Total Product URLs: {total}")
        count = 0
        for doc in ProductUrlItem.objects():
            url = doc.product_url
            if not url:
                continue
            count += 1
            logging.info(f"[{count}/{total}] → {url}")
            parts = urlparse(url).path.strip("/").split("/")
            if len(parts) < 2:
                logging.error(f"Invalid URL → {url}")
                continue

            product_slug = parts[1]
            variant = parts[3] if len(parts) > 3 else None

            # Default API
            api = f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}"
            if variant:
                api = f"{BASE_API}{product_slug}?v={variant}&include={INCLUDE_PARAMS}"
            logging.info(f"API → {api}")
            res = requests.get(api, headers=HEADERS)
            
            # Retry without variant if 422
            if res.status_code == 422:
                res = requests.get(f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}", headers=HEADERS)
            
            if res.status_code != 200:
                logging.error(f"API Failed {res.status_code} → {url}")
                continue
                
            response_json = res.json()
            self.parse_item(url, response_json)
            time.sleep(1)


    def parse_item(self, url, data):

        data_obj = data.get("data", {})
        attr = data_obj.get("attributes", {})
        included = data.get("included") or []
        
        skin_types = []
        for obj in included:
            attrs = obj.get("attributes", {})
            value = attrs.get("value")
            filter_type = attrs.get("filter-type-id")
            skin_types.append(value)

        clean_skin_type = list(set(skin_types))

        clean_ingredients   = attr.get("ingredients")
        if clean_ingredients:
            clean_ingredients = clean_ingredients.replace("<b>", "").replace("</b>", "").strip()
            
        clean_directions    = attr.get("how_to")
        clean_disclaimer    = attr.get("safety_warning")
        clean_description   = attr.get("description")
        if clean_description:
            clean_description = clean_description.replace("<p>", "").replace("</p>", "").strip()
                
        clean_heading = attr.get("heading")
        quantity, unit = "", ""
        if clean_heading:
            match = re.search(r'([\d.]+)\s*([a-zA-Z]+)', str(clean_heading))
            if match:
                quantity, unit = match.groups()
  
        original_price = attr.get("display-original-price")
        if original_price:
            original_price = str(original_price).replace("$", "").strip()

        selling_price = attr.get("display-price")
        if selling_price:
            selling_price = str(selling_price).replace("$", "").strip()

        promotion_description = attr.get("sale-text")or ""
        skin_tone=""


        # Mapping to ProductItem (generic + specific fields)
        item = {}
        item["url"] = url
        item["product_name"] = attr.get("name")
        item["brand"] = attr.get("brand-name")
        item["currency"] = "SGD"
        item["retailer_id"] = data_obj.get("id")
        item["retailer"] = "Sephora SG"
        item["grammage_quantity"] = quantity
        item["grammage_unit"] = unit
        item["original_price"] = original_price
        item["selling_price"] = selling_price
        item["promotion_description"] = promotion_description
        item["pdp_url"] = url
        item["image_url"] = attr.get("image-urls") or []
        item["ingredients"] = clean_ingredients
        item["directions"] = clean_directions
        item["disclaimer"] = clean_disclaimer
        item["description"] = clean_description
        item["diet_suitability"] = attr.get("diet_suitability")
        item["colour"] = attr.get("colour")
        item["hair_type"] = attr.get("hair_type")
        item["skin_type"] = clean_skin_type
        item["skin_tone"] = skin_tone
        
    
        ProductDataItem(**item).save()
        logging.info(f"Saved → {item['product_name']}")
        

    def close(self):
        self.mongo.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    p = Parser()
    p.start()
    p.close()

