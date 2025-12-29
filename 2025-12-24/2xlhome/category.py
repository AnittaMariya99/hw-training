import logging
import json
from mongoengine import connect
from curl_cffi import requests
from parsel import Selector
from items import CategoryUrlItem
from settings import HEADERS, MONGO_DB, BASE_URL,MONGO_HOST,MONGO_PORT


class Crawler:
    """Crawling Urls"""

    def __init__(self):
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, alias="default")

    def start(self):
        """Requesting Start url"""
        logging.info("Fetching homepage to extract category names...")

        response = requests.get(BASE_URL, headers=HEADERS,impersonate='chrome')

        logging.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            self.parse_item(response)
        else:
            logging.error(f"Failed to fetch homepage. Status code: {response.status_code}") 

    def parse_item(self, response):
        """item part"""
        sel = Selector(response.text)

        MAIN_CATEGORY_XPATH = '//ul[contains(@class,"md-top-menu-items")]/li[contains(@class,"category-item")]'
        MAIN_CATEGORY_NAME_XPATH = './a/span//text()'

        SUB_CATEGORY_XPATH = './/div[@class="col-menu-3 vertical-menu-left"]/ul/li'
        SUB_CATEGORY_NAME_XPATH = './a//text()'
        SUB_CATEGORY_ID_XPATH = './@data-subcat-id'



        # ---------------- Main Category ---------------- #
        main_categories = sel.xpath(MAIN_CATEGORY_XPATH)
        for main_category in main_categories:
            main_category_name = main_category.xpath(MAIN_CATEGORY_NAME_XPATH).get()
            
            logging.info(f"Main Category: {main_category_name}")

            sub_categories = main_category.xpath(SUB_CATEGORY_XPATH)
            for sub_category in sub_categories:
                sub_category_name = sub_category.xpath(SUB_CATEGORY_NAME_XPATH).get()
                sub_category_id = sub_category.xpath(SUB_CATEGORY_ID_XPATH).get()
                
                logging.info(f"\tSub Category: {sub_category_name} {sub_category_id}")

                SUB_SUB_CATEGORY_XPATH = f'.//div[@class="col-menu-9 vertical-menu-content"]/div[@data-cat-id="{sub_category_id}"]/ul/li/h4/a'
                SUB_SUB_CATEGORY_NAME_XPATH = './/text()'
                SUB_SUB_CATEGORY_URL_XPATH = './@href'

                sub_sub_categories = main_category.xpath(SUB_SUB_CATEGORY_XPATH)
                for sub_sub_category in sub_sub_categories:
                    sub_sub_category_name = sub_sub_category.xpath(SUB_SUB_CATEGORY_NAME_XPATH).get()
                    sub_sub_category_url = sub_sub_category.xpath(SUB_SUB_CATEGORY_URL_XPATH).get()
                    
                    logging.info(f"\t\tSub Sub Category: {sub_sub_category_name} {sub_sub_category_url}")

                    # Saving details in mongo
                    item = {}
                    item['url'] = sub_sub_category_url
                    item['main_category'] = main_category_name
                    item['sub_category'] = sub_category_name
                    item['sub_category_id'] = sub_category_id
                    item['sub_sub_category'] = sub_sub_category_name

                    CategoryUrlItem(**item).save()
                    logging.info(f"\t\tSub Sub Category saved: {sub_sub_category_name}")


    def close(self):
        """Close function for all module object closing"""

        self.mongo.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()    