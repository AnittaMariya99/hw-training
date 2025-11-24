# run.py
from crawler import MarksAndSpencercrawler, MarksAndSpencerProductParser, BASE_URL

# First: Crawl categories → Get product URLs
list_crawler = MarksAndSpencercrawler()
list_crawler.start(BASE_URL)
list_crawler.close()

# Second: Extract product details
product_parser = MarksAndSpencerProductParser()
product_parser.start()
product_parser.close()
