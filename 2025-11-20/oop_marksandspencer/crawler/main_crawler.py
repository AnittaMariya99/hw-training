import requests
from parsel import Selector
from pymongo import MongoClient
from .utils.logger import get_logger
from .settings import BASE_URL, HEADERS, MONGO_URI, DB_NAME, COLLECTION
from .utils.exceptions import DataMiningError

logger = get_logger("main_crawler")

# ---------------------------
#MarksAndSpencercrawler Class
# ---------------------------
class MarksAndSpencercrawler:
    def __init__(self):
        """Initialize crawler, DB, logs."""
        logger.info("Initializing MarksAndSpencerParser...")

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

        self.raw_file = "raw.html"
        self.cleaned_file = "cleaned_data.txt"                                                                                                  

    # ---------------------------
    # FETCH HTML WITH EXCEPTION HANDLING
    # ---------------------------
    def fetch_html(self, url):
        """Fetch HTML from a URL with exception handling."""
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                raise DataMiningError(
                    f"Invalid response {response.status_code} from {url}"
                )

            html = response.text

            # Save raw HTML
            with open(self.raw_file, "w", encoding="utf-8") as f:
                f.write(html)

            return html

        except requests.exceptions.RequestException as err:
            logger.error(f"Connection error: {err}")
        except DataMiningError as dm_err:
            logger.error(f"Htmpl fetch error: {dm_err}")
            

    # ---------------------------
    # PARSE HTML (mock BeautifulSoup)
    # ---------------------------
    def parse_data(self, html):
        """Return Selector object for HTML parsing."""
        try:
            return Selector(html)
        except Exception as err:
            raise DataMiningError(f"Parsing failed: {err}")

    # ---------------------------
    # SAVE CLEANED DATA TO FILE
    # ---------------------------
    def save_to_file(self, data_list):
        """Save cleaned data (product URLs) to file."""
        with open(self.cleaned_file, "w", encoding="utf-8") as f:
            for item in data_list:
                f.write(item + "\n")

    
    # ---------------------------
    # PARSE ITEMS – MAIN EXTRACTION LOGIC
    # ---------------------------
    def parse_item(self, html):
        """Extract category → subcategory → product links."""
        sel = self.parse_data(html)

        # Extract main categories
        links = sel.xpath('//a[@class="media-0_body__yf6Z_ '
                          'media-1280_textSm__V3PzB gnav_burgerItemHeading__8myW8 '
                          'gnav_tabHeading__Qwe6W"]/@href').getall()

        main_links = [
            link if link.startswith("http") else BASE_URL + link
            for link in links
        ]

        logger.info(f"Main category found: {len(main_links)}")

        all_product_links = []

        # Loop categories
        for category_url in main_links:
          
            logger.info(f"\nProcessing category: {category_url}")
        
            category_html = self.fetch_html(category_url)
            category_sel = Selector(category_html)

            sub_links = category_sel.xpath(
                '//a[@class="circular-navigation_circularNavigationLink__IbVNd"]/@href'
            ).getall()

            subcategory_links = [
                sl if sl.startswith("http") else BASE_URL + sl
                for sl in sub_links
            ]

            # Loop subcategories + pagination
            for sub_url in subcategory_links:
              
                logger.info(f"Subcategory: {sub_url}")

                products_links_in_subcategory = []

                visited_pages = []
                while sub_url and sub_url not in visited_pages:
                    visited_pages.append(sub_url)

                    page_html = self.fetch_html(sub_url)
                    try:
                        page_sel = Selector(page_html)
                    except Exception as err:
                        logger.error(f"Failed to parse page HTML: {err}")
                        break
                        
                    products = page_sel.xpath(
                        "//a[@class='product-card_cardWrapper__GVSTY']/@href").getall()

                    for p in products:
                        full = p if p.startswith("http") else BASE_URL + p
                        all_product_links.append(full)
                        products_links_in_subcategory.append(full)

                    next_page = page_sel.xpath(
                        '//a[@aria-label="Next page"]/@href'
                    ).get()

                    sub_url = (BASE_URL + next_page) if next_page else None

                self.save_urls_to_mongo(products_links_in_subcategory)

        return all_product_links
    
    # ---------------------------
    # SAVE CLEANED DATA TO MONGODB
    # ---------------------------
    def save_urls_to_mongo(self, url_list):
        """Save cleaned data (product URLs) to MongoDB."""
        for url in url_list:
            self.collection.update_one(
                {"url": url},
                {"$set": {"url": url}},
                upsert=True
            )

    # ---------------------------
    # START CRAWLER
    # ---------------------------
    def start(self, url):
        html = self.fetch_html(url)
        product_links = self.parse_item(html)

        logger.info(f"\nTotal extracted product URLs: {len(product_links)}")

        self.save_to_file(product_links)
        
        logger.info(f"All data saved to file successfully.")

    # ---------------------------
    # CLOSE CONNECTIONS
    # ---------------------------
    def close(self):
        """Close database."""
        
        logger.info(f"Closing DB connection...")
        self.client.close()




