import logging
import json
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class DataExporter:
    """Export product data from MongoDB to pipe-delimited file"""

    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")
        
        self.all_keys = [
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
            "image_url_3", "file_name_4", "image_url_4", "file_name_5", "image_url_5",
            "file_name_6", "image_url_6", "competitor_product_key", "fit_guide", "occasion",
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

    def clean_value(self, value):
        """Clean value according to rules"""
        # Skip None, empty strings
        if value is None or value == "":
            return None

        # If value is a dict or list, serialize to compact JSON string
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        else:
            value = str(value).strip()

        # Skip na, 0, {}, empty dict/list representations
        if value.lower() in ["none", "na", "n/a", "0", "{}", "[]"]:
            return None

        # Remove special characters: \n, \r, \t
        value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")

        # Remove multiple spaces
        value = " ".join(value.split())

        # Escape internal double quotes (replace " with '') to avoid breaking CSV quoting
        value = value.replace('"', "'")

        # Escape pipe characters to avoid breaking delimiter
        value = value.replace("|", "/")

        if not value:
            return None

        return value

    def format_price(self, value):
        """Format price to 2 decimal places"""
        if value is None:
            return None
        
        try:
            # Remove currency symbols if any
            value_str = str(value).replace("€", "").replace("$", "").strip()
            if not value_str or value_str.lower() in ["none", "na", "n/a", "0"]:
                return None
            
            # Convert to float and format
            price_float = float(value_str.replace(",", "."))
            if price_float == 0:
                return None
            
            return f"{price_float:.2f}"
        except (ValueError, AttributeError):
            return None

    def process_record(self, record):
        """Process a single database record"""
        processed = {}
        
        for key in self.all_keys:
            value = record.get(key)
            
            # Special handling for price fields
            if key in ["regular_price", "selling_price", "price_was", "promotion_price", 
                       "price_per_unit", "multi_buy_items_price_total", "multibuy_items_pricesingle"]:
                formatted_value = self.format_price(value)
                processed[key] = formatted_value if formatted_value else ""
            else:
                cleaned_value = self.clean_value(value)
                processed[key] = cleaned_value if cleaned_value else ""
        
        # Apply price logics
        regular_price = processed.get("regular_price", "")
        
        # Condition 1: If regular price is empty, then selling price = regular price
        if not regular_price:
            processed["promotion_price"] = processed["price_was"] = processed["regular_price"] = processed["selling_price"]
        else:
            processed["price_was"] = regular_price
            processed["promotion_price"] = processed["selling_price"]
        
        return processed

    def export_to_file(self, output_file="dm_si_2026_03_06_sample.csv", limit=1000):
        """Export data to pipe-delimited file"""
        try:
            # Fetch up to 1000 records
            records = list(self.mongo[MONGO_COLLECTION_DATA].find().limit(limit))
            logging.info(f"Fetched {len(records)} records from database")
            
            if not records:
                logging.warning("No records found in database")
                return
            
            with open(output_file, "w", encoding="utf-8") as f:
                # Write header (all lowercase)
                header = "|".join([f'"{key}"' for key in self.all_keys])
                f.write(header + "\n")
                
                # Write data rows
                row_count = 0
                for record in records:
                    processed_record = self.process_record(record)
                    
                    # Build row with pipe delimiter and quoted values
                    row_values = [f'"{processed_record.get(key, "")}"' for key in self.all_keys]
                    row = "|".join(row_values)
                    
                    f.write(row + "\n")
                    row_count += 1
                
                logging.info(f"Successfully exported {row_count} records to {output_file}")
        
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            raise

    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()
        logging.info("MongoDB connection closed")


if __name__ == "__main__":
    exporter = DataExporter()
    exporter.export_to_file()
    exporter.close()
