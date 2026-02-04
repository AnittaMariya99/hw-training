from curl_cffi import requests
import logging
from pymongo import MongoClient
import re
import json
from parsel import Selector
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, BASE_URL


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser:
    """Ace Hardware Product Parser"""

    def __init__(self):
        """Initialize parser, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")

    def start(self):
        """Start parsing products"""
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.ah.nl/producten/product/wi4177/ah-broccoli',
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

        products = list(self.mongo[MONGO_COLLECTION_RESPONSE].find().limit(200))
        total = len(products)

        logging.info(f"Parser started – total urls: {total}")

        for product in products:
            url = BASE_URL + product.get('link')
            if not url:
                continue
            logging.info(f"Parsing → {url}")

            response=requests.get(url,headers=headers,impersonate="firefox")
            logging.info(response.status_code)
            if response.status_code == 200:
                self.parse_item(response)

    def parse_item(self, response):
        """Extract product details and save to DB."""
        # XPaths
        product_name_xpath = "//h1[@class='typography_typography__gMp8W typography_heading-1__517os typography_align-left__uvtNf']/text()"
        breadcrumb_xpath = "//ol[@data-testid='breadcrumb-nav-breadcrumbs']//li[contains(@class,'breadcrumbs_item')]//span/text()"
        price_xpath = "//div[contains(@class,'product-hero-title_unitInfo')]//span/text()"
        product_description_xpath = "//div[@data-testid='pdp-hero-summary']//text() | //div[@data-testid='pdp-hero-highlights']//text()"
        instructions_xpath = "//div[@data-testid='pdp-additional-information']//text()"
        product_details_xpath = "//script[@type='application/ld+json']/text()"
        servings_per_pack_xpath = "//dt[normalize-space()='Aantal porties:']/following-sibling::dd/text()"
        promotion_description_xpath = "//div[@data-key='pdp-shield-discount']//span/text()"
        ingredients_xpath = "//div[@data-testid='pdp-ingredients-list']//text()"
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
        instruction_for_use_xpath = "//div[@data-testid='pdp-usage-info']//dd//text()[normalize-space()]"
        storage_instructions_xpath = "//div[@data-testid='pdp-storage-info']//p//text()[normalize-space()]"

        sel = Selector(response.text)

        # Initialize variables
        unique_id = competitor_name = store_name = store_addressline1 = store_addressline2 = ""
        store_suburb = store_state = store_postcode = store_addressid = extraction_date = ""
        product_name = brand = brand_type = drained_weight = ""
        grammage_quantity = grammage_unit = ""
        producthierarchy_level1 = producthierarchy_level2 = producthierarchy_level3 = ""
        producthierarchy_level4 = producthierarchy_level5 = producthierarchy_level6 = producthierarchy_level7 = ""
        regular_price = selling_price = price_was = promotion_price = ""
        promotion_valid_from = promotion_valid_upto = promotion_type = percentage_discount = promotion_description = ""
        package_sizeof_sellingprice = per_unit_sizedescription = price_valid_from = price_per_unit = ""
        multi_buy_item_count = multi_buy_items_price_total = currency = pdp_url = variants = ""
        product_description = instructions = storage_instructions = preparationinstructions = instructionforuse = ""
        country_of_origin = age_of_the_product = age_recommendations = flavour = ""
        nutritional_information = vitamins = labelling = grade = region = packaging = receipies = ""
        processed_food = barcode = frozen = chilled = organictype = cooking_part = Handmade = ""
        max_heating_temperature = special_information = label_information = dimensions = ""
        special_nutrition_purpose = feeding_recommendation = warranty = color = model_number = material = ""
        usp = dosage_recommendation = tasting_note = food_preservation = size = rating = review = ""
        file_name_1 = image_url_1 = file_name_2 = image_url_2 = file_name_3 = image_url_3 = ""
        competitor_product_key = fit_guide = occasion = material_composition = style = care_instructions = ""
        heel_type = heel_height = upc = dietary_lifestyle = manufacturer_address = importer_address = distributor_address = ""
        vinification_details = recycling_information = return_address = alchol_by_volume = beer_deg = ""
        netcontent = netweight = site_shown_uom = ingredients = random_weight_flag = instock = promo_limit = ""
        product_unique_key = multibuy_items_pricesingle = perfect_match = servings_per_pack = Warning = ""
        suitable_for = standard_drinks = environmental = grape_variety = retail_limit = ""
        breadcrumb = []
        features = []
        allergens = {}
        nutritions = {}

        product_name = sel.xpath(product_name_xpath).get()
        print(product_name)
        site_shown_uom=product_name
        print(site_shown_uom)


        breadcrumb = sel.xpath(breadcrumb_xpath).getall()
        breadcrumb_path = " > ".join(breadcrumb)

        if len(breadcrumb) >= 1: producthierarchy_level1 = breadcrumb[0]
        if len(breadcrumb) >= 2: producthierarchy_level2 = breadcrumb[1]
        if len(breadcrumb) >= 3: producthierarchy_level3 = breadcrumb[2]
        if len(breadcrumb) >= 4: producthierarchy_level4 = breadcrumb[3]
        if len(breadcrumb) >= 5: producthierarchy_level5 = breadcrumb[4]
        if len(breadcrumb) >= 6: producthierarchy_level6 = breadcrumb[5]
        if len(breadcrumb) >= 7: producthierarchy_level7 = breadcrumb[6]

        print(breadcrumb_path)


        texts = sel.xpath(price_xpath).getall()

        unit = next((t.strip() for t in texts if t.strip().isalpha()), None)
        currency = "€"
        price = next((t.strip().replace(",", ".") for t in texts if "," in t or "." in t), None)

        price_per_unit = None
        if unit and price:
            price_per_unit = f"{unit} {currency} {price}"

        print(price_per_unit)


        pdp_url = response.url
        print(pdp_url)

        product_description = sel.xpath(
            product_description_xpath
        ).getall()
        


        product_description = " ".join(t.strip() for t in product_description if t.strip())

        print(product_description)


        instructions=sel.xpath(instructions_xpath).getall()
        instructions=" ".join(t.strip() for t in instructions if t.strip())
        print(instructions)

        # product_unique_key=crawler

        product_details=sel.xpath(product_details_xpath).getall()

        for product_data in product_details:
            json_data=json.loads(product_data)

            unique_id=json_data.get("sku", "")
            print(unique_id)

            image_url_1 = json_data.get("image", "")
            print(image_url_1)

            selling_price = json_data.get("offers", {}).get("price", "")

            if selling_price:
                selling_price = float(selling_price)
                print(selling_price)

            
            currency=json_data.get("offers", {}).get("priceCurrency")
            print(currency)

            instock_raw = json_data.get("offers", {}).get("availability")
            instock = instock_raw.split("/")[-1].lower() if instock_raw else ""
            print(instock)


            brand=json_data.get("brand", {}).get("name")
            print(brand)


            competitor_name=json_data.get("offers", {}).get("seller", {}).get("name")
            print(competitor_name)

            raw_grammage = json_data.get("weight", "")
            if raw_grammage:
                if raw_grammage == "per stuk":
                    grammage_quantity = 1
                    grammage_unit = "stuk"
                else:
                    parts = raw_grammage.split()
                    if len(parts) >= 2:
                        value, unit = parts[0], parts[1]
                        grammage_quantity = int(value) if value.isdigit() else 1
                        grammage_unit = unit
                    elif len(parts) == 1:
                        grammage_quantity = 1
                        grammage_unit = parts[0]
            print(grammage_quantity)
            print(grammage_unit)



        servings_per_pack=sel.xpath(servings_per_pack_xpath).get()
        print(servings_per_pack)



        promotion_description=sel.xpath(promotion_description_xpath).get()
        print(promotion_description)
        if promotion_description:
            match = re.search(r"\d+\s*%", promotion_description)
            percentage_discount = match.group(0) if match else ""
            print(percentage_discount)

        ingredients = sel.xpath(ingredients_xpath).get()
        print(ingredients)

        # netweight = raw_grammage

        alcohol_percentage = sel.xpath(alcohol_percentage_xpath).get()
        alchol_by_volume = alcohol_percentage.replace("%", "") if alcohol_percentage else ''

        print(alchol_by_volume)

        distributor_address = " ".join(
            t.strip()
            for t in sel.xpath(distributor_address_xpath).getall()
            if t.strip()
        )

        print(distributor_address)


        features = sel.xpath(features_xpath).getall()

        features = [f.strip() for f in features if f.strip()]

        print(features)


        nutritions = {}

        rows = sel.xpath(nutrition_rows_xpath)
        for row in rows:
            key = " ".join(
                t.strip() for t in row.xpath(nutrition_key_xpath).getall() if t.strip()
            )
            value = " ".join(
                t.strip() for t in row.xpath(nutrition_value_xpath).getall() if t.strip()
            )
            if key and value:
                nutritions[key] = value

        print(nutritions)


        allergens = {}

        items = sel.xpath(allergens_items_xpath)
        for item in items:
            key = " ".join(
                t.strip() for t in item.xpath(allergens_key_xpath).getall() if t.strip()
            ).replace(":", "")
            value = " ".join(
                t.strip() for t in item.xpath(allergens_value_xpath).getall() if t.strip()
            )
            if key and value:
                allergens[key] = value

        print(allergens)


        country_of_origin = sel.xpath(country_of_origin_xpath).get()

        print(country_of_origin)


        instructionforuse = sel.xpath(instruction_for_use_xpath).get()

        storage_instructions = sel.xpath(storage_instructions_xpath).get()

        print(instructionforuse)
        print(storage_instructions)


        item={}
        # unique_id,competitor_name,store_name,store_addressline1,store_addressline2,store_suburb,store_state,store_postcode,store_addressid,extraction_date,product_name,brand,brand_type,grammage_quantity,grammage_unit,drained_weight,producthierarchy_level1,producthierarchy_level2,producthierarchy_level3,producthierarchy_level4,producthierarchy_level5,producthierarchy_level6,producthierarchy_level7,regular_price,selling_price,price_was,promotion_price,promotion_valid_from,promotion_valid_upto,promotion_type,percentage_discount,promotion_description,package_sizeof_sellingprice,per_unit_sizedescription,price_valid_from,price_per_unit,multi_buy_item_count,multi_buy_items_price_total,currency,breadcrumb,pdp_url,variants,product_description,instructions,storage_instructions,preparationinstructions,instructionforuse,country_of_origin,allergens,age_of_the_product,age_recommendations,flavour,nutritions,nutritional_information,vitamins,labelling,grade,region,packaging,receipies,processed_food,barcode,frozen,chilled,organictype,cooking_part,Handmade,max_heating_temperature,special_information,label_information,dimensions,special_nutrition_purpose,feeding_recommendation,warranty,color,model_number,material,usp,dosage_recommendation,tasting_note,food_preservation,size,rating,review,file_name_1,image_url_1,file_name_2,image_url_2,file_name_3,image_url_3,competitor_product_key,fit_guide,occasion,material_composition,style,care_instructions,heel_type,heel_height,upc,features,dietary_lifestyle,manufacturer_address,importer_address,distributor_address,vinification_details,recycling_information,return_address,alchol_by_volume,beer_deg,netcontent,netweight,site_shown_uom,ingredients,random_weight_flag,instock,promo_limit,product_unique_key,multibuy_items_pricesingle,perfect_match,servings_per_pack,Warning,suitable_for,standard_drinks,environmental,grape_variety,retail_limit
        item["unique_id"] = unique_id
        item["competitor_name"] = competitor_name
        item["store_name"] = store_name
        item["store_addressline1"] = store_addressline1
        item["store_addressline2"] = store_addressline2
        item["store_suburb"] = store_suburb
        item["store_state"] = store_state
        item["store_postcode"] = store_postcode
        item["store_addressid"] = store_addressid
        item["extraction_date"] = extraction_date
        item["product_name"] = product_name
        item["brand"] = brand
        item["brand_type"] = brand_type
        item["grammage_quantity"] = grammage_quantity
        item["grammage_unit"] = grammage_unit
        item["drained_weight"] = drained_weight
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
        item["promotion_valid_from"] = promotion_valid_from
        item["promotion_valid_upto"] = promotion_valid_upto
        item["promotion_type"] = promotion_type
        item["percentage_discount"] = percentage_discount
        item["promotion_description"] = promotion_description
        item["package_sizeof_sellingprice"] = package_sizeof_sellingprice
        item["per_unit_sizedescription"] = per_unit_sizedescription
        item["price_valid_from"] = price_valid_from
        item["price_per_unit"] = price_per_unit
        item["multi_buy_item_count"] = multi_buy_item_count
        item["multi_buy_items_price_total"] = multi_buy_items_price_total
        item["currency"] = currency
        item["breadcrumb"] = breadcrumb_path
        item["pdp_url"] = pdp_url
        item["variants"] = variants
        item["product_description"] = product_description
        item["instructions"] = instructions
        item["storage_instructions"] = storage_instructions
        item["preparationinstructions"] = preparationinstructions
        item["instructionforuse"] = instructionforuse
        item["country_of_origin"] = country_of_origin
        item["allergens"] = allergens
        item["age_of_the_product"] = age_of_the_product
        item["age_recommendations"] = age_recommendations
        item["flavour"] = flavour
        item["nutritions"] = nutritions
        item["nutritional_information"] = nutritional_information
        item["vitamins"] = vitamins
        item["labelling"] = labelling
        item["grade"] = grade
        item["region"] = region
        item["packaging"] = packaging
        item["receipies"] = receipies
        item["processed_food"] = processed_food
        item["barcode"] = barcode
        item["frozen"] = frozen
        item["chilled"] = chilled
        item["organictype"] = organictype
        item["cooking_part"] = cooking_part
        item["Handmade"] = Handmade
        item["max_heating_temperature"] = max_heating_temperature
        item["special_information"] = special_information
        item["label_information"] = label_information
        item["dimensions"] = dimensions
        item["special_nutrition_purpose"] = special_nutrition_purpose
        item["feeding_recommendation"] = feeding_recommendation
        item["warranty"] = warranty
        item["color"] = color
        item["model_number"] = model_number
        item["material"] = material
        item["usp"] = usp
        item["dosage_recommendation"] = dosage_recommendation
        item["tasting_note"] = tasting_note
        item["food_preservation"] = food_preservation
        item["size"] = size
        item["rating"] = rating
        item["review"] = review
        item["file_name_1"] = file_name_1
        item["image_url_1"] = image_url_1
        item["file_name_2"] = file_name_2
        item["image_url_2"] = image_url_2
        item["file_name_3"] = file_name_3
        item["image_url_3"] = image_url_3
        item["competitor_product_key"] = competitor_product_key
        item["fit_guide"] = fit_guide
        item["occasion"] = occasion
        item["material_composition"] = material_composition
        item["style"] = style
        item["care_instructions"] = care_instructions
        item["heel_type"] = heel_type
        item["heel_height"] = heel_height
        item["upc"] = upc
        item["features"] = features
        item["dietary_lifestyle"] = dietary_lifestyle
        item["manufacturer_address"] = manufacturer_address
        item["importer_address"] = importer_address
        item["distributor_address"] = distributor_address
        item["vinification_details"] = vinification_details
        item["recycling_information"] = recycling_information
        item["return_address"] = return_address
        item["alchol_by_volume"] = alchol_by_volume
        item["beer_deg"] = beer_deg
        item["netcontent"] = netcontent
        item["netweight"] = netweight
        item["site_shown_uom"] = site_shown_uom
        item["ingredients"] = ingredients
        item["random_weight_flag"] = random_weight_flag
        item["instock"] = instock
        item["promo_limit"] = promo_limit
        item["product_unique_key"] = product_unique_key
        item["multibuy_items_pricesingle"] = multibuy_items_pricesingle
        item["perfect_match"] = perfect_match
        item["servings_per_pack"] = servings_per_pack
        item["Warning"] = Warning
        item["suitable_for"] = suitable_for
        item["standard_drinks"] = standard_drinks
        item["environmental"] = environmental
        item["grape_variety"] = grape_variety
        item["retail_limit"] = retail_limit
        
        self.mongo[MONGO_COLLECTION_DATA].insert_one(item)

    def close(self):
        """Close MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")

if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()


