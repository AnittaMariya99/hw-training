
from curl_cffi import requests
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
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.ah.nl/producten/product/wi221495/ah-wortelen',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        

        products = list(self.mongo[MONGO_COLLECTION_RESPONSE].find().limit(300))
        # products=[]
        # products.append({"link": "https://www.ah.nl/producten/product/wi4180/ah-aubergine"})
        total = len(products)

        logging.info(f"Parser started – total urls: {total}")

        for product in products:
            link = product.get('link')
            if not link:
                continue
            url = urljoin(BASE_URL, link)
            logging.info(f"Parsing → {url}")

            response = session.get(url, headers=headers, impersonate="chrome110")
            logging.info(response.status_code)
            if response.status_code == 200:
                self.parse_item(response)

    def parse_item(self, response):
        """Extract product details and save to DB."""
        # XPaths
        product_name_xpath = "//h1[@class='typography_typography__gMp8W typography_heading-1__517os typography_align-left__uvtNf']/text()"
        breadcrumb_xpath = "//ol[@data-testid='breadcrumb-nav-breadcrumbs']//li[contains(@class,'breadcrumbs_item')]//span/text()"
        price_xpath = "//div[contains(@class,'product-hero-title_unitInfo')]//span[last()]//text()"
        product_description_xpath = "//div[@data-testid='pdp-hero-summary']//text() | //ul[contains(@class,'list_root')]//li//text()"
        instructions_xpath = "//div[@data-testid='pdp-additional-information']//text()"
        product_details_xpath = "//script[@type='application/ld+json']/text()"
        servings_per_pack_xpath = "//dt[normalize-space()='Aantal porties:']/following-sibling::dd/text()"
        promotion_description_xpath = "//div[@class='promotion-label-base_base__aRg3h promotion-label_discount__t3rKC promotion-label_promotionLabelTokens__BnXvR']/@aria-label"
        ingredients_xpath = "//div[@data-testid='pdp-ingredients-list']//p//text()"
        alcohol_percentage_xpath = "//dt[normalize-space()='Alcoholpercentage:']/following-sibling::dd/text()"
        distributor_address_xpath = "//address//p//text()"
        features_xpath = "//div[@data-testid='pdp-logos']//ul//li//span//text()"
        nutrition_rows_xpath = "//tbody//tr"
        nutrition_key_xpath = "./td[1]//text()"
        nutrition_value_xpath = "./td[2]//text()"
        allergens_items_xpath = "//div[@data-testid='pdp-ingredients-allergens']//dl//span"
        allergens_key_xpath = ".//dt//text()"
        allergens_value_xpath = ".//dd//text()"
        country_of_origin_xpath = "//div[@data-testid='pdp-origin-info']//p//text()[normalize-space()]"
        instruction_for_use_xpath = "//div[@data-testid='pdp-usage-info']//text()"
        storage_instructions_xpath = "//div[@data-testid='pdp-storage-info']//p//text()"
        regular_price_xpath = "//div[contains(@class,'product-hero_priceAndControls')]//p[contains(@class,'original-price_root')]/text()"
        image_scripts_xpath = "//script/text()"

        sel = Selector(response.text)

        # Initialize variables
        unique_id = ""
        extraction_date = ""
        product_name = ""
        brand = ""
        grammage_quantity = ""
        grammage_unit = ""
        producthierarchy_level1 = ""
        producthierarchy_level2 = ""
        producthierarchy_level3 = ""
        producthierarchy_level4 = ""
        producthierarchy_level5 = ""
        producthierarchy_level6 = ""
        producthierarchy_level7 = ""
        regular_price = ""
        selling_price = 0.0
        price_was = ""
        promotion_price = ""
        percentage_discount = ""
        promotion_description = ""
        price_per_unit = ""
        currency = ""
        breadcrumb_path = ""
        pdp_url = ""
        product_description = ""
        instructions = ""
        storage_instructions = ""
        instructionforuse = ""
        country_of_origin = ""
        allergens = ""
        nutritional_information = {}
        image_url_1 = ""
        image_url_2 = ""
        image_url_3 = ""
        features = ""
        distributor_address = ""
        alchol_by_volume = ""
        site_shown_uom = ""
        ingredients = ""
        product_unique_key = ""
        servings_per_pack = ""
        breadcrumb_path=""
        features = ""
        # ................................................................................# 

        image_urls = set()
        url_pattern = re.compile(
            r'https:\/\/static\.ah\.nl\/dam\/product\/.*?fileType=binary'
        )
        best_images = {}
        # print("\n\nimages")
        for script in sel.xpath(image_scripts_xpath).getall():
            
            if "self.__next_f.push" in script and "product-detail-page" in script:
                matches = url_pattern.findall(script)
                for url in matches:
                    url = url.replace("\\u0026", "&").strip()
                    # print(f"url: rejects detected url:::::: {url}")
                    match = re.search(r"(AHI_\d+)", url)
                    image_id = match.group(1) if match else url
                    if image_id not in best_images:
                        # print("new url detected")
                        best_images[image_id] = url
                    else:
                        # print("url already exists")
                        existing_url = best_images[image_id]
                        if "800x800" in url and "800x800" not in existing_url:
                            # print(f"800x800 {url}")
                            best_images[image_id] = url
                        elif "400x400" in url and "800x800" not in existing_url:
                            # print(f"400x400 {url}")
                            best_images[image_id] = url
                        

        for url in best_images.values():
            image_urls.add(url)

        image_url_1 = image_urls.pop() if image_urls else ""
        image_url_2 = image_urls.pop() if image_urls else ""
        image_url_3 = image_urls.pop() if image_urls else ""
        logging.info(f"image_url_1: {image_url_1}")
        logging.info(f"image_url_2: {image_url_2}")
        logging.info(f"image_url_3: {image_url_3}")
        # ................................................................................# 
        product_name = sel.xpath(product_name_xpath).get()
        logging.info(f"product_name: {product_name}")
    
        

        breadcrumb = []
        breadcrumb = sel.xpath(breadcrumb_xpath).getall()
        breadcrumb_path = " > ".join(breadcrumb)
        if len(breadcrumb) >= 1: producthierarchy_level1 = breadcrumb[0]
        if len(breadcrumb) >= 2: producthierarchy_level2 = breadcrumb[1]
        if len(breadcrumb) >= 3: producthierarchy_level3 = breadcrumb[2]
        if len(breadcrumb) >= 4: producthierarchy_level4 = breadcrumb[3]
        if len(breadcrumb) >= 5: producthierarchy_level5 = breadcrumb[4]
        if len(breadcrumb) >= 6: producthierarchy_level6 = breadcrumb[5]
        if len(breadcrumb) >= 7: producthierarchy_level7 = breadcrumb[6]
        logging.info(f"breadcrumb_path: {breadcrumb_path}")


        price_per_unit = sel.xpath(price_xpath).getall()    
        price_per_unit = " ".join(price_per_unit)
        logging.info(f"price_per_unit: {price_per_unit}")


        pdp_url = str(response.url)
        logging.info(f"pdp_url: {pdp_url}")
        

        product_description = sel.xpath(product_description_xpath).getall()
        #remove repetion in product_description array before joining with \n
        product_description_unique = []
        for text_part in product_description:
            text_part = text_part.strip()
            if text_part and text_part not in product_description_unique:
                product_description_unique.append(text_part)
        product_description = "\n".join(f"{text_part}" for text_part in product_description_unique)
        logging.info(f"Product Description:\n{product_description}\n\n")


        instructions=sel.xpath(instructions_xpath).getall()
        instructions=" ".join(text_part.strip() for text_part in instructions if text_part.strip())
        logging.info(f"instructions: {instructions}")


        servings_per_pack=sel.xpath(servings_per_pack_xpath).get()
        logging.info(f"servings_per_pack: {servings_per_pack}")


        promotion_description=sel.xpath(promotion_description_xpath).get()
        logging.info(f"promotion_description: {promotion_description}")
        


        ingredients = sel.xpath(ingredients_xpath).getall()
        ingredients = " ".join(text_part.strip() for text_part in ingredients if text_part.strip())
        logging.info(f"ingredients: {ingredients}")


        alcohol_percentage = sel.xpath(alcohol_percentage_xpath).get()
        alchol_by_volume = alcohol_percentage.replace("%", "") if alcohol_percentage else ''
        logging.info(f"alchol_by_volume: {alchol_by_volume}")


        distributor_address = " ".join(text_part.strip() for text_part in sel.xpath(distributor_address_xpath).getall() if text_part.strip())
        logging.info(f"distributor_address: {distributor_address}")


        features = sel.xpath(features_xpath).getall()
        features = [text_part.strip() for text_part in features if text_part.strip()]
        features = ",".join(features)
        logging.info(f"features: {features}")


        nutritional_information = {}
        rows = sel.xpath(nutrition_rows_xpath)
        for row in rows:
            key = " ".join(
                text_part.strip() for text_part in row.xpath(nutrition_key_xpath).getall() if text_part.strip()
            )
            value = " ".join(
                text_part.strip() for text_part in row.xpath(nutrition_value_xpath).getall() if text_part.strip()
            )
            if key and value:
                nutritional_information[key] = value
        logging.info(f"nutritional_information: {nutritional_information}")


        allergens_dict = {}
        items = sel.xpath(allergens_items_xpath)
        for item in items:
            key = " ".join(
                text_part.strip() for text_part in item.xpath(allergens_key_xpath).getall() if text_part.strip()
            ).replace(":", "")
            value = " ".join(
                text_part.strip() for text_part in item.xpath(allergens_value_xpath).getall() if text_part.strip()
            )
            if key and value:
                allergens_dict[key] = value
        # convert dict to string
        allergens = ",".join([f"{k}:{v}" for k, v in allergens_dict.items()])
        logging.info(f"allergens: {allergens}")    


        country_of_origin = sel.xpath(country_of_origin_xpath).get()
        logging.info(f"country_of_origin: {country_of_origin}")


        instructionforuse = sel.xpath(instruction_for_use_xpath).getall()
        instructionforuse = " ".join(instructionforuse)
        logging.info(f"instructionforuse: {instructionforuse}")


        storage_instructions = sel.xpath(storage_instructions_xpath).getall()
        storage_instructions = " ".join(storage_instructions)   
        logging.info(f"storage_instructions: {storage_instructions}")


        regular_price = sel.xpath(regular_price_xpath).getall()
        regular_price = "".join(regular_price)
        logging.info(f"regular_price: {regular_price}")


        product_details=sel.xpath(product_details_xpath).getall()
        for product_data in product_details:
            json_data=json.loads(product_data)

            unique_id=json_data.get("sku", "")
            logging.info(f"unique_id: {unique_id}")

            product_unique_key=unique_id+"P"
            logging.info(f"product_unique_key: {product_unique_key}")

            selling_price = json_data.get("offers", {}).get("price", "")
            if selling_price:
                selling_price = float(selling_price)
                logging.info(f"selling_price: {selling_price}")

            currency=json_data.get("offers", {}).get("priceCurrency")
            logging.info(f"currency: {currency}")

            instock_raw = json_data.get("offers", {}).get("availability")
            instock = instock_raw.split("/")[-1].lower() if instock_raw else ""
            if instock == "instock":
                instock = "TRUE"
            else:
                instock = "FALSE"
            logging.info(f"instock: {instock}")

            brand=json_data.get("brand", {}).get("name")
            logging.info(f"brand: {brand}")

            competitor_name=json_data.get("offers", {}).get("seller", {}).get("name")
            logging.info(f"competitor_name: {competitor_name}")

            raw_grammage = json_data.get("weight", "")
            if isinstance(raw_grammage, dict):
                raw_grammage = raw_grammage.get("value", "")
            
            site_shown_uom = str(raw_grammage)
            logging.info(f"site_shown_uom: {site_shown_uom}")
            if raw_grammage:
                if raw_grammage == "per stuk":
                    grammage_quantity = 1
                    grammage_unit = "stuk"
                else:
                    if isinstance(raw_grammage, str) and "|" in raw_grammage:
                        raw_grammage = raw_grammage.split("|")[0]
                    
                    if isinstance(raw_grammage, str):
                        parts = raw_grammage.split()
                    else:
                        parts = []
                    if len(parts) >= 2:
                        value, unit = parts[0], parts[1]
                        grammage_quantity = int(value) if value.isdigit() else 1
                        grammage_unit = unit
                    elif len(parts) == 1:
                        grammage_quantity = 1
                        grammage_unit = parts[0]
            logging.info(f"grammage_quantity: {grammage_quantity}")
            logging.info(f"grammage_unit: {grammage_unit}")
            



        item={}
        item["unique_id"] = unique_id
        item["extraction_date"] = extraction_date
        item["product_name"] = product_name
        item["brand"] = brand
        item["grammage_quantity"] = str(grammage_quantity) if grammage_quantity is not None else ""
        item["grammage_unit"] = grammage_unit
        item["producthierarchy_level1"] = producthierarchy_level1
        item["producthierarchy_level2"] = producthierarchy_level2
        item["producthierarchy_level3"] = producthierarchy_level3
        item["producthierarchy_level4"] = producthierarchy_level4
        item["producthierarchy_level5"] = producthierarchy_level5
        item["producthierarchy_level6"] = producthierarchy_level6
        item["producthierarchy_level7"] = producthierarchy_level7
        item["regular_price"] = regular_price
        item["selling_price"] = selling_price
        item["price_was"] = price_was
        item["promotion_price"] = promotion_price
        item["percentage_discount"] = percentage_discount
        item["promotion_description"] = promotion_description
        item["price_per_unit"] = price_per_unit
        item["currency"] = currency
        item["breadcrumb"] = breadcrumb_path
        item["pdp_url"] = pdp_url
        item["product_description"] = product_description
        item["instructions"] = instructions
        item["storage_instructions"] = storage_instructions
        item["instructionforuse"] = instructionforuse
        item["country_of_origin"] = country_of_origin
        item["allergens"] = allergens
        item["nutritional_information"] = nutritional_information
        item["image_url_1"] = image_url_1
        item["image_url_2"] = image_url_2
        item["image_url_3"] = image_url_3
        item["features"] = features
        item["distributor_address"] = distributor_address
        item["alchol_by_volume"] = alchol_by_volume
        item["site_shown_uom"] = site_shown_uom
        item["ingredients"] = ingredients
        item["product_unique_key"] = product_unique_key
        item["servings_per_pack"] = servings_per_pack
        item["instock"] = instock
        item["competitor_name"] = competitor_name
        if not item.get("unique_id"):
            logging.warning(f"Skipping saving - unique_id is empty for {item.get('pdp_url')}")
            return

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




