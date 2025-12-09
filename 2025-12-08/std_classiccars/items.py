from mongoengine import DynamicDocument, StringField, BooleanField, DictField, ListField, IntField, FloatField
#from settings import (
#    MONGO_COL_URL, MONGO_COLLECTION_EMPTY,
#    MONGO_COLLECTION_URL_FAILED,
#    MONGO_COLLECTION_DATA, MONGO_COLLECTION_MISMATCH,
#    MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_IMAGES, MONGO_COLLECTION_CATEGORY,
#    MONGO_COLLECTION_STORE_CODE, MONGO_COLLECTION_COUNT, MONGO_COLLECTION_PAGINATION
#
#)


class ProductItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""

    #meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
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

    #meta = {"db_alias": "default", "collection": MONGO_COL_URL}
    url = StringField(required=True)


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
