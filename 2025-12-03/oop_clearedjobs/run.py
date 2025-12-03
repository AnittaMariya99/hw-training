# run.py
# from Main_crawler import clearedjobscrawler
from product_parser import clearedjobsParser

# # First: Crawl categories → Get product URLs
# list_crawler = clearedjobscrawler()
# list_crawler.start()
# list_crawler.close()

# Second: Extract product details
product_parser = clearedjobsParser()
product_parser.start()
# product_parser.parse_single_product(
#     "https://clearedjobs.net/api/v1/jobs/1835293?locale=en&mt=3520786441",
#     "https://clearedjobs.net/company/maximus-388055"
# )
product_parser.close()
