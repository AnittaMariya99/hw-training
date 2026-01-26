
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





FILE_NAME = f"acehardware_data.csv"
# FILE_HEADERS = ["make","model","year","vin","price","mileage","transmission","engine","color","fuel type","body style","description","image urls","url"]

# Mongo db and collections
# MONGO_URI = "mongodb://localhost:27017/"
# MONGO_HOST = "localhost"
# MONGO_PORT = 27017
MONGO_DB = "classiccars_db"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@167.172.244.21:27017/?authSource=admin"



MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"



