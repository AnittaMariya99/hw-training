import logging
import requests
from parsel import Selector
from mongoengine import connect, DynamicDocument, StringField

from settings import (HEADERS, MONGO_DB, MONGO_HOST, MONGO_PORT, MONGO_COLLECTION_DATA,)
from items import ProductUrlItem, ProductFailedItem, ProductDataItem


class Parser:
    """2XL Home product detail parser using MongoEngine"""

    def __init__(self):
        # ---------- MongoEngine Connection ----------
        self.mongo = connect(db=MONGO_DB,host=MONGO_HOST,port=MONGO_PORT, alias="default")

    def start(self):
        """Iterate over product URLs and parse details"""

        for item in ProductUrlItem.objects():
            url = item.url
            logging.info(f"Parsing: {url}")

            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                logging.error(f"FAILED: {url} (fetch_failed)")
                ProductFailedItem(url=url, reason="fetch_failed").save()
                continue

            self.parse_item(item, response)

        logging.info("Parsing completed")    

    def parse_item(self, item, response):
        """item parsing"""

        sel = Selector(text=response.text)
        
        # Updated XPaths
        PRODUCT_TYPE_XPATH = "//div[@class='category-name']/span/a/text()"
        SPECIFICATION_XPATH = "//div[@class='collapsibleContent']//div[@class='value'][strong]"
        COLOR_XPATH = "//strong[normalize-space()='Color:']/parent::div/text()"
        MATERIAL_XPATH = "//strong[normalize-space()='Material:']/parent::div/text()"
        DETAILS_STRING_XPATH = "//div[@class='value']/p[normalize-space()]/text()"

        # ---------------- EXTRACT ---------------- #
        product_type = sel.xpath(PRODUCT_TYPE_XPATH).get()
        
        # Details/Description
        details_list = sel.xpath(DETAILS_STRING_XPATH).getall()
        details_string = "\n\n ".join([d.strip() for d in details_list if d.strip()])

        color = sel.xpath(COLOR_XPATH).get()
        material = sel.xpath(MATERIAL_XPATH).get()

        specs_nodes = sel.xpath(SPECIFICATION_XPATH)
        specifications = {}
        for spec in specs_nodes:
            key = spec.xpath('./strong/text()').get()
            # Extract text value (removing key)
            full_text = spec.xpath('string(.)').get()
            if key and full_text:
                value = full_text.replace(key, "").strip()
                key_clean = key.strip().strip(":")
                specifications[key_clean] = value

        # ---------------- DOCUMENT ---------------- #
        data = {}
        data["url"] = item.url
        data["product_id"] = item.product_id
        data["product_name"] = item.product_name
        data["price"] = item.price
        data["was_price"] = item.was_price
        data["image"] = item.image
        data["product_color"] = color.strip() if color else ""
        data["material"] = material.strip() if material else ""
        data["details_string"] = details_string
        data["specification"] = specifications
        data["product_type"] = product_type.strip() if product_type else ""
        data["quantity"] = ""
        data["breadcrumb"] = ""
        data["stock"] = ""

        ProductDataItem(**data).save()


    def close(self):
        """Close MongoDB connection"""
        self.mongo.close()
        logging.info("MongoDB connection closed")


if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()
