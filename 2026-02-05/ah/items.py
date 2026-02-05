from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, FloatField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    link = StringField(unique=True)
    category_id = StringField()
    category_slug = StringField()

class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    product_id = StringField(required=True, unique=True)
    link = StringField()      
    title = StringField()

class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"}
    unique_id = StringField(unique=True)
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
    breadcrumb = StringField()
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
    servings_per_pack = StringField()

class ProductFailedItem(DynamicDocument):
    meta = {"db_alias": "default"}
    url = StringField(required=True)