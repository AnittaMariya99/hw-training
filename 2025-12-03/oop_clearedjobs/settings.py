import requests

API_URL = "https://clearedjobs.net/api/v1/jobs?locale=en&"


HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'is-landing': 'jobs',
    'landing-initial-request': 'false',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://clearedjobs.net/jobs?locale=en&page=1&sort=relevance&country=&state=&city=&zip=&latitude=&longitude=&keywords=&city_state_zip=&job_id=',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-csrf-token': 'bh2PNplKOqOMCaJHXmOki1ogSwmpOhzkysboZtPg',
    'x-requested-with': 'XMLHttpRequest',
}
response = requests.get(API_URL,headers=HEADERS)

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "clearedjob_db"
COLLECTION = "clearedjob_products"
