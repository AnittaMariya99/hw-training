import requests
from parsel import Selector
import json

def extract_property_urls(api_url, output_file="the_house_of_rare_product_links.txt"):
    try:
        
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Unbxd API stores products under "response" → "products"
        products = response.json().get("response", {}).get("products", [])

        # Step 3: Extract product URLs
        extracted_urls = []
        for product in products:
            if "productUrl" in product:
                extracted_urls.append(product["productUrl"])
        

        full_links = []
        for extracted in extracted_urls:
            if extracted.startswith("http"):
                full_links.append(extracted)
            else:
                full_links.append(f"https://thehouseofrare.com{extracted}")
            

        # Step 5: Save URLs to a text file
        with open(output_file, "w", encoding="utf-8") as f:
            for link in full_links:
                f.write(link.strip() + "\n")

        print(f"Extracted {len(full_links)} URLs and saved to '{output_file}'")

    except requests.exceptions.RequestException as e:
        print(f" Request failed: {e}")
    except json.JSONDecodeError:
        print(" Failed to parse JSON response")

# Example usage
api_url = "https://search.unbxd.io/e94cac92f0f2da84ae5ca93f42a57658/ss-unbxd-aapac-prod-shopify-houseofrare58591725608684/category?p=category_handle_uFilter%3A%22rare-rabbit-all-product%22&uid=uid-1760959858009-91593&facet.multiselect=true&variants=true&variants.fields=variantId%2Cv_Size%2Cv_availableForSale%2Cv_sku&variants.count=20&fields=title%2CuniqueId%2Cprice%2CimageUrl%2CproductUrl%2Cmeta_my_fields_main_title%2Chandle%2Cimages%2Cvariants%2Cmeta_my_fields_sub_title%2CcompareAtPrice%2Ccomputed_discount%2Cgrouped_products%2Cmeta_custom_variant_color_image%2Cmeta_my_fields_COLOR%2Cswatch_image_url%2Cmeta_custom_gender%2Cmeta_custom_best_price%2Cbest_price%2Curl%2Cv_sku%2Cgst_saving_amount&spellcheck=true&pagetype=boolean&start=0&rows=20&sort="
extract_property_urls(api_url)
