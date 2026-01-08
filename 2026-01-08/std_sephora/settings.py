from datetime import datetime
import calendar
import logging
import pytz
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "Sephora"
CLIENT_NAME = "Sephora"
PROJECT_NAME = "Sephora"
FREQUENCY = "daily"
BASE_URL = "https://www.sephora.sg/"

datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
# iteration = datetime_obj.strftime("%Y_%m_%d")
iteration = "2025_12_19"
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"Sephora_{iteration}.csv"

# Mongo db and collections
MONGO_URI = "mongodb://localhost:27017/"
MONGO_HOST = "localhost"
MONGO_PORT = 27017

# Mongo db and collections
MONGO_DB = f"Sephora_sg_{iteration}"
MONGO_COLLECTION_URL = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"





 # Fields as requested
FILE_HEADERS = ["url", "product_name", "brand", "currency", "retailer_id", "retailer", "grammage_quantity", "grammage_unit", "original_price", "selling_price", "promotion_description", "pdp_url", "image_url", "ingredients", "directions", "disclaimer", "description", "diet_suitability", "colour", "hair_type", "skin_type", "skin_tone"]


HEADERS = {



    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-SG',
    'priority': 'u=1, i',
    'referer': 'https://www.sephora.sg/products/fenty-beauty-match-stix-matte-contour-skinstick/v/amber',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-app-platform': 'web_desktop',
    'x-app-version': '1.0.0',
    'x-csrf-token': 'a+BWA3VkM8ubE/9ApDMqi1vgWJcEpAokXtmmSdihfz1hE6i5URIOqOljqx4Pv1WzAxssiwsDS+h0ZrmHpJThxA==',
    'x-platform': 'web',
    'x-requested-with': 'XMLHttpRequest',
    'x-site-country': 'SG',
}

# API configuration
BASE_API = "https://www.sephora.sg/api/v2.6/products/"
INCLUDE_PARAMS = "variants.filter_values,variants.ingredient_preference,featured_ad.virtual_bundle.bundle_elements,product_articles,filter_types"

# MongoDB client initialization

# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB]
# collection_categories = db[MONGO_COLLECTION_CATEGORY]
# collection_products = db[MONGO_COLLECTION_DATA]
# collection_urls = db[MONGO_COLLECTION_URL]
# collection_failed = db[MONGO_COLLECTION_URL_FAILED]