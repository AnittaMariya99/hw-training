# run.py
from Main_crawler import Bayutrcrawler, BASE_URL
from product_parser import BayutProductParser

# First: Crawl categories → Get product URLs
list_crawler = Bayutrcrawler()
list_crawler.start(BASE_URL)
list_crawler.close()

# # Second: Extract product details
# product_parser = BayutProductParser()
# product_parser.start()
# product_parser.close()
