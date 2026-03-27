import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "auchan.hu"
CLIENT_NAME = ""
PROJECT_NAME = "auchan_hu"
FREQUENCY = ""
CATEGORY_URL= "https://auchan.hu/api/v2/cache/tree/0?depth=10&cacheSegmentationCode=DS&hl=hu"
BASE_URL = "https://auchan.hu"
BASE_API_URL = "https://auchan.hu/api/v2/cache/products"
CRAWLER_API_URL = "https://auchan.hu/api/v2/cache/products"



# Mongo db and collections
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"
MONGO_DB = "auchan_hu_db"

MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_PRODUCTS = f"{PROJECT_NAME}_products_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
