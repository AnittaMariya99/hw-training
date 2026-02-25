from curl_cffi import requests
import logging
from pymongo import MongoClient
import re
import json 
from parsel import Selector
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, BASE_URL, MONGO_COLLECTION_PRODUCTS, PARSER_HEADERS
from items import ProductItem
from datetime import date

session = requests.Session()


class ProductParser:


    def __init__(self):
        """Initialize parser and connect to MongoDB."""
        logging.info("Connecting to MongoDB ...")
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        self.total_saved  = 0
        logging.info("MongoDB connected.")

        self.mongo[MONGO_COLLECTION_DATA].create_index("pdp_url", unique=True)
        logging.info("Index on 'pdp_url' field created successfully.")

    def start(self):
        """Load all product URLs from MongoDB and parse each product page."""
        products = list(self.mongo[MONGO_COLLECTION_PRODUCTS].find({}, {"_id": 0, "url": 1}).limit(400))
        logging.info(f"Found {len(products)} product URLs to parse.")

        for entry in products:
            url = entry["url"]
            logging.info(f"Parsing: {url}")

            
            response = requests.get(url, headers=PARSER_HEADERS, impersonate="chrome")
            logging.info(f"  Response status: {response.status_code}")

            if response.status_code != 200:
                logging.warning(f"  Skipping – unexpected status {response.status_code}")
                continue

            self.parse_item(response, url)
            
        logging.info(f"Done – {self.total_saved} products saved to MongoDB.")

    def parse_item(self, response, url: str):
        """
        Parse a product detail page and return a fully populated product dict.
        Uses structured parsing logic from parser_workflow.py.
        """
        sel = Selector(response.text)
        
        # 1. Extract ld+json
        product_ld = {}
        breadcrumb_list = []
        ld_jsons = sel.xpath('//script[@type="application/ld+json"]/text()').getall()
        for block in ld_jsons:
            try:
                data = json.loads(block)
                if isinstance(data, dict):
                    if data.get("@type") == "Product":
                        product_ld = data
                    elif data.get("@type") == "BreadcrumbList":
                        breadcrumb_list = [item.get("name", "") for item in data.get("itemListElement", []) if item.get("name")]
            except Exception as e:
                logging.warning(f"Failed to parse ld+json block: {e}")

        breadcrumb_list.insert(0, "All categories")
        breadcrumb_path = " > ".join(breadcrumb_list)
        hierarchy = {f"producthierarchy_level{i+1}": breadcrumb_list[i] for i in range(min(len(breadcrumb_list), 7))}

        # 2. Basic fields from ld+json
        product_name = product_ld.get("name", "").strip()
        if not product_name:
            product_name = re.sub(r"\s+", " ", sel.xpath("//h1//text()").get("")).strip()

        brand = product_ld.get("brand", "")
        if isinstance(brand, dict):
            brand = brand.get("name", "")
        
        sku = product_ld.get("sku", "")
        unique_id = sku.replace("-", "")
        countryoforigin = product_ld.get("countryOfOrigin", "")
        description_raw = product_ld.get("description", "")
        description = re.sub(r"\s+", " ", " ".join(Selector(description_raw).xpath("//text()").getall())).strip() if description_raw else ""
        
        offers = product_ld.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        selling_price_str = str(offers.get("price", ""))
        currency = offers.get("priceCurrency", "EUR")
        
        price_was = sel.xpath("//div[@class='ws-product-detail__sidebar']//span[contains(@class,'ws-product-price-strike')]//s/text()|//div[@class='ws-product-detail-main__price']//div[contains(@class,'ws-product-price-strike')]//s/text()").get("").strip()
        price_was = price_was.replace("€", "").replace(",", ".")
        
        price_per_unit = sel.xpath("//div[@class='ws-product-detail-main__price']//div[@class='ws-product-price-type__label']//text()").get("").strip()
        promotion_description = sel.xpath("//div[@class='ws-product-detail-main__price']//div[@class='ws-product-price__additional-info text-discount font-weight-bold']//text()").get("").strip()
        
        # 4. Specific Content (Ingredients, Nutrition, etc.)
        def get_row_content(label):
            node = sel.xpath(f'//div[contains(@class,"ws-product-detail-row") and div[contains(text(),"{label}")]]/div[contains(@class,"content")]')
            return " ".join(node.xpath(".//text()").getall()).strip()
        
        allergens = get_row_content("Allergene")
        if "Allergene:" in allergens:
            allergens = allergens.split("Allergene:", 1)[1].strip()
        
        ingredients = get_row_content("Zutaten")
        if "Zutaten:" in ingredients:
            ingredients = ingredients.split("Zutaten:", 1)[1].strip()

        alchol_by_volume = get_row_content("Alkoholanteil")
        if "Alkoholanteil:" in alchol_by_volume:
            alchol_by_volume = alchol_by_volume.split("Alkoholanteil:", 1)[1].strip()

        nutrition = {}
        for row in sel.xpath("//table//tr"):
            cells = [re.sub(r"\s+", " ", c).strip() for c in row.xpath(".//td//text()|.//th//text()").getall() if c.strip()]
            if len(cells) >= 2:
                label = cells[0]
                nutrition[label] = {
                    "per_100g": cells[1] if len(cells) > 1 else "",
                    "per_portion": cells[2] if len(cells) > 2 else "",
                }
        
        storage_instructions = get_row_content("Aufbewahrung")
        manufacturer_address = get_row_content("Hersteller")
        label_information = get_row_content("Labelinformationen")

        netcontent = get_row_content("Abmessungen")
        netcontent_pattern = r'Netto(?:gehalt|gewicht):\s*([\d\s.,]+)\s*([A-Za-zÄÖÜäöüß]+)'
        match = re.search(netcontent_pattern, netcontent, re.IGNORECASE)

        if not match:
            return ""

        # Normalize number
        grammage_quantity = (
            match.group(1)
            .replace(" ", "")   # remove thousand spaces
            .replace(",", ".")  # normalize decimal
        )

        grammage_unit = match.group(2).strip()
        netcontent = f"{grammage_quantity} {grammage_unit}"
            
        # Images
        images_raw = product_ld.get("image", [])
        if isinstance(images_raw, str):
            images_raw = [images_raw]
        
        img_data = {}
        for i, img_url in enumerate(images_raw[:6], start=1):
            img_data[f"file_name_{i}"] = f"{unique_id}_{i}.PNG"
            img_data[f"image_url_{i}"] = img_url

        instock = "TRUE" if "InStock" in offers.get("availability", "InStock") else "FALSE"

        
        # Assembly
        item = {}
        item["unique_id"] = unique_id
        item["extraction_date"] = date.today().isoformat()
        item["product_name"] = product_name
        item["brand"] = brand
        item["selling_price"] = selling_price_str
        item["price_was"] = price_was
        item["currency"] = currency
        item["breadcrumb_path"] = breadcrumb_path
        item["pdp_url"] = url
        item["ingredients"] = ingredients
        item["nutritional_information"] = nutrition
        item["netcontent"] = netcontent
        item["site_shown_uom"] = netcontent
        item["grammage_quantity"] = grammage_quantity
        item["grammage_unit"] = grammage_unit
        item["product_unique_key"] = unique_id + "P"
        item["country_of_origin"] = countryoforigin
        item["product_description"] = description
        item["price_per_unit"] = price_per_unit
        item["promotion_description"] = promotion_description
        item["allergens"] = allergens
        item["storage_instructions"] = storage_instructions
        item["manufacturer_address"] = manufacturer_address
        item["label_information"] = label_information
        item["alchol_by_volume"] = alchol_by_volume
        item["instock"] = instock
        item.update(img_data)
        item.update(hierarchy)

        
        product_item = ProductItem(**item)            
        self.mongo[MONGO_COLLECTION_DATA].replace_one({"pdp_url": url}, item, upsert=True)
        self.total_saved += 1
        logging.info(f"    Saved: {item['product_name']} -> {item['pdp_url']}")

    def close(self):
        """Close the MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    parser = ProductParser()
    parser.start()
    parser.close()