from playwright.sync_api import sync_playwright
from parsel import Selector
import time
from items import ProductCategoryUrlItem
from settings import BASE_URL, MONGO_DB, MONGO_HOST, MONGO_PORT
import logging
from mongoengine import connect

class Category:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, alias="default")
        logging.info("MongoDB connected")

    def start(self):
        nav_links = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(BASE_URL, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_selector('use[href*="sprite"][href*="#close"]')
    
            page.click('i.close-icon[aria-label="close"]')
    

            page.wait_for_selector('nav', timeout=30000)
            time.sleep(2)
            
            # Extract all category links
            nav_links = page.locator('a[href^="/categories/"]').all()
        
            logging.info(f"Found {len(nav_links)} total category links")
            
            # Collect all categories with their paths
            self.parse(nav_links)

            browser.close()

    def parse(self, nav_links):
        """Parsing function"""
        all_categories = {}
        for link in nav_links:
            try:
                href = link.get_attribute('href')
                text = link.inner_text().strip()

                # If inner_text is empty, try aria-label
                if not text:
                    text = link.get_attribute('aria-label')
                    if text:
                        text = text.strip()
                
                # If still empty, try text content from div inside
                if not text:
                    div_text = link.locator('div.text-container').inner_text().strip()
                    if div_text:
                        text = div_text

                logging.info(f"{text}: {href}")
                
                if href and text:
                    all_categories[href] = {
                        'name': text,
                        'url': f"https://www.sephora.sg{href}",
                        'path': href
                    }
            except:
                continue
        
        # Find leaf categories (those that are not parent to any other)
        leaf_categories = []
        for path, category in all_categories.items():
            # Check if this path is a parent to any other path
            is_parent = any(
                other_path.startswith(path + '/') 
                for other_path in all_categories.keys() 
                if other_path != path
            )
            
            # If not a parent, it's a leaf category
            if not is_parent:
                item = {}
                item["name"] = category['name']
                item["url"] = category['url']
                leaf_categories.append(item)

                ProductCategoryUrlItem(**item).save()
        
        logging.info(f"\nFound {len(leaf_categories)} leaf categories")
        

    def close(self):
        """Close function for all module object closing"""
        pass
    

if __name__ == "__main__":
    crawler = Category()
    crawler.start()
    crawler.close()  