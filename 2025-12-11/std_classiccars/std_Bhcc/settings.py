from datetime import datetime
import os
import calendar
import logging
import configparser
import pytz
from dateutil.relativedelta import relativedelta, MO
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "BeverlyHillscarClub"
CLIENT_NAME = ""
PROJECT_NAME = "BeverlyHillscarClub"
FREQUENCY = ""
BASE_URL = "https://www.beverlyhillscarclub.com/isapi_xml.php?module=inventory&sold=Available&future_inventory=!1&pending_sale=!1&pending=!1&limit=60&orderby=make,year&"




FILE_NAME = f"BHCC.csv"
FILE_HEADERS = ["make","model","year","vin","price","mileage","transmission","engine","color","fuel type","body style","description","image urls","url"]

# Mongo db and collections
MONGO_URI = "mongodb://localhost:27017/"
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "BHCC_db"



MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"



HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.beverlyhillscarclub.com/inventory.htm?&orderby=make,year',
    'sec-ch-ua': '"Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    
}
   

HEADERS_2 = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	'accept-language': 'en-US,en;q=0.9',
	'cache-control': 'no-cache',
	'pragma': 'no-cache',
	'priority': 'u=0, i',
	'referer': 'https://www.beverlyhillscarclub.com/inventory.htm?page_no=2:60&orderby=make,year',
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


