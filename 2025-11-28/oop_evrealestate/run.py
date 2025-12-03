# run.py
from Main_crawler import Evrealestatecrawler
from Product_parser import EvrealestateProductParser

# First: Crawl categories → Get product URLs
list_crawler = Evrealestatecrawler()
list_crawler.start()
list_crawler.close()

# Second: Extract product details
product_parser = EvrealestateProductParser()
product_parser.start()
# product_parser.parse_single_product("https://www.evrealestate.com/en/our-advisors/abby-humes/d1e28a1f-51f9-4907-936d-0cafa1867587?userId=d1e28a1f-51f9-4907-936d-0cafa1867587")
product_parser.close()
