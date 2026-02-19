from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, FloatField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    category_name = StringField()
    category_url = StringField(unique=True)
   

class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    product_id = StringField(required=True, unique=True)     
    name = StringField()
    url_key = StringField()
    url = StringField()

class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"}
    unique_id = StringField(required=True)   
    name = StringField()
    url = StringField()
    breadcrumbs = StringField()
    extraction_date = StringField()
    product_details = DictField()
    regular_price = FloatField()
    selling_price = FloatField()
    currency = StringField()
    gender = StringField()
    color = StringField()
    size = StringField()
    quantity = StringField()
    image = ListField(StringField())
    description = StringField()
    
   