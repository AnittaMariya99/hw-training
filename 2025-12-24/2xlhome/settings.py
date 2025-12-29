from datetime import datetime
import calendar
import logging
import pytz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "2xlhome"
CLIENT_NAME = "2xlhome"
PROJECT_NAME = "2xlhome"
FREQUENCY = ""
BASE_URL = "https://www.2xlhome.com/ae-en"

datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
# iteration = datetime_obj.strftime("%Y_%m_%d")
iteration = "2025_12_23"
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"2xlhome_{iteration}.csv"

# Mongo db and collections
MONGO_DB = f"2xlhome_ae_{iteration}"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"






HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://2xlhome.com/ae-en/',
    'sec-ch-ua': '"Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}





# Mongo db and collections
MONGO_URI = "mongodb://localhost:27017/"
MONGO_HOST = "localhost"
MONGO_PORT = 27017



FILE_HEADERS = [
    "url",
    "product_id",
    "product_name",
    "product_color",
    "material",
    "quantity",
    "details_string",
    "specification",
    "price",
    "was_price",
    "product_type",
    "breadcrumb",
    "stock",
    "image_url"
]
