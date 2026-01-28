import csv
import logging
import html
from pymongo import MongoClient
from settings import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION_DATA,
    FILE_NAME
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_text(value):
    """Unescape HTML entities and ensure safe string output."""
    if value is None:
        return ""
    return html.unescape(str(value))

def export_to_csv():
    """Export data from MongoDB to CSV with cleaned text."""
    client = None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]

        # Fetch all records (exclude MongoDB ObjectID)
        data = list(collection.find({}, {'_id': 0}))

        if not data:
            logging.info("No data found in MongoDB to export.")
            return

        # Explicit field order
        field_names = [
            "company_name",
            "manufacturer_name",
            "brand_name",
            "manufacturer_part_number",
            "vendor/seller_part_number",
            "item_name",
            "full_product_description",
            "price",
            "country_of_origin",
            "unit_of_issue",
            "qty_per_uoi",
            "upc",
            "model_number",
            "product_category",
            "url",
            "availability",
            "date_crawled"
        ]

        # Write to CSV
        with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            for row in data:
                clean_row = {
                    field: clean_text(row.get(field, ""))
                    for field in field_names
                }
                writer.writerow(clean_row)

        logging.info(
            f"Successfully exported {len(data)} records to {FILE_NAME}"
        )

    except Exception as e:
        logging.error(f"An error occurred during export: {e}")

    finally:
        if client:
            client.close()

if __name__ == "__main__":
    export_to_csv()
