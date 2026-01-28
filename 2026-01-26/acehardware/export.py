import csv
import logging
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def export_to_csv():
    """Export data from MongoDB to CSV."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]

        # Fetch all records
        data = list(collection.find({}, {'_id': 0})) # Exclude MongoDB ObjectID

        if not data:
            logging.info("No data found in MongoDB to export.")
            return

        # Get field names from the first record (or define them explicitly)
        # Defining them explicitly to ensure order
        field_names = [
            "company_name",
            "brand",
            "manufacturer_part_number",
            "vendor_part_number",
            "item_name",
            "full_product_description",
            "price",
            "country_of_origin",
            "upc",
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
                # Ensure all fields are present even if None
                clean_row = {field: row.get(field, "") for field in field_names}
                writer.writerow(clean_row)

        logging.info(f"Successfully exported {len(data)} records to {FILE_NAME}")

    except Exception as e:
        logging.error(f"An error occurred during export: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    export_to_csv()
