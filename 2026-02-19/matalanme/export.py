import csv
from pymongo import MongoClient
import logging
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Exporter:
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        self.collection = self.mongo[MONGO_COLLECTION_DATA]
        logging.info("Connected to MongoDB for export")

    def clean_text(self, text):
        if text:
            return str(text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
        return ""

    def format_price(self, price):
        try:
            if price is not None and price != "":
                return "{:.2f}".format(float(price))
        except ValueError:
            pass
        return ""

    def start(self):            
        products = list(self.collection.find().limit(200))
        if not products:
            logging.info("No products found to export.")
            return

        logging.info(f"Found {len(products)} products. Starting export...")
        
        fieldnames = [
            'unique_id',
            'url',
            'product_name',
            'selling_price',
            'image',
            'description',
            'currency',
            'gender',
            'breadcrumbs',
            'extraction_date',
            'product_details',
            'regular_price',
            'quantity',
            'color',
            'size',
        ]

        with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore', delimiter='|')
            writer.writeheader()

            for item in products:
                # Direct assignment without pricing logic
                selling_price = item.get("selling_price")
                regular_price = item.get("regular_price")
                price_was = item.get("price_was")
                promotion_price = item.get("promotion_price")

                # Prepare row
                row = {
                    'unique_id': self.clean_text(item.get('unique_id')),
                    'product_name': self.clean_text(item.get('product_name')),
                    'name': self.clean_text(item.get('name')),
                    'breadcrumbs': self.clean_text(item.get('breadcrumbs')),
                    'url': self.clean_text(item.get('url')),
                    'selling_price': self.format_price(selling_price),
                    'regular_price': self.format_price(regular_price),
                    'price_was': self.format_price(price_was),
                    'promotion_price': self.format_price(promotion_price),
                    'currency': self.clean_text(item.get('currency')),
                    'gender': self.clean_text(item.get('gender')),
                    'color': self.clean_text(item.get('color')),
                    'size': self.clean_text(item.get('size')),
                    'quantity': self.clean_text(item.get('quantity')),
                    'description': self.clean_text(item.get('description')),
                    'extraction_date': self.clean_text(item.get('extraction_date')),
                    'product_details': self.clean_text(item.get('product_details')),
                }
                
                # Image handling
                images = item.get('image', [])
                if isinstance(images, list):
                    # Filter out potential None values before joining
                    valid_images = [str(img) for img in images if img]
                    row['image'] = " | ".join(valid_images)
                else:
                    row['image'] = self.clean_text(images)

                writer.writerow(row)
        
        logging.info(f"Export completed. File saved as {FILE_NAME}")

if __name__ == "__main__":
    exporter = Exporter()
    exporter.start()
