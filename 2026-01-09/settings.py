from datetime import datetime
import calendar
import logging
# import pytz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "LuluHypermarket"
CLIENT_NAME = "LuluHypermarket"
PROJECT_NAME = "LuluHypermarket"
FREQUENCY = "daily"
BASE_URL = "https://gcc.luluhypermarket.com/en-ae/"

# datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
# # iteration = datetime_obj.strftime("%Y_%m_%d")
# iteration = "2025_12_19"
# YEAR = datetime_obj.strftime("%Y")
# MONTH = datetime_obj.strftime("%m")
# DAY = datetime_obj.strftime("%d")
# MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
# WEEK = (int(DAY) - 1) // 7 + 1

# FILE_NAME = f"LuluHypermarket_{iteration}.csv"

# Mongo db and collections
# MONGO_URI = "mongodb://localhost:27017/"
# MONGO_HOST = "localhost"
MONGO_PORT = 27017

MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@167.172.244.21:27017/?authSource=admin"

# Mongo db and collections
MONGO_DB = f"LuluHypermarket_ae_sample"
MONGO_COLLECTION_URL = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_response"

API_URL = "https://gcc.luluhypermarket.com/api/client/menus/generate/?depth_height=4"


 # Fields as requested
FILE_HEADERS = [
    "url", "product_id", "product_name", "product_color", "material",
    "quantity", "details_string", "specification", "price", "wasprice",
    "product_type", "breadcrumb", "stock", "image"
]


HEADERS =  {
    'accept': '*/*',
    'accept-language': 'en-ae',
    'baggage': 'sentry-environment=production,sentry-public_key=b322140811e243ba6102adcb735911c7,sentry-trace_id=5e2395dae4754ec7a9f43f9a8f11cbc3,sentry-sampled=false,sentry-sample_rand=0.8968390954700278,sentry-sample_rate=0',
    'priority': 'u=1, i',
    'referer': 'https://gcc.luluhypermarket.com/en-ae/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': '5e2395dae4754ec7a9f43f9a8f11cbc3-a2ae5a7ae37a576c-0',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-csrftoken': 'eOX3ybnBbSOltqhgkjRCxYnxCUXwetpi3nf2VM1ud53LyXnKWvO63h66RqJIoGC4',
    'x-currency': 'aed',

}



