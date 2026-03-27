import csv
import logging
import re
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, PROJECT
from datetime import date

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def format_price(val):
    """Return value formatted as a float with two decimal places.

    Empty and None values are returned as empty string.  Any comma in the
    incoming value is treated as a decimal point.
    """
    if val is None or val == "":
        return ""
    try:
        return "{:.2f}".format(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return ""


def clean_html_tags(text):
    """Remove all HTML tags from text."""
    if not isinstance(text, str):
        return text
    # Remove all HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text


def export_to_csv():
    logging.info("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION_DATA]

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

    today_str = date.today().strftime("%Y_%m_%d")
    output_file = f"{PROJECT}_2026_03_02_sample.csv"

    logging.info(f"Fetching data from collection: {MONGO_COLLECTION_DATA}")
    # restrict to 200 samples for testing/quick export
    cursor = collection.find({}).limit(200)

    count = 0
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()

        for doc in cursor:
            row = {key: "" for key in all_keys}
            # copy fields directly
            for key in all_keys:
                if key in doc:
                    row[key] = doc[key]

            # ---------- PRICING LOGIC ----------
            db_selling_price = doc.get("selling_price")
            db_regular_price = doc.get("regular_price")
            db_price_was = doc.get("price_was")
            promotion_price = ""

            if db_price_was:
                db_regular_price = db_price_was
                promotion_price = db_selling_price

            if not db_regular_price:
                db_regular_price = db_selling_price

            row["regular_price"] = db_regular_price
            row["selling_price"] = db_selling_price


            # apply price formatting
            for price_key in ("regular_price", "selling_price", "price_was", "promotion_price", "price_per_unit"):
                if row.get(price_key) is not None:
                    row[price_key] = format_price(row[price_key])

            # clean whitespace/newlines
            for k, v in row.items():
                if isinstance(v, (dict, list)):
                    if not v:
                        v = ""
                    else:
                        v = str(v)
                if v is None:
                    v = ""
                # remove any stray control characters
                v = str(v).replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
                # clean HTML tags
                v = clean_html_tags(v)
                row[k] = v

            writer.writerow(row)
            count += 1
            if count % 1000 == 0:
                logging.info(f"Exported {count} rows...")

    logging.info(f"Export completed. {count} records saved to {output_file}")
    client.close()


if __name__ == "__main__":
    export_to_csv()
