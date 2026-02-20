#__________________________________________________________category________________________________________________
from curl_cffi import requests         
from parsel import Selector


BASE_URL = "https://shop.billa.at"


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    }

url = f"{BASE_URL}/kategorie"
print(f"[STEP 1] Fetching top-level categories from {url} ...")

response = requests.get(url, headers=HEADERS,impersonate="chrome")
print(response.status_code)

sel = Selector(response.text)

categories = []
for category in sel.css("div.category-list__item"):
    name = category.css("a.category-list__link::text").get().strip()
    link = category.css("a.category-list__link::attr(href)").get()
    categories.append({"name": name, "link": link})
    print(f"  - Found category: {name} ({link})")


#__________________________________________________________crawler_________________________________________________

from curl_cffi import requests
from parsel import Selector
import csv
import json
import time

BASE_URL = "https://shop.billa.at"

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}

"""GET a URL with curl_cffi Chrome impersonation. Returns Response or None."""

response = requests.get( url,headers=HEADERS,impersonate="chrome",)
print(f"  [{response.status_code}] {url}")
if response.status_code == 200:
    sel = Selector(response.text)
    #__________________________________________________________parser_________________________________________________

from curl_cffi import requests
from parsel import Selector
import csv
import json
import re
from datetime import date

BASE_URL   = "https://shop.billa.at"
COMPETITOR = "BILLA"
STORE_NAME = "BILLA Online Shop"
CURRENCY   = "EUR"
TODAY      = date.today().isoformat()

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}










