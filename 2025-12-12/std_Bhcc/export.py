import csv
import logging
from time import sleep
from settings import MONGO_COLLECTION_DATA,FILE_NAME, FILE_HEADERS, MONGO_DB, MONGO_HOST, MONGO_PORT
from mongoengine import connect

class Export:       
    """Post-Processing"""

    def __init__(self, writer):
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, alias="default", port=MONGO_PORT)
        self.writer = writer

    def start(self):
        """Export as CSV file"""

        self.writer.writerow(FILE_HEADERS)
        logging.info(FILE_HEADERS)

        pipeline = [
            {
                "$addFields": {
                    "year_int": { "$convert": { "input": "$year", "to": "double", "onError": 0, "onNull": 0 } }
                }
            },
            {
                "$match": {
                    "year_int": { "$gt": 1960 }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "year_int": 0
                }
            }
        ]

        for item in self.mongo[MONGO_DB][MONGO_COLLECTION_DATA].aggregate(pipeline):
            logging.info(item)  
            
            
            
            profile_url = item.get("url")
            image_urls=item.get("image_urls")
            price=item.get("price")
            make=item.get("make")
            year=item.get("year")   
            vin=item.get("vin")
            model=item.get("model")
            color=item.get("color")
            description=item.get("description")
            
            # CLEAN DATA
            

            
            price = self.clean_price(price)
            mileage=""
            transmission=""
            engine=""
            fuel_type=""
            body_style=""   

# ["make","model","year","vin","price","mileage","transmission","engine","color","fuel type","body style","description","image URLs","url"]
            data = [
                make,
                model,
                year,
                vin,
                price,
                mileage,
                transmission,
                engine,
                color,
                fuel_type,
                body_style,
                description,
                image_urls,
                profile_url
            ]

            self.writer.writerow(data)

    def clean_price(self,price_str):
            # print(f"Cleaning price: {price_str}")
            if not price_str:
                return None

            # Remove $, spaces, and "(OBO)"
            cleaned = price_str.replace("$", "")
            cleaned = cleaned.replace(" (OBO)", "")
            cleaned = cleaned.replace(" (obo)", "")
            cleaned = cleaned.strip()
            # print(f"Cleaned price: {cleaned}")

            return cleaned


if __name__ == "__main__":
    with open(FILE_NAME, "a", encoding="utf-8") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
        file.close()
