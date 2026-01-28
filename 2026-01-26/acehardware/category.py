from settings import MONGO_URI,MONGO_DB,CATEGORY_URL,MONGO_COLLECTION_CATEGORY
import requests
import logging
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
class CategoryCrawler:
    """Crawling Urls"""

    def __init__(self):
        """Initialize crawler, DB, logs."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo = self.mongo_client[MONGO_DB]
        


    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        # .........................................................................
        cookies = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the website
            page.goto('https://www.acehardware.com')


            # Get all cookies
            for cookie in context.cookies():
                cookies[cookie['name']] = cookie['value']

            browser.close()


        # .........................................................................................

        payload = {"operationName":"CategoryTree","variables":{},"query":"query CategoryTree {\ncategoriesTree(includeAttributes: true){\ntotalCount\nitems{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\nattributes{\nfullyQualifiedName\nvalues\n}\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\nchildrenCategories{\ncategoryId\ncategoryCode\nisDisplayed\nparentCategory{\ncategoryId\n}\ncontent{\nname\nslug\n}\n}\n}\n}\n}\n}\n}\n}"}
        response = requests.post(CATEGORY_URL,json=payload,cookies=cookies)
        logging.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            self.parse_item(response)


    def parse_item(self, response):
        """Extract category links and basic details"""

        data = response.json()

        items = data.get("data", {}).get("categoriesTree", {}).get("items", [])
        #filter items where content > name is Departments
        items = [item for item in items if item.get("content", {}).get("name", "") == "Departments"]

        stack = [(item, "https://www.acehardware.com") for item in items]

        count = 0


        while stack:
            curr, base_url = stack.pop()
            isDisplayed = curr.get("isDisplayed", False)
            parentCategory = curr.get("parentCategory", {})
            content = curr.get("content", {})
            slug = content.get("slug", "")
            name = content.get("name", "")
            categoryId = curr.get("categoryId", "")

            if not isDisplayed:
                continue

            url = f"{base_url}/{slug}" if slug else base_url
            children = curr.get("childrenCategories", [])
            # Filter children with isDisplayed = True, it should not be null
            children = [child for child in children if child.get("isDisplayed", False)]

            if not children:
            
                item = {
                    "url": url,
                    "category_name": name,
                    "category_id": categoryId     
                }

                logging.info(f"Found category: {name} - {url}")
                count += 1
                self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)

            else:
                for child in reversed(children):
                    stack.append((child, url))

        logging.info(f"Total categories found: {count}")

    def close(self):
        """Close function for all module object closing"""

        self.mongo_client.close()

        
if __name__ == "__main__":
    crawler = CategoryCrawler()
    crawler.start()
    crawler.close()


