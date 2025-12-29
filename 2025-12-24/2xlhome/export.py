import csv
import logging
from time import sleep
from settings import MONGO_COLLECTION_DATA, FILE_NAME, FILE_HEADERS, MONGO_DB, MONGO_URI
from pymongo import MongoClient
from mongoengine import connect
from items import ProductUrlItem, ProductDataItem, ProductFailedItem

class Export:       
    """Post-Processing"""



    def __init__(self, writer):
        self.mongo = connect(db=MONGO_DB, host="localhost", alias="default")
        logging.info(MONGO_URI)
        logging.info(MONGO_DB)
        logging.info(MONGO_COLLECTION_DATA)
        self.client = MongoClient(MONGO_URI)
        self.collection_data = self.client[MONGO_DB][MONGO_COLLECTION_DATA]
        self.writer = writer

        

    def start(self):
        """Export as CSV file"""

        self.writer.writerow(FILE_HEADERS)
        logging.info(FILE_HEADERS)

        for item in self.collection_data.find():
            
            url = item.get("url")
            product_id = item.get("product_id")
            product_name = item.get("product_name")
            product_color = item.get("product_color")
            material = item.get("material")
            quantity = item.get("quantity")
            details_string = item.get("details_string")
            specification = item.get("specification")
            
            price = item.get("price", "")
            if price:
                price = price.replace("AED", "").replace(",", "").strip()

            was_price = item.get("was_price", "")
            if was_price:
                was_price = was_price.replace("AED", "").replace(",", "").strip()

            product_type = item.get("product_type")
            breadcrumb = item.get("breadcrumb")
            stock = item.get("stock")
            
            image_list = item.get("image", [])
            image_url = "|".join(image_list) if isinstance(image_list, list) else str(image_list)

            data = [
               url,
               product_id,
               product_name,
               product_color,
               material,
               quantity,
               details_string,
               specification,
               price,
               was_price,
               product_type,
               breadcrumb,
               stock,
               image_url
            ]

            self.writer.writerow(data)

if __name__ == "__main__":
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
