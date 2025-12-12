from mongoengine import DynamicDocument, StringField, BooleanField, DictField, ListField, IntField, FloatField
from settings import (
   MONGO_COLLECTION_URL_FAILED,MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA
)

class ProductItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
    url = StringField(required=True)
    image_url = StringField()
    price = StringField()
    description = StringField()
    make = StringField()
    model = StringField()
    year = StringField()
    color = StringField()
    vehicleIdentificationNumber = StringField()

class ProductUrlItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True)
    image_url = StringField()
    price = StringField()
    description = StringField()



