import requests
from pymongo import MongoClient
import logging
import json
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, BASE_URL
from items import ProductItem
from datetime import date

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
            'sec-ch-ua-platform': '"Linux"',
            'Referer': 'https://www.dm.si/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'x-dm-version': '2026.304.65913-1',
            'sec-ch-ua-mobile': '?0',
        }
        products = list(self.mongo[MONGO_COLLECTION_RESPONSE].find())
        logging.info(f"Loaded {len(products)} products from DB")
        for product in products:
            url = product.get('url')
            gtin = product.get('gtin')
            product_url=f"https://products.dm.de/product/products/detail/SI/gtin/{gtin}"
            response = requests.get(product_url, headers=headers)
            logging.info(f"Status: {response.status_code} | Product: {product.get('name')}")
            if response.status_code == 200:
                self.parse(response, url)


    def parse(self, response, url=None):
        data = response.json()
        unique_id=str(data.get("gtin"))
        logging.info(unique_id)
        competitor_name="dm.si"
        logging.info(competitor_name)
        extraction_date=str(date.today())
        logging.info(extraction_date)
        product_name= data.get("title").get("headline")
        logging.info(product_name)
        brand=data.get("seoInformation").get("structuredData").get("brand")
        logging.info(brand)
       
        # pdp_url=
        product_unique_key=str(unique_id)+"P"
        logging.info(product_unique_key)
        

        labelling=data.get("pills",[])
        labelling = ", ".join(labelling)
        logging.info(labelling)

        
        variants = data.get("variants", {})

        colors = []

        for color_group in variants.get("colors", []):
            for option in color_group.get("options", []):
                label = option.get("label", "").strip()  # strip whitespace
                if label:
                    colors.append(label)

        # save as dict with colors list (use empty dict if no colors to avoid validation errors)
        variants_final = {"colors": colors} if colors else {}
        logging.info(f"variants: {variants_final}")
        # .....................................................................
        currency=  data.get("metadata").get("currency")
        review=data.get("rating",{}).get("ratingCount")
        rating=data.get("rating",{}).get("reviewCount") or data.get("rating",{}).get("ratingValue")
        logging.info(f"review: {review}")
        logging.info(f"rating: {rating}")

        # ..................................................................
        images = data.get("images", [])

        # Extract src values
        image_urls = [img.get("src", "") for img in images]

        # Fill up to 6 images
        image_urls += [""] * (6 - len(image_urls))

        image_url_1, image_url_2, image_url_3, image_url_4, image_url_5, image_url_6 = image_urls[:6]

        logging.info(f"Image URL 1: {image_url_1}")
        logging.info(f"Image URL 2: {image_url_2}")
        logging.info(f"Image URL 3: {image_url_3}")
        logging.info(f"Image URL 4: {image_url_4}")
        logging.info(f"Image URL 5: {image_url_5}")
        logging.info(f"Image URL 6: {image_url_6}")

        # ....................................................................
        breadcrumbs=data.get("breadcrumbs")
        home = "Domov"
        breadcrumb_string = [home] + breadcrumbs
        breadcrumb_string = " > ".join(breadcrumb_string)
        levels = breadcrumb_string.split(" > ")
        levels.extend([""] * (7 - len(levels)))
        (producthierarchy_level1,producthierarchy_level2,producthierarchy_level3,producthierarchy_level4,producthierarchy_level5,producthierarchy_level6,producthierarchy_level7,) = levels[:7]
        logging.info(f"breadcrumb: {breadcrumb_string}")
        logging.info(f"producthierarchy_level1: {producthierarchy_level1}")
        logging.info(f"producthierarchy_level2: {producthierarchy_level2}")
        logging.info(f"producthierarchy_level3: {producthierarchy_level3}")
        logging.info(f"producthierarchy_level4: {producthierarchy_level4}")
        logging.info(f"producthierarchy_level5: {producthierarchy_level5}")
        logging.info(f"producthierarchy_level6: {producthierarchy_level6}")
        logging.info(f"producthierarchy_level7: {producthierarchy_level7}")

        # ...............................................................
        price=data.get("price").get("infos")
        first_part = price[0].strip().split('(')[0].strip()  
        parts = first_part.split()
        gramage_quantity = parts[0].replace(',', '.')
        gramage_unit = parts[1]
        shown_uom = f"{parts[0]} {gramage_unit}"


        selling_price=data.get("price").get("price").get("current").get("value")
        selling_price = selling_price.replace('€', '').replace(',', '.')
        previous = data.get("price", {}).get("price", {}).get("previous")
        if previous:
            regular_price = previous.get("value", "").replace('€', '').replace(',', '.')
        else:
            regular_price = ""

        price = price[0]
        start = price.find('(')
        end = price.find(')', start)
        price_per_unit = price[start+1:end].strip()
        price_per_unit = price_per_unit.replace('<lineThrough>', '').replace('</lineThrough>', '')


        logging.info(f"shown_uom: {shown_uom}")
        logging.info(f"gramage_quantity: {gramage_quantity}")
        logging.info(f"gramage_unit: {gramage_unit}")
        logging.info(f"selling_price: {selling_price}")
        logging.info(f"regular_price: {regular_price}")
        logging.info(f"price_per_unit: {price_per_unit}")

        logging.info("\n-----------------\n")

        # .......................................................................

        nutritional_information = {}
        description_groups = data.get("descriptionGroups", [])

        sections = {}

        for group in description_groups:
            header = group.get("header", "").strip()
            content_blocks = group.get("contentBlock", [])

            section_parts = []

            for block in content_blocks:
                # Bulletpoints
                if "bulletpoints" in block:
                    section_parts.extend(block["bulletpoints"])

                # Texts
                if "texts" in block:
                    section_parts.extend(block["texts"])

                # DescriptionList
                if "descriptionList" in block:
                    for item in block["descriptionList"]:
                        title = item.get("title", "").strip()
                        description = item.get("description", "").strip()
                        if title and description:
                            section_parts.append(f"{title}: {description}")
                        elif description:
                            section_parts.append(item.get("description", ""))

            if header=="Hranilne vrednosti":
                table = content_blocks[0]["table"]

                column_name = table[0][1]   # "na 100 ml"

                nutritional_information = {}

                for row in table[1:]:
                    key = row[0].strip().replace(" ", "_") + "_na 100 g"
                    value = row[1].strip()
                    nutritional_information[key] = value 

            # Join section into single string
            sections[header] = "\n".join(section_parts).strip()


        # Separate variables
        product_description = sections.get("Opis izdelka", "")
        features = sections.get("Značilnosti", "")
        ingredients = sections.get("Sestavine", "")
        manufacturing_address = sections.get("Naslov podjetja", "")
        country_of_origin = sections.get("Proizvedeno v", "")
        warnings = sections.get("Opozorila") + "\n" + sections.get("Opozorilo o nevarnosti") if sections.get("Opozorila") and sections.get("Opozorilo o nevarnosti") else sections.get("Opozorila") or sections.get("Opozorilo o nevarnosti")
        storage_instructions=sections.get("Navodila za shranjevanje") 
        instructionforuse=sections.get("Navodilo za uporabo")


        logging.info(f"product_description: {product_description}")
        logging.info("\n-----------------\n")
        logging.info(f"features: {features}")
        logging.info("\n-----------------\n")
        logging.info(f"ingredients: {ingredients}")
        logging.info("\n-----------------\n")
        logging.info(f"manufacturer_address: {manufacturing_address}")
        logging.info("\n-----------------\n")
        logging.info(f"country_of_origin: {country_of_origin}")
        logging.info("\n-----------------\n")
        logging.info(f"warnings: {warnings}")
        logging.info("\n-----------------\n")
        logging.info(f"storage_instructions: {storage_instructions}")
        logging.info("\n-----------------\n")
        logging.info(f"instructionforuse: {instructionforuse}")
        logging.info("\n-----------------\n")
        logging.info(f"nutritional_information: {nutritional_information}")
        logging.info("\n-----------------\n")

        item={}
        item["unique_id"] = unique_id   
        item["competitor_name"] = competitor_name
        item["extraction_date"] = extraction_date
        item["product_name"] = product_name
        item["brand"] = brand
        item["breadcrumb"] = breadcrumb_string
        item["pdp_url"] = url
        item["product_unique_key"] = product_unique_key
        item["labelling"] = labelling
        item["variants"] = variants_final
        item["currency"] = currency
        item["review"] = str(review) if review else ""
        item["rating"] = str(rating) if rating else ""
        item["image_url_1"] = image_url_1
        item["image_url_2"] = image_url_2
        item["image_url_3"] = image_url_3
        item["image_url_4"] = image_url_4
        item["image_url_5"] = image_url_5
        item["image_url_6"] = image_url_6
        item["producthierarchy_level1"] = producthierarchy_level1
        item["producthierarchy_level2"] = producthierarchy_level2
        item["producthierarchy_level3"] = producthierarchy_level3
        item["producthierarchy_level4"] = producthierarchy_level4
        item["producthierarchy_level5"] = producthierarchy_level5
        item["producthierarchy_level6"] = producthierarchy_level6
        item["producthierarchy_level7"] = producthierarchy_level7
        item["site_shown_uom"] = shown_uom
        item["grammage_quantity"] = gramage_quantity
        item["grammage_unit"] = gramage_unit
        item["selling_price"] = selling_price
        item["regular_price"] = regular_price
        item["price_per_unit"] = price_per_unit
        item["product_description"] = product_description
        item["features"] = features
        item["ingredients"] = ingredients
        item["manufacturer_address"] = manufacturing_address
        item["country_of_origin"] = country_of_origin
        item["warnings"] = warnings
        item["storage_instructions"] = storage_instructions
        item["instructionforuse"] = instructionforuse
        item["nutritional_information"] = json.dumps(nutritional_information) if nutritional_information else ""

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
