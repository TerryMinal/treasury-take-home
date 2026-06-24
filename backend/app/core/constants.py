"""Business constants used across extraction and checklist evaluation."""

GOVERNMENT_WARNING_TEXT = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not "
    "drink alcoholic beverages during pregnancy because of the risk of birth "
    "defects. (2) Consumption of alcoholic beverages impairs your ability to "
    "drive a car or operate machinery, and may cause health problems."
)

BEVERAGE_TYPE_LABELS: dict[str, str] = {
    "wine": "Wine",
    "distilled_spirits": "Distilled Spirits",
    "malt_beverage": "Malt Beverage",
}
