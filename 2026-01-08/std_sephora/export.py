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
            product_name = item.get("product_name")
            brand = item.get("brand")
            currency = item.get("currency")
            retailer_id = item.get("retailer_id")
            retailer = item.get("retailer")
            grammage_quantity = item.get("grammage_quantity")
            grammage_unit = item.get("grammage_unit")
            original_price = item.get("original_price")
            selling_price = item.get("selling_price")
            promotion_description = item.get("promotion_description")
            pdp_url = item.get("pdp_url")
            image_url = item.get("image_url")
            ingredients = item.get("ingredients")
            if ingredients:
                ingredients = (
                    ingredients
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .replace("<br>", "")
                    .replace("<br/>", "")
                    .replace("<br />", "")
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                )
            directions = item.get("directions")
            disclaimer = item.get("disclaimer")
            description = item.get("description")
            if description:
                description = (
                    description
                    .replace("<p>", "")
                    .replace("</p>", " ")
                    .replace("<br>", " ")
                    .replace("<br/>", " ")
                    .replace("<br />", " ")
                    .strip()
                )
            diet_suitability = item.get("diet_suitability")
            colour = item.get("colour")
            hair_type = item.get("hair_type")
            skin_type = item.get("skin_type")
            skin_tone = item.get("skin_tone")
            
            
            data = [
                url,
                product_name,
                brand,
                currency,
                retailer_id,
                retailer,
                grammage_quantity,
                grammage_unit,
                original_price,
                selling_price,
                promotion_description,
                pdp_url,
                image_url,
                ingredients,
                directions,
                disclaimer,
                description,
                diet_suitability,
                colour,
                hair_type,
                skin_type,
                skin_tone,
              
            ]

            self.writer.writerow(data)

if __name__ == "__main__":
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
