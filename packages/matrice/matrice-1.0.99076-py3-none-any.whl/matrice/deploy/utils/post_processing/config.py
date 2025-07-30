APP_NAME_TO_USECASE = {
    "people_counting": "people_counting",
    "mask_detection": "mask_detection",
    "vehicle_type_monitoring": "vehicle_monitoring"
}

APP_NAME_TO_CATEGORY = {
    "people_counting": "general",
    "mask_detection": "mask_detection",
    "vehicle_type_monitoring": "traffic",
}

def get_usecase_from_app_name(app_name: str) -> str:
    normalized_app_name = app_name.lower().replace(" ", "_").replace("-", "_")
    return APP_NAME_TO_USECASE.get(app_name, APP_NAME_TO_USECASE.get(normalized_app_name))

def get_category_from_app_name(app_name: str) -> str:
    normalized_app_name = app_name.lower().replace(" ", "_").replace("-", "_")
    return APP_NAME_TO_CATEGORY.get(app_name, APP_NAME_TO_CATEGORY.get(normalized_app_name))
