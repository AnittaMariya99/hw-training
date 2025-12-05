
# from Main_crawler import classiccarscrawler
# from settings import BASE_URL
from product_parser import classiccarsProductParser
 
# # First: Crawl categories → Get product URLs
# list_crawler = classiccarscrawler()
# list_crawler.start(BASE_URL)
# list_crawler.close()

# Second: Extract product details
product_parser = classiccarsProductParser()
product_parser.start()
# product_parser.parse_single_product("https://classiccars.com/listings/view/1045220/1967-lola-t-70-for-sale-in-lakeland-florida-33813")
product_parser.close()
