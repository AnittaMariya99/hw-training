import requests
import json
import re
from datetime import datetime
import logging
from pymongo import MongoClient
from items import ProductItem
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, PARSER_HEADERS, BASE_PRODUCT_URL

session = requests.Session()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Parser:
    """ Product Parser"""

    def __init__(self):
        """Initialize parser, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        logging.info("Connected to MongoDB")

        # try:
        #     self.mongo[MONGO_COLLECTION_DATA].drop_index("url_1")
        #     logging.info("Dropped legacy index 'url_1'")
        # except Exception:
        #     pass

        self.mongo[MONGO_COLLECTION_DATA].create_index("pdp_url", unique=True)
        logging.info("Index on 'pdp_url' field created successfully.")

    def start(self):
        """Start parsing products"""
        products = list(self.mongo[MONGO_COLLECTION_RESPONSE].find().limit(300))
        total = len(products)
        logging.info(f"Parser started – total urls: {total}")

        PRODUCT_VERSION = "1717"

        VARIANT_HEADERS = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.matalanme.com',
            'priority': 'u=1, i',
            'referer': 'https://www.matalanme.com/',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'source': 'matalan_city_centre_deira',
            'store': 'matalan_ae_en',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'website': 'matalan',
        }

        for i, product in enumerate(products):
            url_key = product.get("url_key")
            if not url_key:
                continue

            logging.info(f"Processing {i+1}/{total}: {url_key}")

            # Step 1: Get selected variant indexes (size + color)
            size_value_index  = None
            color_value_index = None

            try:
                variant_query = """
                query GetProductVarientOptions($url_key: String!) {
                  products(filter: {url_key: {eq: $url_key}}) {
                    items {
                      selected_variant_options(url_key: $url_key) {
                        attribute_id
                        value_index
                        label
                        code
                        __typename
                      }
                      __typename
                    }
                    __typename
                  }
                }
                """

                variant_params = {
                    "product_version": "1733",
                    "query": variant_query,
                    "operationName": "GetProductVarientOptions",
                    "variables": json.dumps({"url_key": url_key}),
                }

                variant_response = requests.get(
                    "https://api.bfab.com/graphql",
                    params=variant_params,
                    headers=VARIANT_HEADERS,
                    timeout=30,
                )
                variant_response.raise_for_status()
                variant_data  = variant_response.json()
                variant_items = variant_data.get("data", {}).get("products", {}).get("items", [])

                if variant_items:
                    for option in variant_items[0].get("selected_variant_options", []):
                        if option.get("code") == "size":
                            size_value_index = option.get("value_index")
                            logging.info(f"Size  -> label: {option.get('label')}, value_index: {size_value_index}")
                        elif option.get("code") == "color":
                            color_value_index = option.get("value_index")
                            logging.info(f"Color -> label: {option.get('label')}, value_index: {color_value_index}")
                else:
                    logging.warning(f"No variant options found for: {url_key}")

            except Exception as e:
                logging.error(f"Variant options fetch failed for {url_key}: {e}")

            logging.info(f"Variant options -> size: {size_value_index}, color: {color_value_index}")

            # Step 2: Fetch full product details
            query = """
            query GetProductDetailVariants($url_key: String!) {
            products(filter: {url_key: {eq: $url_key}}) {
                items {
                id
                name
                description {
                    html
                }
                categories {
                    name
                    url_path
                    breadcrumbs {
                    category_name
                    category_url_path
                    }
                }
                ... on ConfigurableProduct {
                    variants {
                    product {
                        id
                        url_key
                        name
                        sku
                        stock_status
                        qty_left_in_stock
                        swatch_image
                        media_gallery {
                        url
                        label
                        }
                        product_custom_attributes
                        price_range {
                        minimum_price {
                            regular_price {
                            value
                            currency
                            }
                            final_price {
                            value
                            currency
                            }
                            discount {
                            amount_off
                            percent_off
                            }
                        }
                        }
                    }
                    attributes {
                        label
                        code
                        value_index
                        uid
                    }
                    }
                }
                }
            }
            }
            """

            payload = {
                "operationName": "GetProductDetailVariants",
                "variables": {"url_key": url_key},
                "query": query,
            }

            try:
                response = requests.post(
                    BASE_PRODUCT_URL,
                    params={"product_version": PRODUCT_VERSION},
                    json=payload,
                    headers=PARSER_HEADERS,
                    timeout=30,
                )
                logging.info(f"Status code: {response.status_code}")
                if response.status_code == 200:
                    self.parse_item(response, url_key, size_value_index, color_value_index)
            except Exception as e:
                logging.error(f"Error processing {url_key}: {e}")

    def parse_item(self, response, url_key, size_value_index=None, color_value_index=None):
        """Parse product data and save to MongoDB."""
        data = response.json()

        if not ("data" in data and data["data"]["products"]["items"]):
            return

        item_main = data["data"]["products"]["items"][0]
        variants  = item_main.get("variants", [])

        # Select the correct variant by matching size + color value indexes
        selected_variant = None
        for variant in variants:
            attr_map    = {a.get("code"): a.get("value_index") for a in variant.get("attributes", [])}
            size_match  = (size_value_index  is None) or (attr_map.get("size")  == size_value_index)
            color_match = (color_value_index is None) or (attr_map.get("color") == color_value_index)
            if size_match and color_match:
                selected_variant = variant
                logging.info(f"Matched variant: {attr_map}")
                break

        if not selected_variant:
            logging.warning(f"No variant matched for {url_key} – falling back to first variant.")
            selected_variant = variants[0] if variants else None

        if not selected_variant:
            logging.warning(f"No variants found for {url_key}, skipping.")
            return

        product = selected_variant.get("product", {})

        # Parse product_custom_attributes
        product_custom_attributes = product.get("product_custom_attributes", [])
        if isinstance(product_custom_attributes, str):
            try:
                product_custom_attributes = json.loads(product_custom_attributes)
            except Exception as e:
                logging.error(f"Error parsing product_custom_attributes JSON: {e}")
                product_custom_attributes = []
        if not isinstance(product_custom_attributes, list):
            product_custom_attributes = []

        # Breadcrumbs
        department_name   = ""
        category_name     = ""
        product_type_name = ""
        for attribute in product_custom_attributes:
            for child in attribute.get("children", []):
                if child.get("label") == "Department":
                    department_name = child.get("value")
                elif child.get("label") == "Category":
                    category_name = child.get("value")
                elif child.get("label") == "Product Type":
                    product_type_name = child.get("value")

        product_name    = product.get("name")
        product_id      = product.get("id")
        breadcrumbs_str = " > ".join(filter(None, ["Home", department_name, category_name, product_type_name, product_name]))

        # Description
        description_html  = item_main.get("description", {}).get("html", "")
        clean_description = re.sub('<[^<]+?>', '', description_html).strip() if description_html else ""

        # Product details / specifications
        product_details = {}
        for attribute in product_custom_attributes:
            if attribute.get("title") == "Specifications":
                for child in attribute.get("children", []):
                    label = child.get("label")
                    value = child.get("value")
                    if label and isinstance(label, str):
                        product_details[label] = value

        # Images
        images = [img.get("url") for img in product.get("media_gallery", [])]
        if not images:
            images = [product.get("swatch_image")]

        # Prices
        price_info    = product.get("price_range", {}).get("minimum_price", {})
        selling_price = price_info.get("final_price", {}).get("value")
        regular_price = price_info.get("regular_price", {}).get("value")
        currency      = price_info.get("final_price", {}).get("currency")

        product_url=f"https://www.matalanme.com/ae_en/{url_key}"
        gender=product_details.get("Gender")
        color=product_details.get("Color")
        size=product_details.get("Size Code")
        quantity=product.get("qty_left_in_stock") or "1"
        extraction_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        # Build item
        item = {}
        item["unique_id"]       = str(product_id)
        item["pdp_url"]         = product_url
        item["product_name"]    = product_name
        item["selling_price"]   = selling_price
        item["regular_price"]   = regular_price
        item["currency"]        = currency
        item["image"]           = images
        item["description"]     = clean_description
        item["gender"]          = gender
        item["color"]           = color
        item["size"]            = size
        item["quantity"]        = quantity
        item["breadcrumbs"]     = breadcrumbs_str
        item["product_details"] = product_details
        item["extraction_date"] = extraction_date

        product_item = ProductItem(**item)
        product_item.validate()
        self.mongo[MONGO_COLLECTION_DATA].update_one(
            {"pdp_url": item["pdp_url"]},
            {"$set": item},
            upsert=True,
        )

    def close(self):
        """Close MongoDB connection."""
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()