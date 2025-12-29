from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField
from settings import MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_URL_FAILED, MONGO_COLLECTION_DATA

class CategoryUrlItem(DynamicDocument):
    meta = {'collection': MONGO_COLLECTION_CATEGORY }
    url = StringField(required=True)
    main_category = StringField(required=True)
    sub_category = StringField(required=True)
    sub_category_id = StringField(required=True)
    sub_sub_category = StringField(required=True)

class ProductUrlItem(DynamicDocument):
    meta = {"collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True, unique=True) 
    product_id = StringField() 
    product_name=StringField()
    price=StringField()
    was_price=StringField()
    image=ListField(StringField())


class ProductFailedItem(DynamicDocument):
    url = StringField()
    reason = StringField()
    meta = {'collection': MONGO_COLLECTION_URL_FAILED}

class ProductDataItem(DynamicDocument):
    meta = {'collection': MONGO_COLLECTION_DATA}
    url = StringField()
    product_id = StringField() 
    product_name=StringField()
    price=StringField()
    was_price=StringField()
    image=ListField(StringField())

    product_color = StringField()
    material = StringField()
    details_string = StringField()
    specification = DictField()
    product_type = StringField()

    quantity = StringField()
    breadcrumb = StringField()
    stock = StringField()
    
    # Detailed fields
    # color = StringField()
    # material = StringField()
    # quantity = StringField()
    # description = StringField()
    # specification = DictField()
    # product_type = StringField()
    # breadcrumb = StringField()
    # stock = StringField()