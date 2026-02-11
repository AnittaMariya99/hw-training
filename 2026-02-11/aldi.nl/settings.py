import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
HEADERS ={
    
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
# basic details
PROJECT = "aldi.nl"
CLIENT_NAME = ""
PROJECT_NAME = "aldi.nl"
FREQUENCY = ""
CATEGORY_URL= "https://www.aldi.nl/producten.html"
BASE_URL = "https://www.aldi.nl"
BASE_PRODUCT_URL = "https://www.aldi.nl/product/"


FILE_NAME = f"aldi_nl_2026_02_10_sample.csv"

# Mongo db and collections
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"
MONGO_DB = "aldi_nl_db"



MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_PRODUCTS = f"{PROJECT_NAME}_products_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
