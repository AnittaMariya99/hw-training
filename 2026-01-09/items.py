# items.py
# from mongoengine import DynamicDocument, StringField, ListField
# from settings import MONGO_COLLECTION_RESPONSE, MONGO_COLLECTION_URL_FAILED, MONGO_COLLECTION_DATA

# class ProductResponseItem(DynamicDocument):
#     meta = {"collection": MONGO_COLLECTION_RESPONSE, "db_alias": "default"}
#     url = StringField(required=True, unique=True)


# class AgentDataItem(DynamicDocument):
#     meta = {"collection": MONGO_COLLECTION_DATA, "db_alias": "default"}

#     profile_url = StringField(required=True, unique=True)
#     first_name = StringField()
#     middle_name = StringField()
#     last_name = StringField()
#     title = StringField()
#     description = StringField()
#     address = StringField()
#     street_address = StringField()
#     city = StringField()
#     state = StringField()
#     zip_code = StringField()
#     country = StringField()
#     languages = StringField()
#     website = StringField()
#     image_url = StringField()
#     social_links = ListField(StringField())
#     agent_phone_numbers = StringField()


# class ProductFailedItem(DynamicDocument):
#     meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL_FAILED}
#     url = StringField(required=True)
#     reason = StringField()
