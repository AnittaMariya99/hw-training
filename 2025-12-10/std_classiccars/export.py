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

        for item in self.mongo[MONGO_DB][MONGO_COLLECTION_DATA].find():
            logging.info(item)  
            
            profile_url = item.get("url")
            image_url=item.get("image_url")
            title=item.get("title")
            price=item.get("price")
            listing_id=item.get("listing_id")
            location=item.get("location")
            make=item.get("make")
            year=item.get("year")
            model=item.get("model")
            exterior_color=item.get("exterior_color")
            interior_color=item.get("interior_color")
            mileage=item.get("mileage")
            transmission=item.get("transmission")
            engine=item.get("engine")
            
            

            data = [
                profile_url,
                image_url,
                title,
                price,
                listing_id,
                location,
                make,
                year,
                model,
                exterior_color,
                interior_color,
                mileage,
                transmission,
                engine

            ]

            self.writer.writerow(data)


if __name__ == "__main__":
    with open(FILE_NAME, "a", encoding="utf-8") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
        file.close()
