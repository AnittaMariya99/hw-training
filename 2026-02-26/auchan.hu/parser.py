import logging
import re
import json
from datetime import datetime

from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient
import html

from settings import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION_PRODUCTS,
    MONGO_COLLECTION_DATA,
)
from items import ProductItem

# reuse a single HTTP session
session = requests.Session()


class ProductParser:
    """Simple parser for auchan.hu product pages.

    The class keeps a connection to MongoDB, fetches URLs from the
    products collection and stores parsed details in the data collection.
    """

    def __init__(self):
        logging.info("Connecting to MongoDB ...")
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        self.total_saved = 0
        logging.info("MongoDB connected.")

        # enforce uniqueness on the url field so replace_one works
        self.mongo[MONGO_COLLECTION_DATA].create_index("pdp_url", unique=True)
        logging.info("Index on 'pdp_url' field created successfully.")

        # token used by the site api
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI4cG1XclQzWmxWMUFJbXdiMUhWYWE5T1BWSzkzcjhIcyIsImp0aSI6IjU0NDQ4N2RlOTM3N2FmODhjYTNiZTAzOTRiYmMwNDBjZmZiYzE0YTllZjA4YTI0ZTAyNDA3MTMwZjE5Y2M1ZjVhNTUxODRlNjMyOWQ3OGQyIiwiaWF0IjoxNzcyMzk4NDcxLjE1MDExMiwibmJmIjoxNzcyMzk4NDcxLjE1MDExNSwiZXhwIjoxNzcyNDg0ODcxLjEyMzYyNSwic3ViIjoiYW5vbl82OWUyMjlmMS1kODZlLTQ3MDAtYTVlNC0yMjFmZDk3ZDFlYzQiLCJzY29wZXMiOltdfQ.SuHMpJraccCj8gIvdvJHLr7RbnWTVFpzQOrHCdocSI5Qu8bNopNV47ULpgilMVuP9j4pkucpL4C6nEeBkGNGmUP5MpZPdYOhZe3o_8QDaVKpmIt8o_gKlw04ncl7j2qBF_IqB_ZO0wOxBT96Rsf7TEIE1BzPjG3PgLSJmNwAWYHyqnwAMK0uj2GZs4LOoTD6TzZPVWiafVSEli_AFOZ_-YV0XiZmltRq1apKWHgsqlUWQo0zFQcD3K5m7NG0ZAUINDax9X3Ke93QpZQNoLN5lKJRgBIozfmLAJu-ZwN4giWqziAsjzzFFu898A-wxhbDicl6ITfs3hLT4c6e6zprIw"

    def start(self):
        """Iterate over every product URL stored in MongoDB."""
        products = list(
            self.mongo[MONGO_COLLECTION_PRODUCTS].find({}, {"_id": 0, "url": 1})
        )
        logging.info(f"Found {len(products)} product URLs to parse.")

        for entry in products:
            url = entry.get("url")
            if not url:
                continue
            logging.info(f"Parsing: {url}")
            try:
                self.parse_item(url)
            except Exception as exc:
                logging.exception(f"Failed to parse {url}: {exc}")

        logging.info(f"Done – {self.total_saved} products saved to MongoDB.")

    def parse_item(self, url: str):
        """Download and parse a single product page and save result.

        The method performs both HTML scraping and secondary API requests.  It
        constructs an ``item`` dictionary, validates it with :class:`ProductItem` and
        then upserts it into the database.
        """

        sku_match = re.search(r"\.p-(\d+)", url)
        if not sku_match:
            logging.warning(f"cannot extract SKU from {url}")
            return
        sku = sku_match.group(1)

        headers = {
            "accept": "application/json",
            "accept-language": "hu",
            "authorization": f"Bearer {self.token}",
            "referer": url,
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        resp = session.get(url, headers=headers)
        if resp.status_code != 200:
            logging.warning(f"Skipping {url}, status {resp.status_code}")
            return

        sel = Selector(resp.text)
        selling_price = (
            sel.xpath("//span[@class='FBX6R-Sn']/text()").get("")
            .replace("Ft", "")
            .strip()
        )
        was_price = re.sub(
            r"[^0-9]",
            "",
            sel.xpath("//div[@class='YYvv13AT']/del/text()").get(""),
        )

        price_per_unit = sel.xpath("//div[@class='uAfhBdJO']/text()").get() or ''
        price_per_unit = price_per_unit.replace('(', '').replace(')', '')
    
        ingredients = "\n".join(sel.xpath("//div[@class='e6xkGFTB']//p/text()").getall())

        api_url = "https://auchan.hu/api/v2/cache/products"
        params = {
            "auchanCodes[]": sku,
            "page": 1,
            "itemsPerPage": 16,
            "cacheSegmentationCode": "DS",
            "hl": "hu",
        }
        api_resp = session.get(api_url, headers=headers, params=params)
        if api_resp.status_code != 200:
            logging.warning(f"API call failed for {url}: {api_resp.status_code}")
            return

        data = api_resp.json()
        if not data.get("results"):
            logging.warning(f"no results returned for {url}")
            return

        product_data = data["results"][0]
        variant = product_data.get("selectedVariant", {})
        product_id = product_data.get("id")
        variant_id = variant.get("id")
        
        review_data = product_data.get('reviewSum', {})
        review = review_data.get('sumCount', 0)
        rating = review_data.get('average', 0)
        logging.info(f"review: {review}, rating: {rating}")

        country_of_origin = ""
        distributor_address = ""
        details = {}
        for d_type in [
            "ingredients",
            "nutrition",
            "allergensDetailed",
            "description",
            "parameterList",
        ]:
            detail_url = (
                f"https://auchan.hu/api/v2/cache/products/{product_id}/"
                f"variants/{variant_id}/details/{d_type}?hl=hu"
            )
            d_resp = session.get(detail_url, headers=headers)
            if d_resp.status_code != 200:
                continue
            d_json = d_resp.json()

            if d_type == "nutrition" and "nutritions" in d_json:
                details[d_type] = d_json["nutritions"]
            elif d_type == "allergensDetailed":
                details[d_type] = "\n".join(
                    [a.get("name", "") for a in d_json.get("allergensDetailed", [])]
                )
            elif d_type == "parameterList":
                feats = []
                for param in d_json.get("parameters", []):
                    if param.get("id") == "place-of-origin":
                        country_of_origin = param.get("value", "")
                    if param.get("id") == "vendor-name":
                        distributor_address = param.get("value", "")
                    feats.append(f"{param.get('name')}: {param.get('value')}")
                details[d_type] = "\n".join(feats)
            else:
                details[d_type] = d_json.get("description", "")
        
        html_content = details.get("description", "")
        # Remove HTML tags
        text = re.sub(r"<.*?>", "", html_content)
        # Unescape HTML entities (&nbsp;, &amp;, etc.)
        text = html.unescape(text)
        details["description"] = text
        
        item = {}
        item["unique_id"] = sku
        item["competitor_name"] = "Auchan"
        item["store_name"] = "Auchan Online"
        item["product_unique_key"] = sku + "P"
        item["extraction_date"] = datetime.now().strftime("%Y-%m-%d")
        item["product_name"] = variant.get("name")
        item["brand"] = variant.get("brandName")
        
        item["currency"] = (
                price_info.get("currency", "HUF")
                if (price_info := variant.get("price", {}))
                else "HUF"
            )
        item["breadcrumb"] = "Főoldal > Online áruház > " + " > ".join([c.get("name", "") for c in product_data.get("categories", [])]) + " > " + variant.get("name")
        item["pdp_url"] = url
        item["product_description"] = details.get("description", "")
        item["country_of_origin"] = country_of_origin
        item["distributor_address"] = distributor_address
        item["features"] = details.get("parameterList", "")
        item["ingredients"] = details.get("ingredients", "")
        item["nutritional_information"] = details.get("nutrition", "")
        item["allergens"] = details.get("allergensDetailed", "")
        item["instock"] = "TRUE" if variant.get("cartInfo", {}).get("availability") == "available" else "FALSE"
        
        cats = item["breadcrumb"].split(" > ")
        for idx, cat in enumerate(cats, 1):
            item[f"producthierarchy_level{idx}"] = cat

        item["selling_price"] = selling_price
        item["price_was"] = was_price
        item["price_per_unit"] = price_per_unit
        item["ingredients_raw"] = ingredients
        item["review"] = review
        item["rating"] = rating

        pkg_info = variant.get("packageInfo", {})
        item["grammage_quantity"] = str(pkg_info.get("packageSize"))
        item["grammage_unit"] = pkg_info.get("packageUnit", "")
        item["site_shown_uom"] = f"{item['grammage_quantity']} {item['grammage_unit']}".strip()

        media = variant.get("media", {})
        images = media.get("images", [])
        for i in range(1, 4):
            img_url = images[i-1] if len(images) >= i else ""
            item[f"image_url_{i}"] = img_url
            item[f"file_name_{i}"] = f"{sku}_{i}.PNG" if img_url else ""

        ProductItem(**item)

        self.mongo[MONGO_COLLECTION_DATA].replace_one({"pdp_url": url}, item, upsert=True)
        self.total_saved += 1
        logging.info(f"    Saved: {item.get('product_name')} -> {url}")

    def close(self):
        self.mongo_client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    parser = ProductParser()
    parser.start()
    parser.close()
