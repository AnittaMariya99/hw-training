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
for a in sel.xpath('//a[@class="ws-category-tree-navigation-button ws-btn ws-btn--secondary-link ws-btn--large"]'):
    href = a.xpath("./@href").get("")
    if not href.startswith("/kategorie/"):
        continue

#__________________________________________________________crawler_________________________________________________

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

"""GET a URL with curl_cffi Chrome impersonation. Returns Response or None."""

response = requests.get( url,headers=HEADERS,impersonate="chrome",)
print(f"  [{response.status_code}] {url}")
if response.status_code == 200:
    sel = Selector(response.text)

    total_pages = 1
    for href in sel.xpath('//a[contains(@href, "?page=")]/@href').getall():
        try:
            page_num = int(href.split("?page=")[-1].split("&")[0])
            if page_num > total_pages:
                total_pages = page_num
        except ValueError:
            pass
    print(f"  Total pages: {total_pages}")
    #__________________________________________________________parser_________________________________________________

from curl_cffi import requests
from parsel import Selector
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










