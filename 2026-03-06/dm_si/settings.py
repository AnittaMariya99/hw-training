import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "dm.si"
CLIENT_NAME = ""
PROJECT_NAME = "dm.si"
FREQUENCY = ""
CATEGORY_URL= "https://content.services.dmtech.com/rootpage-dm-shop-sl-si?view=navigation&mrclx=false"
CRAWLER_URL="https://product-search.services.dmtech.com/si/search/static"
BASE_URL = "https://www.dm.si"



FILE_NAME = f"dm_si_2026_03_06_sample.csv"

# Mongo db and collections
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"
MONGO_DB = "dm_si_db"



MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_products_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"

CATEGORY_HEADERS = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://www.dm.si',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.dm.si/',
    'sec-ch-ua': '"Chromium";v="145", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}