import logging
from playwright.sync_api import sync_playwright
from parsel import Selector
from mongoengine import connect
from settings import MONGO_DB, MONGO_HOST, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_URL
from items import ProductCategoryUrlItem, ProductUrlItem
import time


class Crawler:
    """Crawling Product URLs from Categories"""

    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, alias="default")
        logging.info("MongoDB connected")

    def start(self):
        """Requesting Start URL - Get categories from MongoDB"""
        
        # Fetch all categories from MongoDB
        categories = ProductCategoryUrlItem.objects.all()
        
        if not categories:
            logging.warning("No categories found in database")
            return
        
        logging.info(f"Found {categories.count()} categories to crawl")
        
        # Launch browser once for all categories
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            for idx, category in enumerate(categories, 1):
                logging.info(f"[{idx}/{categories.count()}] Processing: {category.name}")
                
                meta = {}
                meta['sub_category_url'] = category.url
                meta['sub_category_name'] = category.name
                meta['page'] = 1
                
                try:
                    page.goto(category.url, timeout=60000)
                    
                    while True:
                        # Wait for products to load
                        page.wait_for_selector("a[href*='/products/']", timeout=30000)
                        
                        # Parse products
                        response = page.content()
                        is_next = self.parse_item(response, meta)
                        
                        if not is_next:
                            logging.info(f"Pagination completed for {category.name}")
                            break
                        
                        # Try next page
                        try:
                            next_button = page.locator("a[aria-label='Next Page']")
                            if next_button.is_visible(timeout=5000):
                                next_button.click()
                                page.wait_for_load_state("networkidle")
                                time.sleep(2)
                                meta['page'] += 1
                            else:
                                break
                        except:
                            break
                    
                    time.sleep(2)  # Delay between categories
                    
                except Exception as e:
                    logging.error(f"Error processing {category.name}: {e}")
            
            browser.close()
        
        logging.info("Crawling completed for all categories")

    def parse_item(self, response, meta):
        """Parse product items from page"""
        
        sel = Selector(text=response)
        
        # XPATH
        PRODUCT_XPATH = '//a[contains(@href,"/products/")]'
        
        # EXTRACT
        products = sel.xpath(PRODUCT_XPATH)
        
        if products:
            logging.info(f"Page {meta.get('page')}: Found {len(products)} product links")
            
            for product in products:
                url = product.xpath('@href').extract_first()
                
                if url:
                    # Make absolute URL
                    if url.startswith('/'):
                        url = f"https://www.sephora.sg{url}"
                    
                    # ITEM
                    item = {}
                    item['product_url'] = url
                    item['sub_category_url'] = meta.get('sub_category_url')
                    item['sub_category_name'] = meta.get('sub_category_name')
                    
                    try:
                        # Save to MongoDB using items
                        product_item = ProductUrlItem(**item)
                        product_item.save()
                        logging.info(f"Saved: {url}")
                        
                    except Exception as e:
                        # Skip duplicates
                        pass
            
            return True
        
        return False

    def close(self):
        """Close function for all module object closing"""
        
        if self.mongo:
            self.mongo.close()
            logging.info("MongoDB connection closed")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()