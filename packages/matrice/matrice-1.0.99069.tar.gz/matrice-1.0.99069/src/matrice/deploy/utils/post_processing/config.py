APP_NAME_TO_USECASE = {
    "people_counting": "people_counting",
    "customer_service": "customer_service",
    "advanced_customer_service": "advanced_customer_service",
    "security": "security",
    "traffic": "traffic",
    "sales": "sales",
    "general": "general",
}

APP_NAME_TO_CATEGORY = {
    "people_counting": "general",
    "customer_service": "sales",
    "advanced_customer_service": "sales",
    "security": "security",
    "traffic": "traffic",
    "sales": "sales",
    "general": "general",
}

def get_usecase_from_app_name(app_name: str) -> str:
    normalized_app_name = app_name.lower().replace(" ", "_").replace("-", "_")
    return APP_NAME_TO_USECASE.get(app_name, APP_NAME_TO_USECASE.get(normalized_app_name))

def get_category_from_app_name(app_name: str) -> str:
    normalized_app_name = app_name.lower().replace(" ", "_").replace("-", "_")
    return APP_NAME_TO_CATEGORY.get(app_name, APP_NAME_TO_CATEGORY.get(normalized_app_name))
