from app.models.schemas import BeverageType
from app.services.extraction import detect_beverage_type, extract_label_data


def test_detects_distilled_spirits_and_extracts_key_fields() -> None:
    text = """
    OLD TOM DISTILLERY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol. (90 Proof)
    750 mL
    Bottled by Old Tom Distillery, Frankfort, KY.
    GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during
    pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability
    to drive a car or operate machinery, and may cause health problems.
    """

    beverage_type, _ = detect_beverage_type(text)
    extracted = extract_label_data(text, beverage_type)

    assert beverage_type == BeverageType.DISTILLED_SPIRITS
    assert extracted.brand_name == "OLD TOM DISTILLERY"
    assert extracted.designation == "Kentucky Straight Bourbon Whiskey"
    assert extracted.alcohol_content == "45% Alc./Vol. (90 Proof)"
    assert extracted.net_contents == "750 mL"
    assert extracted.name_and_address == "Bottled by Old Tom Distillery, Frankfort, KY"
    assert extracted.government_warning is not None


def test_detects_wine_from_varietal_terms() -> None:
    beverage_type, reason = detect_beverage_type("SONOMA VINEYARDS\nChardonnay\nCalifornia\n12.5% Alc. by Vol.")

    assert beverage_type == BeverageType.WINE
    assert reason is not None


def test_returns_none_when_beverage_type_is_ambiguous() -> None:
    beverage_type, reason = detect_beverage_type("Craft reserve beverage")

    assert beverage_type is None
    assert reason is not None
