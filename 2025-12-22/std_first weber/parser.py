import logging
from curl_cffi import requests
from urllib.parse import urljoin
from mongoengine import connect, NotUniqueError
from parsel import Selector

from settings import (BASE_URL,HEADERS,MONGO_DB,MONGO_HOST,MONGO_PORT,)
from items import ProductResponseItem, AgentDataItem, ProductFailedItem


class Parser:
    """Parser for FirstWeber agent details (MongoEngine)"""

    def __init__(self):
        # MongoEngine connection
        connect(db=MONGO_DB,host=MONGO_HOST,port=MONGO_PORT,alias="default")

    def start(self):
        """Start parsing agent profiles"""

        urls = ProductResponseItem.objects.only("url")

        logging.info(f"Loaded {urls.count()} URLs")

        for obj in urls:
            url = obj.url
            
            response = requests.get(url,headers=HEADERS,impersonate="chrome",timeout=60)

            if response.status_code == 200:
                self.parse_item(url, response)
            else:
                logging.warning(f"Failed ({response.status_code}): {url}")
                ProductFailedItem(url=url, reason=response.status_code).save()

        logging.info( f"Completed!")

    def parse_item(self, url, response):
        """Parse agent profile page"""

        sel = Selector(response.text)

        # XPATH SECTION
        NAME_XPATH = '//p[@class="rng-agent-profile-contact-name"]/text()'
        IMAGE_XPATH = '//img[@class="rng-agent-profile-photo"]/@src'
        ADDRESS_XPATH = '//li[@class="rng-agent-profile-contact-address"]//text()'
        DESCRIPTION_XPATH = '//div[contains(@id,"widget-text-1-preview-")]/text()'
        LANGUAGES_XPATH = '//p[@class="rng-agent-profile-languages" and small[contains(text(),"Languages Spoken")]]/text()'
        SOCIAL_XPATH = '//li[@class="rng-agent-profile-contact-social"]//a/@href'
        WEBSITE_XPATH = '//li[@class="rng-agent-profile-contact-website"]/a/@href'
        TITLE_XPATH = '//p[@class="rng-agent-profile-languages" and small[contains(text(),"Designations")]]/text()'
        AGENT_PHONE_XPATH = '//a[starts-with(@href,"tel:")]/text()'

        # NAME
        name = sel.xpath(NAME_XPATH).get()
        # IMAGE
        image = sel.xpath(IMAGE_XPATH).get()
        # ADDRESS
        address = sel.xpath(ADDRESS_XPATH).getall()
        # DESCRIPTION
        desc = sel.xpath(DESCRIPTION_XPATH).get()
        # LANGUAGES
        langs = sel.xpath(LANGUAGES_XPATH).get()
        # WEBSITE
        website = sel.xpath(WEBSITE_XPATH).get()
        # TITLE
        title = sel.xpath(TITLE_XPATH).get()
        # AGENT_PHONE
        agent_phone_numbers = sel.xpath(AGENT_PHONE_XPATH).get()
        # SOCIAL
        social_links = sel.xpath(SOCIAL_XPATH).getall()

        # cleaning
        # name is a string,so converst name into a array
        parts = name.strip().split() if name else []

        first_name = parts[0] if parts else ""
        middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
        last_name = parts[-1] if len(parts) > 1 else ""

        image_url = urljoin(BASE_URL, image[0]) if image else ""

        # ADDRESS SPLIT - ['435 Village Walk Lane', 'Johnson Creek WI 53038'] to street, city, state, zipcode
        street = address[0].strip() if address else ""
        city_state_zip = address[1].strip() if len(address) > 1 else ""
        city = state = zipcode = ""
        parts = city_state_zip.split()
        if len(parts) >= 3:
            city = " ".join(parts[:-2])
            state = parts[-2]
            zipcode = parts[-1]

        # Initialize item
        item = {}
        item["profile_url"]= url
        item["first_name"] = first_name
        item["middle_name"] = middle_name
        item["last_name"] = last_name
        item["image_url"] = image_url
        item["address"] = " | ".join(address)
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

        # SAVE USING MONGOENGINE
      
        AgentDataItem(**item).save()
        logging.info(f"Saved agent: {item.get('first_name')} {item.get('last_name')}")

    def close(self):
        logging.info("Parser finished.")


if __name__ == "__main__":
    parser = Parser()
    parser.start()
    parser.close()
