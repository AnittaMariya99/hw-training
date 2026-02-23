#__________________________________________________________crawler_________________________________________________
import requests

url="https://auchan.hu/api/v2/cache/tree/0?depth=10&cacheSegmentationCode=DS&hl=hu"
headers = {
    'accept': 'application/json',
    'accept-language': 'hu',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI4cG1XclQzWmxWMUFJbXdiMUhWYWE5T1BWSzkzcjhIcyIsImp0aSI6IjIyZWI1NzNhZDk5Y2RmZDkyMGI1MTE0NWU0MzMzNjA0ZjU1ZmNkNzEyZTBhY2E3MjkwNmI4MTE4YTRmMzcwZjc1MTE5OTFiNGM4ODFmMTdmIiwiaWF0IjoxNzcxNzg1MzYyLjUyNDUzNCwibmJmIjoxNzcxNzg1MzYyLjUyNDUzNiwiZXhwIjoxNzcxODcxNzYyLjUwMTA1Mywic3ViIjoiYW5vbl8yOWY2YzVmYy04NTU2LTRhNjAtODRjMi0zOTgzM2VmOGE2MjMiLCJzY29wZXMiOltdfQ.WuziK9g9YyRyQNnAyZeDVPXlMXxT1LwzLimGkl5-4LXQve6Gx7PzQruGvNAKXEAwdOfzxnOP2XsDcHMzj9Q_svIrre-8KlCgqkJyxK3QaKlCBuQfhy1Bawzv4pKxD9Bpl4LdmC6gQ9s-WFaslJxfBBVweMogyNIH867HC2stsVJi6BuCeXZDojeXy_mVrzTzdC4O3_pKCzla0xVQ2HTX1ziFryMDCPdb_-1D7IwonHlgvM3ok_sF3Lpww1jmbQkBjPE46Jge20ho5vNSPF7-PKD7EfVpesKXXFbXqwwRy_8job7DJKu8KfL-0mMb9b-kP-SH8h-ozO0G02_gvj7HGw',
    'priority': 'u=1, i',
    'referer': 'https://auchan.hu/shop/husvet/husveti-vasar.c-9486',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
def get_leaf_categories(node, path=""):
    leaves = []
    name = node.get("name", "")
    current_path = f"{path} > {name}" if path else name
    children = node.get("children", [])
    
    if node.get("level", -1) != -1 and not children:
        leaves.append({
            "id": node.get("id"),
            "name": name,
            "path": current_path,
            "link": f"https://auchan.hu/shop/{node.get('slug')}.c-{node.get('id')}"
        })
    
    for child in children:
        leaves.extend(get_leaf_categories(child, current_path if node.get("level", -1) != -1 else ""))
    return leaves

response = requests.get(url, headers=headers)
data = response.json()
leaf_categories = get_leaf_categories(data)

print(f"Total Leaf Categories Found: {len(leaf_categories)}")
for leaf in leaf_categories[:50]: # Print first 10
    print(leaf)

#__________________________________________________________crawler_________________________________________________



def get_products(category_id):
    base_url = "https://auchan.hu/api/v2/cache/products"
    products = []
    page = 1
    items_per_page = 16 
    
    headers = {
    'accept': 'application/json',
    'accept-language': 'hu',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI4cG1XclQzWmxWMUFJbXdiMUhWYWE5T1BWSzkzcjhIcyIsImp0aSI6IjIyZWI1NzNhZDk5Y2RmZDkyMGI1MTE0NWU0MzMzNjA0ZjU1ZmNkNzEyZTBhY2E3MjkwNmI4MTE4YTRmMzcwZjc1MTE5OTFiNGM4ODFmMTdmIiwiaWF0IjoxNzcxNzg1MzYyLjUyNDUzNCwibmJmIjoxNzcxNzg1MzYyLjUyNDUzNiwiZXhwIjoxNzcxODcxNzYyLjUwMTA1Mywic3ViIjoiYW5vbl8yOWY2YzVmYy04NTU2LTRhNjAtODRjMi0zOTgzM2VmOGE2MjMiLCJzY29wZXMiOltdfQ.WuziK9g9YyRyQNnAyZeDVPXlMXxT1LwzLimGkl5-4LXQve6Gx7PzQruGvNAKXEAwdOfzxnOP2XsDcHMzj9Q_svIrre-8KlCgqkJyxK3QaKlCBuQfhy1Bawzv4pKxD9Bpl4LdmC6gQ9s-WFaslJxfBBVweMogyNIH867HC2stsVJi6BuCeXZDojeXy_mVrzTzdC4O3_pKCzla0xVQ2HTX1ziFryMDCPdb_-1D7IwonHlgvM3ok_sF3Lpww1jmbQkBjPE46Jge20ho5vNSPF7-PKD7EfVpesKXXFbXqwwRy_8job7DJKu8KfL-0mMb9b-kP-SH8h-ozO0G02_gvj7HGw',
    'priority': 'u=1, i',
    'referer': f'https://auchan.hu/shop/c-{category_id}',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
    
    while True:
        params = {
            'categoryId': category_id,
            'itemsPerPage': items_per_page,
            'page': page,
            'cacheSegmentationCode': 'DS',
            'hl': 'hu'
        }
        
        print(f"Fetching page {page} for category {category_id}...")
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching products: {response.status_code}")
            break
            
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            break
            
        for item in results:
            variant = item.get('selectedVariant', {})
            name = variant.get('name')
            sku = variant.get('sku')
            
            if name and sku:
                slug = slugify(name)
                url = f"https://auchan.hu/shop/{slug}.p-{sku}"
                products.append({
                    "name": name,
                    "url": url
                })
            
        page_count = data.get('pageCount', 1)
        if page >= page_count:
            break
            
        page += 1
        
    return products


#__________________________________________________________parser_________________________________________________


api_url = "https://auchan.hu/api/v2/cache/products"
params = {
    'auchanCodes[]': sku,
    'page': 1,
    'itemsPerPage': 16,
    'cacheSegmentationCode': 'DS',
    'hl': 'hu'
}
resp = requests.get(api_url, headers=headers, params=params)
if resp.status_code != 200:
    print(f"Failed to fetch product info: {resp.status_code}")
    print(f"Response: {resp.text}")
    return None

data = resp.json()
if not data.get('results'):
    print("Product not found in API results")
    return None
    
product_data = data['results'][0]
variant = product_data.get('selectedVariant', {})
product_id = product_data.get('id')
variant_id = variant.get('id')