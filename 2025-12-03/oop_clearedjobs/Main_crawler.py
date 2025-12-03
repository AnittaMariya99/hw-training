import json
import requests
from parsel import Selector
from pymongo import MongoClient
from logger import get_logger
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION,API_URL
from exceptions import DataMiningError

logger = get_logger("main_crawler")


# ---------------------------------------------------------
#  CRAWLER CLASS
# ---------------------------------------------------------
class clearedjobscrawler:
    def __init__(self):
        """Initialize crawler, DB, logs."""
        logger.info("Initializing ...........")

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
    # PARSE HTML
    # ---------------------------------------------------------
    def parse_data(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"Parsing failed: {err}")


    # ---------------------------------------------------------
    # PARSE ITEMS – clearedjobs LISTINGS
    # ---------------------------------------------------------
    def parse_item(self):
        """Extract property listing links from Bayut.bh with pagination."""

        logger.info("Starting clearedjobs Crawler...")
        all_profile_links = []
        page = 1

        while True: 

            api_url = f"{API_URL}page={page}&sort=relevance&country=&state=&city=&zip=&latitude=&longitude=&keywords=&city_state_zip=&job_id="
            logger.info(f"Fetching API page: {api_url}")

            # -------- Fetch JSON --------
            json_text = self.fetch_json(api_url)
            # print(json_text)

            records = json_text.get("data", [])

            logger.info(f"Found {len(records)} job records on page {page}")

            if not records:
                logger.info("No more JSON records. Ending crawl.")
                break

            # -----------------------------------------------------
            # Extract each job_urls
            # -----------------------------------------------------
            for job in records:
                job_id = job.get("id", "")
                modified_tm = job.get("modified_time", "")
                job_title = job.get("title", "")
                loction = job.get("location", "")
                location_type= job.get("coordinates", {})
                company = job.get("company", {})
                company_name= company.get("name","")
                company_profile_url= company.get("url","")
                company_logo= company.get("logo","")
                url = f"https://clearedjobs.net/api/v1/jobs/{job_id}?locale=en&mt={modified_tm}"

            # Extract custom fields       
                security_clearance = ""
                posted = ""

                for item in job.get("customBlockList", []):
                    if item.get("label") == "Security Clearance":
                        security_clearance = item.get("value", "")
                    
                    if item.get("label") == "Posted":
                        posted= item.get("value", "")
                    
                extracted_record = {
                    "url": url,
                    "job_id": job_id,
                    "job_title": job_title,
                    "loction": loction,
                    "location_type": location_type,
                    "company_name": company_name,
                    "company_profile_url": company_profile_url,
                    "company_logo": company_logo,
                    "security_clearance": security_clearance,
                    "posted": posted    
                }

                self.save_data_to_mongo(extracted_record)


            # Check if there are more pages
            total_page = json_text.get("meta", {}).get("last_page", 0)
            if page >= total_page:
                logger.info("Reached the last page. Ending crawl.")
                break
            page += 1
            logger.info(f"Moving to next page: {page}")

        return all_profile_links

    # ---------------------------------------------------------
    # SAVE CLEANED URLS TO MONGO
    # ---------------------------------------------------------
    def save_data_to_mongo(self, extracted_record):
        self.collection.update_one(
            {"job_id": extracted_record["job_id"]},
            {"$set": extracted_record},
            upsert=True
            )
        



    # ---------------------------------------------------------
    # SAVE CLEANED URLS TO MONGO
    # ---------------------------------------------------------
    def save_urls_to_mongo(self, url_list):
        for url in url_list:
            self.collection.update_one(
                {"url": url},
                {"$set": {"url": url}},
                upsert=True
            )


    # ---------------------------------------------------------
    # START CRAWLER
    # ---------------------------------------------------------
    def start(self):
        self.parse_item()

        logger.info(f"All data saved to file successfully.")


    # ---------------------------------------------------------
    # CLOSE CONNECTIONS
    # ---------------------------------------------------------
    def close(self):
        logger.info(f"Closing DB connection...")
        self.client.close()