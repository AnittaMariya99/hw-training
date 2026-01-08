from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED, MONGO_COLLECTION_URL
from mongoengine import BooleanField

class ProductCategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_CATEGORY}

    url = StringField(required=True)
    name = StringField()


class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL}

    product_url = StringField(required=True)
    sub_category_url = StringField(required=True)
    sub_category_name = StringField()


class ProductDataItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
    
    url = StringField(required=True)
    product_name = StringField()
    brand = StringField()
    currency = StringField()
    retailer_id = StringField()
    retailer = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    original_price = StringField()
    selling_price = StringField()
    promotion_description = StringField()
    pdp_url = StringField()
    image_url = ListField()
    ingredients = StringField()
    directions = StringField()
    disclaimer = StringField()
    description = StringField()
    diet_suitability = StringField()
    colour = StringField()
    hair_type = StringField()
    skin_type = ListField()
    skin_tone = StringField()       



class ProductFailedItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL_FAILED}

    url = StringField(required=True)
    reason = StringField()