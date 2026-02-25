import csv
import logging
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, PROJECT_NAME
from datetime import date

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_price(val):
    if val is None or val == "":
        return ""
    try:
        # Convert to float and format to .2f
        return "{:.2f}".format(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return val

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
    output_file = f"shop_billa_at_{today_str}.csv"

    logging.info(f"Fetching data from collection: {MONGO_COLLECTION_DATA}")
    cursor = collection.find({}).limit(200)
    
    count = 0
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        # Small letter headers (they are already small in the list, but let's ensure)
        writer.writeheader()

        for doc in cursor:
            # Handle default values
            row = {key: "" for key in all_keys}
            
            # Map existing fields
            for key in all_keys:
                if key in doc:
                    row[key] = doc[key]
            
            # Mapping aliases if names differ slightly between parser and export list
            if not row["breadcrumb"] and doc.get("breadcrumb_path"):
                row["breadcrumb"] = doc.get("breadcrumb_path")
            
            if not row["country_of_origin"] and doc.get("countryoforigin"): # check both cases
                row["country_of_origin"] = doc.get("countryoforigin")

            if not row["manufacturer_address"] and doc.get("distributor_address"):
                row["manufacturer_address"] = doc.get("distributor_address")

            # Mapping prices
            promo_desc = str(doc.get("promotion_description", "")).strip()
            selling_price = str(doc.get("selling_price", "")).strip()
            price_was = str(doc.get("price_was", "")).strip()
            regular_price = str(doc.get("regular_price", "")).strip()

            if not regular_price or regular_price == "None":
                regular_price = selling_price

            if promo_desc:
                # If promotion description is present
                row["selling_price"] = format_price(selling_price)
                if price_was:
                    row["regular_price"] = format_price(price_was)
                    row["price_was"] = format_price(price_was)
                else:
                    row["regular_price"] = format_price(regular_price)
                    row["price_was"] = format_price(regular_price)
                
                row["promotion_price"] = format_price(selling_price)
            else:
                # No promotion
                row["selling_price"] = format_price(selling_price)
                row["regular_price"] = format_price(regular_price)
                row["price_was"] = ""
                row["promotion_price"] = ""
            
            # Format other price fields if they exist in doc but weren't caught
            for p_key in ["promotion_price", "price_was"]:
                if not row[p_key] and doc.get(p_key):
                    row[p_key] = format_price(doc.get(p_key))

            # Competitor metadata
            row["competitor_name"] = "Billa"
            row["store_name"] = "Billa Online Shop"

            # Final cleaning of all fields to remove newlines, carriage returns and tabs
            for key in all_keys:
                val = row[key]
                if val is not None:
                    if isinstance(val, (dict, list)):
                        if not val:
                            val = ""
                        else:
                            val = str(val)
                    
                    cleaned_val = str(val).replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
                    if cleaned_val == "{}" or cleaned_val == "[]":
                        cleaned_val = ""
                    row[key] = cleaned_val

            writer.writerow(row)
            count += 1
            if count % 1000 == 0:
                logging.info(f"Exported {count} rows...")

    logging.info(f"Export completed. {count} records saved to {output_file}")
    client.close()

if __name__ == "__main__":
    export_to_csv()
