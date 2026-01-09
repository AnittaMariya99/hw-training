import logging

""" Logging Configuration """
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


""" Project Details """
PROJECT_NAME = "firstweber"
BASE_URL = "https://www.firstweber.com"
API_URL = f"{BASE_URL}/CMS/CmsRoster/RosterSearchResults"


""" MongoDB Configuration (PyMongo) """
# MONGO_HOST = "localhost"
# MONGO_PORT = 27017
MONGO_DB = "firstweber"
MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@167.172.244.21:27017/?authSource=admin"

MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"


""" Pagination """
PAGE_SIZE = 10



""" HTTP Headers"""

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "referer": "https://www.firstweber.com/roster/Agents",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "cookie": "subsiteID=333277; subsiteDirectory=; culture=en; ASP.NET_SessionId=ovq2e5tskmx5sqq0g5dfoocp; currencyAbbr=USD; currencyCulture=en-US; rnSessionID=734277756116199566; cf_clearance=YOUR_CF_CLEARANCE_HERE"
}


""" CSV Export (for later use) """

FILE_NAME = "firstweber_agents.csv"

FILE_HEADERS = [
    "profile_url",
    "first_name",
    "middle_name",
    "last_name",
    "title",
    "description",
    "address",
    "street_address",
    "city",
    "state",
    "zip_code",
    "country",
    "languages",
    "website",
    "social_links",
    "image_url",
    "agent_phone_numbers",
]












