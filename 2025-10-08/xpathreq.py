import requests
url="https://styleunion.in/collections/women-western-wear/products/graphic-longline-active-tee-wact00068"
headers = {
     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
     'accept-language': 'en-US,en;q=0.9',
     'cache-control': 'max-age=0',
     'if-none-match': '"cacheable:256876de9865c9b0d4173eecc05e8335"',
     'priority': 'u=0, i',
     'sec-ch-ua': '"Not=A?Brand";v="24", "Chromium";v="140"',
     'sec-ch-ua-mobile': '?0',
     'sec-ch-ua-platform': '"Linux"',
     'sec-fetch-dest': 'document',
     'sec-fetch-mode': 'navigate',
     'sec-fetch-site': 'same-origin',
     'sec-fetch-user': '?1',
     'upgrade-insecure-requests': '1',
     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
 }
response = requests.get(
     'https://styleunion.in/collections/women-western-wear/products/graphic-longline-active-tee-wact00068',
     headers=headers,
 )
response.status_code
print(response.status_code)

response.text
# print(response.text)


from parsel import Selector
sel = Selector(response.text)
product_name = sel.xpath('//h1[@class="product__section-title product-title"]/text()').get()
print(product_name)


price = sel.xpath("//div[@class='price__pricing-group']/dl[@class='price__regular']//span[@class='price-item price-item--regular']/text()").get()
print(price)

sku = sel.xpath("//span[@id='variantSku']/text()").get()
print(sku)

size = sel.xpath("//span[.='S']/text()").get()
print(size)

discriptionHD=sel.xpath("//h3[.='Description']/text()").get()
print(discriptionHD)

discription1=sel.xpath("//div[@class='desc_inner acc__card']/div[@class='acc__panel']/text()").get()
print(discription1)

discription2h=sel.xpath("//strong[.='Comfortable Fabric:']/text()").get()
print(discription2h)

discription2=sel.xpath("//div[@class='desc_inner acc__card']/div[@class='acc__panel']/text()").get()
li = sel.xpath("//div[@class='desc_inner acc__card']/div[@class='acc__panel']/ul/li/text()").getall()
li_joined = ''.join(li)
print(li_joined)



