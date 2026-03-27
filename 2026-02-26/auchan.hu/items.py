from mongoengine import DynamicDocument, StringField, BooleanField

class CategoryUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    link = StringField(unique=True)
    category_id = StringField()
    category_slug = StringField()
    is_leaf = BooleanField()
    path = StringField()
    main_category = StringField()

class ProductUrlItem(DynamicDocument):
    meta = {"db_alias": "default"}
    name = StringField()
    url = StringField(unique=True)
    sku = StringField()
    category_id = StringField()
    category_name = StringField()
    main_category = StringField()


# generic product item for validation/storage
class ProductItem(DynamicDocument):
    meta = {"db_alias": "default"}
    unique_id = StringField(unique=True)
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    brand_type = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    # hierarchy levels (1..7)
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
    currency = StringField()
    breadcrumb = StringField()
    pdp_url = StringField()
    product_description = StringField()
    country_of_origin = StringField()
    distributor_address = StringField()
    features = StringField()
    ingredients = StringField()
    nutritional_information = StringField()
    allergens = StringField()
    instock = StringField()
    image_url_1 = StringField()
    image_url_2 = StringField()
    image_url_3 = StringField()
    file_name_1 = StringField()
    file_name_2 = StringField()
    file_name_3 = StringField()
    random_weight_flag = StringField()
    promo_limit = StringField()
    retail_limit = StringField()
    upc = StringField()
    barcode = StringField()
