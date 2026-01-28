
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "acehardware"
CLIENT_NAME = ""
PROJECT_NAME = "acehardware"
FREQUENCY = ""
CATEGORY_URL= "https://www.acehardware.com/graphql"
PLP_URL = "https://www.acehardware.com/api/commerce/catalog/storefront/productsearch/search"



FILE_NAME = f"acehardware_data.csv"

# Mongo db and collections
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"
MONGO_DB = "acehardware_db"
# MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@167.172.244.21:27017/?authSource=admin"



MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_PRODUCTS = f"{PROJECT_NAME}_products_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
