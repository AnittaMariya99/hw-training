from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, FloatField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_PRODUCTS, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    url = StringField()
    slug = StringField()
    product_count = IntField()
    parent_slug = StringField()


class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    url = StringField()
    slug = StringField()
    category_name = StringField()
    category_url = StringField()
    

class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"} 
    unique_id = StringField()
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
    regular_price = StringField()
    selling_price = FloatField()
    price_was = StringField()
    promotion_price = StringField()
    percentage_discount = StringField()
    promotion_description = StringField()
    price_per_unit = StringField()
    currency = StringField()
    breadcrumb_path = StringField()
    pdp_url = StringField()
    product_description = StringField()
    instructions = StringField()
    storage_instructions = StringField()
    instructionforuse = StringField()
    country_of_origin = StringField()
    allergens = StringField()
    nutritional_information = DictField()
    image_url_1 = StringField()
    image_url_2 = StringField()
    image_url_3 = StringField()
    features = StringField()
    distributor_address = StringField()
    alchol_by_volume = StringField()
    site_shown_uom = StringField()
    ingredients = StringField()
    product_unique_key = StringField()   
    instock = StringField()
    file_name_1 = StringField()
    image_url_1 = StringField()
    file_name_2 = StringField()
    image_url_2 = StringField()
    file_name_3 = StringField()
    image_url_3 = StringField()
    file_name_4 = StringField()
    image_url_4 = StringField()
    file_name_5 = StringField()
    image_url_5 = StringField()
    file_name_6 = StringField()
    image_url_6 = StringField()
    label_information = StringField()
    manufacturer_address = StringField()
    netweight = StringField()
    dimensions = StringField()
    

    


    
    
    
    