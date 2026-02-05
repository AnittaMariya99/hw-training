import csv
import logging
import re
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
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
        value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        value = value.replace("{}", "")
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

        extraction_date_today = datetime.utcnow().strftime("%Y-%m-%d")

        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=all_keys,
                extrasaction="ignore",
                delimiter="|"
            )
            writer.writeheader()

            for item in data:
                cleaned_item = {}

                # ---------- PRICING LOGIC ----------
                regular_price = item.get("regular_price")
                selling_price = item.get("selling_price")
                promotion_price = item.get("promotion_price")
                price_was = item.get("price_was")
                promotion_description = item.get("promotion_description")

                has_promo = bool(promotion_description and str(promotion_description).strip())

                # Promotion rule
                if has_promo and selling_price:
                    promotion_price = selling_price
                    price_was = regular_price
                    selling_price = promotion_price
                    regular_price = price_was
                # Fallback rule
                if not promotion_description:
                    regular_price = selling_price


                # ---------- WRITE CSV ----------
                for key in all_keys:

                    if key == "extraction_date":
                        value = item.get(key) or extraction_date_today

                    elif key == "regular_price":
                        value = regular_price

                    elif key == "selling_price":
                        value = selling_price

                    elif key == "promotion_price":
                        value = promotion_price

                    elif key == "price_was":
                        value = price_was

                    elif key == "competitor_name":
                        value = item.get(key) or "Albert Heijn"

                    elif key == "file_name_1" and item.get("image_url_1"):
                        value = f"{item.get('unique_id')}_1.jpg"

                    elif key == "file_name_2" and item.get("image_url_2"):
                        value = f"{item.get('unique_id')}_2.jpg"

                    elif key == "file_name_3" and item.get("image_url_3"):
                        value = f"{item.get('unique_id')}_3.jpg"

                    else:
                        value = item.get(key)

                    if key in PRICE_FIELDS:
                        cleaned_item[key] = format_price(value)
                    else:
                        cleaned_item[key] = clean_value(value)

                writer.writerow(cleaned_item)

        logging.info(f"Data exported successfully to {FILE_NAME}")
        client.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    export_to_csv()
