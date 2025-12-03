
import json
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, MONGO_URI, DB_NAME, COLLECTION
from logger import get_logger
logger = get_logger("product_parser")

# -----------------------
# Custom Exception
# -----------------------
class DataMiningError(Exception):
    """Raised for errors during product parsing."""
    pass


# ------------------------------------------------------
# PRODUCT PARSER CLASS
# ------------------------------------------------------
class clearedjobsParser:
    def __init__(self):
        """Initialize DB connection and filenames."""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

        self.raw_file = "product_raw.html"
        self.cleaned_file = "product_cleaned.txt"

    # --------------------------------------------------
    # 1. Fetch HTML with safe exception handling 
    # --------------------------------------------------
    def fetch_html(self, url):
        try:
            
            logger.info(f"Fetching product page ::: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} for {url}"
                )

            # Save raw HTML (Task 2)
            with open(self.raw_file, "w", encoding="utf-8") as file:
                file.write(response.text)

            return response.text

        except requests.RequestException as err:
            raise DataMiningError(f"Connection failed: {err}")
        
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

    # --------------------------------------------------
    # 2. Parse HTML 
    # --------------------------------------------------
    def parse_data(self, html):
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"HTML parsing failed: {err}")

    # --------------------------------------------------
    # 2.5 Parse Job Details (Main logic) 
    # --------------------------------------------------
    def parse_job_details(self, url):
        json_txt = self.fetch_json(url)
        experience = json_txt.get("data", {}).get("experience", None)  
        salary= json_txt.get("data", {}).get("salary", None)
        positionType= json_txt.get("data", {}).get("positionType", None)


        return {
            "experience": experience,
            "salary": salary,
            "position": positionType,
        }
    
    # --------------------------------------------------
    # 3. Extract product details (main logic)
    # --------------------------------------------------
    def parse_company_details(self, url):
        html = self.fetch_html(url)
        sel = self.parse_data(html)
        
        try:
             
            company_social_handles=sel.xpath("//div[@class='socials']/a[contains(@class, 'btn-social-icon')]/@href").getall()
          

            return {
                "company_social_handles": company_social_handles,
            }

        except Exception as err:
            raise DataMiningError(f"Failed to parse product {url}: {err}")

    # --------------------------------------------------
    # 4. Save cleaned data to file 
    # --------------------------------------------------
    def save_to_file(self, cleaned_data):
        with open(self.cleaned_file, "w", encoding="utf-8") as file:
            for key, value in cleaned_data.items():
                file.write(f"{key}: {value}\n")

    # --------------------------------------------------
    # 5. Yield URLs from MongoDB
    # --------------------------------------------------
    def yield_urls_from_mongoDB(self):
        cursor = self.collection.find({"experience": {"$exists": False}})
        for document in cursor:
            
            yield document["_id"], document.get("url"), document.get("company_profile_url")


    # --------------------------------------------------
    # 6. Start product detail scraping (Main)
    # --------------------------------------------------
    def start(self):
        
        logger.info(f"\nStarting Marks & Spencer Product Detail Scraper...\n")


        for doc_id, job_url, company_url in self.yield_urls_from_mongoDB():
            
            try:
                logger.info(f"\nProcessing Job url: {job_url}")
                job_details = self.parse_job_details(job_url)
                logger.info(f"\nProcessing Company url: {company_url}")
                company_details = self.parse_company_details(company_url) if company_url else {}

                full_details = {**job_details, **company_details}

                # Save to cleaned file (only last product)
                self.save_to_file(full_details)

                # Update database
                self.collection.update_one(
                    {"_id": doc_id},
                    {"$set": full_details}
                )

                
                logger.info(f"Updated job: {job_url}\n")


            except DataMiningError as err:
               logger.info(f"Error: {err}")

    # --------------------------------------------------
    # Close DB connection (Destructor)
    # --------------------------------------------------
    def close(self):
        
        logger.info(f"Closing MongoDB connection...")
        self.client.close()

    # --------------------------------------------------
    # parse a single product (for testing)
    # --------------------------------------------------
    def parse_single_product(self, joburl, companyurl):
        try:
            jobdetails = self.parse_job_details(joburl)
            logger.info("Extracted Job Details:")
            for key, value in jobdetails.items():
                logger.info(f"{key}: {value}")
            
            if companyurl:
                companydetails = self.parse_company_details(companyurl)
                logger.info("Extracted Company Details:")
                for key, value in companydetails.items():
                    logger.info(f"{key}: {value}")

        except DataMiningError as err:
            logger.error(f"{err}")