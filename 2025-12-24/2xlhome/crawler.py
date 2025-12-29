from asyncio.log import logger
import logging
from curl_cffi import requests
from parsel import Selector
from mongoengine import connect
from settings import HEADERS, MONGO_DB, MONGO_COLLECTION_DATA,MONGO_HOST,MONGO_PORT
from items import CategoryUrlItem,ProductUrlItem
import html as html_module
import json

class Crawler:
    """Crawling Urls"""

    def __init__(self):
        self.mongo = connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, alias="default")

    def start(self):
        """Requesting Start url"""
        # Fetch status='pending' urls from CategoryUrlItem
        categories = CategoryUrlItem.objects()
        
        logging.info(f"Found {categories.count()} pending urls")

        for category in categories:
            url = category.url
            logging.info(f"\nProcessing: {url}")
            
            # Simple pagination loop
            params = {}
            page = 1
            while True:
                logger.info(f"Fetching: page {page} ...")

                response = requests.get(url, headers=HEADERS, params=params, impersonate='chrome')

                if response.status_code == 200:
                    
                    html = response.text
                    if (page > 1):
                        #> sections > product_list
                        # logging.info(f"Response: {response.json()}")
                        html = response.json().get('sections', {}).get('product_list', '')
                        html = html_module.unescape(html)

                    total_pages, _category_id, core_filters, isPowerListingAjax = self.parse_item(html)
                    # logging.info(f"url: {url}")
                    # logging.info(f"Total pages: {total_pages}")
                    # logging.info(f"Category id: {_category_id}")
                    # logging.info(f"Core filters: {core_filters}")
                    # logging.info(f"Is Power Listing Ajax: {isPowerListingAjax}")    
                    if (page >= total_pages):
                        logging.info(f"Completed category: {url}")
                        break

                    page += 1
                    
                    params = {
                        "p": page,
                        "_category_id": _category_id,
                        "core_filters": core_filters,
                        "isPowerListingAjax": isPowerListingAjax,
                        "_sections": "product_list"
                    }

                else:
                    logging.warning(f"Status {response.status_code} for {url}")
                    break

    def parse_item(self, html):
        """item part"""
        sel = Selector(html)

        PRODUCT_CONTAINER_XPATH = '//li[@class="product-card item product product-item"]'
        PRODUCT_URL_XPATH = './/a[@class="product-item-link"]/@href'
        PRODUCT_ID_XPATH = './/strong[@class="product name product-item-name"]/@data-product-id'
        PRODUCT_NAME_XPATH = './/a[@class="product-item-link"]//text()'
        PRODUCT_PRICE_XPATH = './/div[@class="price-section"]//span[@class="special-price"]/p/span/text()'
        PRODUCT_WAS_PRICE_XPATH = './/div[@class="price-section"]//span[@class="old-price"]/p/span/text()'
        PRODUCT_IMAGE_XPATH = './/img/@image-data-src'
        PRODUCT_IMAGE_ALT_XPATH = './/img/@src'

        SCRIPT_TAG_XPATH = '//script[@type="text/x-magento-init"]//text()'
                
        products = sel.xpath(PRODUCT_CONTAINER_XPATH)
        
        for product in products:

            url = product.xpath(PRODUCT_URL_XPATH).get()
            product_id = product.xpath(PRODUCT_ID_XPATH).get()
            product_name = product.xpath(PRODUCT_NAME_XPATH).get().strip()
            price = product.xpath(PRODUCT_PRICE_XPATH).get()
            was_price = product.xpath(PRODUCT_WAS_PRICE_XPATH).get()
            image = product.xpath(PRODUCT_IMAGE_XPATH).getall()

            if(not image or len(image) == 0):
                image = product.xpath(PRODUCT_IMAGE_ALT_XPATH).getall()
            
            # Item Yield
            item = {}
            item['url'] = url
            item['product_id'] = product_id
            item['product_name'] = product_name
            item['price'] = price
            item['was_price'] = was_price
            item['image'] = image
            
            logging.info(f"Product: {item}")
            
            # Save to specific collection
            ProductUrlItem(**item).save()

        # get total pages and request params from html
        script_tags = sel.xpath(SCRIPT_TAG_XPATH).getall()
        for script_tag in script_tags:
            ajax_content = json.loads(script_tag).get('*', {}).get('power_listing_ajax_actions')
            # logging.info(f"Ajax content: {ajax_content}")
            if not ajax_content:
                continue

            total_pages = ajax_content['total_pages']
            _category_id = ajax_content['category_id']
            core_filters = ajax_content['core_filters']
            isPowerListingAjax = ajax_content['isPowerListingAjax']
            return total_pages, _category_id, core_filters, isPowerListingAjax

        return 1, None, None, None

    def close(self):
        """Close function"""
        self.mongo.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
