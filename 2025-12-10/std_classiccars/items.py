from mongoengine import DynamicDocument, StringField, BooleanField, DictField, ListField, IntField, FloatField
from settings import (
   MONGO_COLLECTION_URL_FAILED,MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_DATA
)


class ProductItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
    url = StringField()
    listing_id = StringField()
    year = StringField()
    make = StringField()
    model = StringField()
    location = StringField()
    exterior_color = StringField()
    interior_color = StringField()
    mileage = StringField()
    transmission = StringField()
    engine = StringField()
    drive_train = StringField()
    description = StringField()


class ProductUrlItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True)
    image_url = StringField()
    title = StringField()
    price = StringField()


class ProductMismatchItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_MISMATCH}
    input_style = StringField(required=True)


class ProductEmptyItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_EMPTY}
    input_style = StringField(required=True)


class ProductCountItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_COUNT}
    zipcode = StringField(required=True)


class ProductResponseItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True)


class ProductFailedItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL_FAILED}
    url = StringField(required=True)


class ProductCategoryUrlItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_CATEGORY}

    url = StringField(required=True)


class ProductPageItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_PAGINATION}
    url = StringField(required=True)
