import logging
from curl_cffi import requests
from mongoengine import connect
from parsel import Selector
import re

from settings import (BASE_URL, HEADERS, MONGO_DB, MONGO_HOST, MONGO_PORT)
from items import ProductResponseItem, AgentDataItem, ProductFailedItem


class Parser:
    """Parser for Allie Beth agent details (MongoEngine)"""

    def __init__(self):
        # MongoEngine connection
        connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, alias="default")

    def start(self):
        """Start parsing agent profiles"""

        urls = ProductResponseItem.objects.only("url")

        logging.info(f"Loaded {urls.count()} URLs")

        for obj in urls:
            url = obj.url
            
            # Using curl_cffi to impersonate chrome
            response = requests.get(url, headers=HEADERS, impersonate="chrome", timeout=60)

            if response.status_code == 200:
                self.parse_item(url, response.text)
            else:
                logging.warning(f"Failed ({response.status_code}): {url}")
                ProductFailedItem(url=url, reason=str(response.status_code)).save()

        logging.info("Completed!")

    def parse_item(self, url, html_content):
        """Parse agent profile page"""

        sel = Selector(html_content)

        # XPATH SECTION - Allie Beth Allman & Associates specific structure
        NAME_XPATH = '//h2/text()'
        IMAGE_STYLE_XPATH = '//div[@class="site-bio-image"]/@style'
        TITLE_XPATH = '//div[@class="site-info-contact"]/h2/following-sibling::p[1][not(descendant::a)]/text()'
        DESCRIPTION_XPATH = '//div[@class="site-about-column"]//text()'
        SOCIAL_XPATH = '//ul[contains(@class,"site-bio-social")]//a/@href'
        AGENT_PHONE_XPATH = '//a[starts-with(@href,"tel:")]/text()'
        WEBSITE_XPATH = '//a[.//i[@class="rni-website"]]/@href'
        
        # Address is in the info column after the phone
        STREET_XPATH = '//div[@class="site-info-contact"]/p/b/text()'
        CITY_STATE_ZIP_XPATH = '//div[@class="site-info-contact"]/p[b]/text()[2]'
        # //div[@class="site-info-contact"]/p/text()

        # Extraction
        name = sel.xpath(NAME_XPATH).get()
        image_style = sel.xpath(IMAGE_STYLE_XPATH).get()
        desc = "".join(sel.xpath(DESCRIPTION_XPATH).getall()).strip()
        agent_phone_numbers = " | ".join(sel.xpath(AGENT_PHONE_XPATH).getall())
        social_links = sel.xpath(SOCIAL_XPATH).getall()
        website = sel.xpath(WEBSITE_XPATH).get() or ""
        title = sel.xpath(TITLE_XPATH).get()
        street = sel.xpath(STREET_XPATH).get()
        city_state_zip = sel.xpath(CITY_STATE_ZIP_XPATH).get()
        langs = ""

        name = name.strip() if name else ""
        parts = name.split() if name else []
        first_name = parts[0] if parts else ""
        middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
        last_name = parts[-1] if len(parts) > 1 else ""

        if not title:
            title = ""

        image_url = ""
        if image_style:
            # Parse URL from: background-image:url(https://...)
            match = re.search(r'url\((.*?)\)', image_style)
            if match:
                image_url = match.group(1)
        
        # Address parsing
        city = state = zipcode = ""
        if city_state_zip:
            # Example: "Dallas TX 75219" or "Dallas, TX 75219"
            city_state_zip = city_state_zip.replace(',', '').strip()
            if len(city_state_zip.split()) == 3:
                city, state, zipcode = city_state_zip.split()
            elif len(city_state_zip.split()) == 2:
                city, state = city_state_zip.split()

        # Initialize item
        item = {}
        item["profile_url"] = url
        item["first_name"] = first_name
        item["middle_name"] = middle_name
        item["last_name"] = last_name
        item["image_url"] = image_url
        item["address"] = f"{street} {city_state_zip}".strip() if street or city_state_zip else ""
        item["description"] = desc
        item["languages"] = langs
        item["social_links"] = social_links
        item["website"] = website
        item["title"] = title
        item["street_address"] = street
        item["city"] = city
        item["state"] = state
        item["zip_code"] = zipcode
        item["country"] = "USA"
        item["agent_phone_numbers"] = agent_phone_numbers

        # Save to database
        
        AgentDataItem(**item).save()
        logging.info(f"Saved agent: {first_name} {last_name}")
        
    def close(self):
        logging.info("Parser finished.")


if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()
