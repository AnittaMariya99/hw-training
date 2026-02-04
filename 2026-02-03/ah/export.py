import csv
import logging
import re
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_value(value):
    """Clean unwanted characters from a value."""
    if value is None:
        return ""

    # Convert list/dict to string
    if isinstance(value, (list, dict)):
        value = str(value)

    if isinstance(value, str):
        # Remove newlines, tabs, carriage returns
        value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")

        # Remove curly braces
        value = value.replace("{", "").replace("}", "")

        # Collapse multiple spaces
        value = re.sub(r"\s+", " ", value)

        return value.strip()

    return value


def export_to_csv():
    """Fetch data from MongoDB and export to CSV"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]

        data = list(collection.find())
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
            "Handmade", "max_heating_temperature", "special_information",
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
            "servings_per_pack", "Warning", "suitable_for",
            "standard_drinks", "environmental", "grape_variety", "retail_limit"
        ]

        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=all_keys, extrasaction="ignore")
            writer.writeheader()

            for item in data:
                cleaned_item = {}
                for key in all_keys:
                    cleaned_item[key] = clean_value(item.get(key))

                writer.writerow(cleaned_item)

        logging.info(f"Data exported successfully to {FILE_NAME}")
        client.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    export_to_csv()

