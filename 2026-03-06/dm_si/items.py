from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, FloatField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    link = StringField(unique=True)
    slug = StringField(unique=True)

class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    url = StringField(unique=True)
    gtin = StringField()


class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"}
    unique_id = StringField()
    competitor_name = StringField()
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    pdp_url = StringField()
    product_unique_key = StringField()
    instock = StringField()
    labelling = StringField()
    variants = DictField()
    currency = StringField()
    reviews = StringField()
    rating = StringField()
    image_url_1 = StringField()
    image_url_2 = StringField()
    image_url_3 = StringField()
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
    shown_uom = StringField()
    gramage_quantity = StringField()
    gramage_unit = StringField()
    selling_price = StringField()
    regular_price = StringField()
    price_per_unit = StringField()
    price_was = StringField()
    promotion_price = StringField()
    product_description = StringField()
    features = StringField()
    ingredients = StringField()
    manufacturer_address = StringField()
    country_of_origin = StringField()
    warnings = StringField()
    storage_instructions = StringField()
    instructionforuse = StringField()
    nutritional_information = StringField()
