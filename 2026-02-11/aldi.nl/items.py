from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField, FloatField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL_FAILED

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField(required=True)
    link = StringField(required=True)
    sub_name = StringField(required=True)
    sub_link = StringField(required=True)


class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    product_id = StringField(required=True)
    link = StringField(required=True)
    title = StringField(required=True)


class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"}
    unique_id = StringField(required=True)
    product_name = StringField()
    brand = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    regular_price = StringField()
    selling_price = StringField()
    percentage_discount = StringField()
    promotion_description = StringField()
    price_per_unit = StringField()
    pdp_url = StringField()
    product_description = StringField()
    image_url_1 = StringField()
    file_name_1 = StringField()
    image_url_2 = StringField()
    file_name_2 = StringField()
    image_url_3 = StringField()
    file_name_3 = StringField()
    site_shown_uom = StringField()
    product_unique_key = StringField()
    breadcrumbs = StringField()
