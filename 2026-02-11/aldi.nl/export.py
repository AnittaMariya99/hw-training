import csv
import logging
import re
from datetime import datetime
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PRICE_FIELDS = {
    "regular_price", "selling_price", "price_was", "promotion_price",
    "price_per_unit", "multi_buy_items_price_total",
    "multibuy_items_pricesingle"
}


def clean_value(value):
    if value is None:
        return ""

    if isinstance(value, (list, dict)):
        value = str(value)

    if isinstance(value, str):
        # Remove HTML tags if any
        value = re.sub(r'<[^>]+>', ' ', value)
        value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        value = value.replace("{}", "").replace("|", " ")
        value = re.sub(r"\s+", " ", value)
        return value.strip()
        
    return value


def format_price(value):
    try:
        if value in ("", None):
            return ""
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return ""


def export_to_csv():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]

        data = list(collection.find().limit(200))
        if not data:
            logging.warning("No data found in the collection.")
            return

        all_keys = [
            "unique_id", "competitor_name", "store_name", "store_addressline1",
            "store_addressline2", "store_suburb", "store_state", "store_postcode",
            "store_addressid", "extraction_date", "product_name", "brand",
            "brand_type", "grammage_quantity", "grammage_unit", "drained_weight",
            "producthierarchy_level1", "producthierarchy_level2",
            "producthierarchy_level3", "producthierarchy_level4",
            "producthierarchy_level5", "producthierarchy_level6",
            "producthierarchy_level7", "regular_price", "selling_price",
            "price_was", "promotion_price", "promotion_valid_from",
            "promotion_valid_upto", "promotion_type", "percentage_discount",
            "promotion_description", "package_sizeof_sellingprice",
            "per_unit_sizedescription", "price_valid_from", "price_per_unit",
            "multi_buy_item_count", "multi_buy_items_price_total", "currency",
            "breadcrumb", "pdp_url", "variants", "product_description",
            "instructions", "storage_instructions", "preparationinstructions",
            "instructionforuse", "country_of_origin", "allergens",
            "age_of_the_product", "age_recommendations", "flavour",
            "nutritions", "nutritional_information", "vitamins", "labelling",
            "grade", "region", "packaging", "receipies", "processed_food",
            "barcode", "frozen", "chilled", "organictype", "cooking_part",
            "handmade", "max_heating_temperature", "special_information",
            "label_information", "dimensions", "special_nutrition_purpose",
            "feeding_recommendation", "warranty", "color", "model_number",
            "material", "usp", "dosage_recommendation", "tasting_note",
            "food_preservation", "size", "rating", "review", "file_name_1",
            "image_url_1", "file_name_2", "image_url_2", "file_name_3",
            "image_url_3", "competitor_product_key", "fit_guide", "occasion",
            "material_composition", "style", "care_instructions", "heel_type",
            "heel_height", "upc", "features", "dietary_lifestyle",
            "manufacturer_address", "importer_address", "distributor_address",
            "vinification_details", "recycling_information", "return_address",
            "alchol_by_volume", "beer_deg", "netcontent", "netweight",
            "site_shown_uom", "ingredients", "random_weight_flag", "instock",
            "promo_limit", "product_unique_key",
            "multibuy_items_pricesingle", "perfect_match",
            "servings_per_pack", "warning", "suitable_for",
            "standard_drinks", "environmental", "grape_variety", "retail_limit"
        ]

        extraction_date_today = datetime.now().strftime("%Y-%m-%d")

        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[k.lower() for k in all_keys],
                extrasaction="ignore",
                delimiter="|"
            )
            writer.writeheader()

            for item in data:
                cleaned_item = {}

                # ---------- PRICING LOGIC ----------
                db_selling_price = item.get("selling_price")
                db_regular_price = item.get("regular_price")
                promotion_description = item.get("promotion_description")
                has_promo = bool(promotion_description and str(promotion_description).strip())

                if not has_promo:
                    # Case 1 & 2: No promotion description present
                    if not db_regular_price and db_selling_price:
                        # Case 1: if no regular_price then assign selling_price as regular_price
                        selling_price = db_selling_price
                        regular_price = db_selling_price
                    
                    promotion_price = ""
                    price_was = ""
                else:
                    # Case 3 & 4: Promotion description present
                    if not db_regular_price:
                        # Case 4: If promotion description present, reguler price is empty
                        # selling price = reguller price, in this case promotion price and price was empty
                        regular_price = db_selling_price
                        selling_price = db_selling_price
                        promotion_price = ""
                        price_was = ""
                    else:
                        # Case 3: If promotion description present
                        # promotion price will be the selling price and selling price & regular price will be price was
                        promotion_price = db_selling_price
                        regular_price = db_regular_price
                        selling_price = db_selling_price
                        price_was = db_regular_price

                if ">>" in (item.get("breadcrumb") or ""):
                    continue

                # ---------- WRITE CSV ----------
                for key in all_keys:
                    key_lower = key.lower()

                    if key_lower == "extraction_date":
                        value = item.get(key) or extraction_date_today

                    elif key_lower == "competitor_name":
                        value = item.get(key) or "ALDI"

                    elif key_lower == "regular_price":
                        value = regular_price

                    elif key_lower == "selling_price":
                        value = selling_price

                    elif key_lower == "promotion_price":
                        value = promotion_price

                    elif key_lower == "price_was":
                        value = price_was

                    elif key_lower.startswith("file_name_"):
                        idx = key_lower.split("_")[-1]
                        img_key = f"image_url_{idx}"
                        if item.get(img_key):
                            value = f"{item.get('unique_id')}_{idx}.jpg"
                        else:
                            value = ""
                    else:
                        value = item.get(key_lower) or item.get(key)

                    if key_lower in PRICE_FIELDS and key_lower != "price_per_unit":
                        cleaned_item[key_lower] = format_price(value)
                    else:
                        cleaned_item[key_lower] = clean_value(value)

                writer.writerow(cleaned_item)

        logging.info(f"Data exported successfully to {FILE_NAME}")
        client.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    export_to_csv()
