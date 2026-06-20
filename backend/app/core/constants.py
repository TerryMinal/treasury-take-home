"""Business constants used across extraction and comparison logic."""

GOVERNMENT_WARNING_TEXT = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not "
    "drink alcoholic beverages during pregnancy because of the risk of birth "
    "defects. (2) Consumption of alcoholic beverages impairs your ability to "
    "drive a car or operate machinery, and may cause health problems."
)

FIELD_DISPLAY_NAMES: dict[str, str] = {
    "brand_name": "Brand Name",
    "class_type": "Class / Type",
    "abv": "Alcohol Content / ABV",
    "net_contents": "Net Contents",
    "producer": "Name and Address",
    "country_of_origin": "Country of Origin",
    "government_warning": "Government Warning",
}
