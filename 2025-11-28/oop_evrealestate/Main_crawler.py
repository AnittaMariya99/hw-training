
import requests
from parsel import Selector
from pymongo import MongoClient
from logger import get_logger
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION
from exceptions import DataMiningError

logger = get_logger("main_crawler")


# ---------------------------------------------------------
# Evrealestatecrawler
# ---------------------------------------------------------
class Evrealestatecrawler:
    
    def __init__(self):
        """Initialize crawler, DB, logs."""
        logger.info("Initializing ..............................................")

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

      
    # ---------------------------------------------------------
    # FETCH JSON
    # ---------------------------------------------------------
    def fetch_json(self, url):
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} from {url}"
                )

            return response.json()

        except Exception as err:
            logger.error(f"Connection error: {err}")



    # ---------------------------------------------------------
    # PARSE ITEMS – EV REAL ESTATE ADVISORS LISTINGS
    # ---------------------------------------------------------
    def parse_item(self):
        """Extract advisor profile links & details from EVRealEstate with HTML pagination check."""

        BASE_URL = "https://www.evrealestate.com/en/our-advisors/"
        API_URL = "https://eva-personnel-service.evipscloud.com/advisors?sortKey=firstname&sortDir=asc"

        logger.info("Starting EVRealEstate Advisor Crawler...")

        all_profile_links = []
        current_page = 1

        while True: 

            api_url = f"{API_URL}&offset={(current_page - 1) * 18}&limit=18"
            logger.info(f"Fetching API page: {api_url}")

            # -------- Fetch JSON --------
            json_text = self.fetch_json(api_url)
            # print(json_text)

            records = json_text.get("records", [])
            logger.info(f"Found {len(records)} advisor records on page {current_page}")

            if not records:
                logger.info("No more JSON records. Ending crawl.")
                break

            # -----------------------------------------------------
            # Extract each advisor
            # -----------------------------------------------------
            for advisor in records:

                # print(rec)  # Debug: print the entire record
                type = advisor.get("type", "")
                if type != "advisor":
                    logger.info(f"Skipping non-advisor record of type: {type}")
                    continue

                
              
                id = advisor.get("advisorId", "")
                accounts = advisor.get("accounts", [])
                account = accounts[0] if accounts else {}
                shops = account.get("associatedShops", [])
                shop = shops[0] if shops else {}

                contact = account.get("contact", {})
                social_profiles = account.get("socialProfiles", [])
                nameobject = advisor.get("name", {})
                first_name = nameobject.get("firstName", "")
                last_name = nameobject.get("lastName", "")
                
                name = first_name + " " + last_name
                # Create slug
                slug = (
                    name.strip().lower()
                    .replace(" ", "-")
                    .strip()
                )

                profile_url = f"{BASE_URL}{slug}/"

                all_profile_links.append(profile_url)

                
                extracted_record = {
                    "first_name": advisor.get("name", {}).get("firstName", ""),
                    "middle_name": advisor.get("name", {}).get("middleName", ""),
                    "last_name": advisor.get("name", {}).get("lastName", ""),

                    "address": shop.get("address", "").strip(),
                    "city": shop.get("city", ""),
                    "state": shop.get("state", ""),
                    "country": shop.get("country", ""),
                    "zipcode": shop.get("postalCode", ""),

                    "email": contact.get("email", ""),
                    "website": contact.get("website", ""),

                    "office_name": shop.get("name", ""),
                    "title": account.get("title", ""),
                    "languages": account.get("languages", []),

                    "image_url": advisor.get("profilePicture", ""),

                    "office_phone_numbers": shop.get("phoneNumbers", []), 
                    "agent_phone_numbers": [p.get("phone") for p in account.get("phoneNumbers", [])],

                    "social": [
                        {"type": s.get("type"), "url": s.get("url")}
                        for s in social_profiles
                        if isinstance(s, dict) 
                    ],

                    "profile_url": profile_url,
                    
                }

                self.save_data_to_mongo(extracted_record)

            # Check if there are more pages
            total_records = json_text.get("totalRecords", 0)
            if current_page * 18 >= total_records:
                logger.info("Reached the last page of JSON records. Ending crawl.")
                break
            # Otherwise move to next page
            current_page += 1
            logger.info(f"Moving to next page: {current_page}")
            

        return all_profile_links

    



    # ---------------------------------------------------------
    # SAVE CLEANED URLS TO MONGO
    # ---------------------------------------------------------
    def save_data_to_mongo(self, extracted_record):
        self.collection.update_one(
            {"profile_url": extracted_record["profile_url"]},
            {"$set": extracted_record},
            upsert=True
        )


    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------
    def start(self):
        
        product_links = self.parse_item()

        logger.info(f"\nTotal extracted product URLs: {len(product_links)}")


    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        logger.info(f"Closing DB connection...")
        self.client.close()
