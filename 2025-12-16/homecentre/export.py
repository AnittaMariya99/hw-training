import csv
import logging
from time import sleep
from settings import MONGO_COLLECTION_DATA, FILE_NAME, FILE_HEADERS, MONGO_DB, MONGO_URI
from pymongo import MongoClient
from mongoengine import connect
from items import ProductUrlItem, ProductItem, ProductFailedItem

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
            product_id=item.get("product_id")
            product_name=item.get("product_name")
            product_color=item.get("product_color")
            material=item.get("material")
            quantity=item.get("quantity")
            details_string=item.get("details_string")
            specification=item.get("specification")
            price=item.get("price")
            wasprice=item.get("wasprice")
            product_type=item.get("product_type")
            breadcrumb=item.get("breadcrumb")
            stock=item.get("stock")
            image=item.get("image")
            

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
               wasprice,
               product_type,
               breadcrumb,
               stock,
               image
               
            ]

            self.writer.writerow(data)

    


if __name__ == "__main__":
    with open(FILE_NAME, "a", encoding="utf-8") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
        file.close()
