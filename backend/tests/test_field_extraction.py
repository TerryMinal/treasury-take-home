from app.services.extraction import extract_application_fields


def test_extracts_fields_from_ocr_text() -> None:
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

    extracted = extract_application_fields(text)

    assert extracted.brand_name == "OLD TOM DISTILLERY"
    assert extracted.class_type == "Kentucky Straight Bourbon Whiskey"
    assert extracted.abv == "45% Alc./Vol. (90 Proof)"
    assert extracted.net_contents == "750 mL"
    assert extracted.producer == "Bottled by Old Tom Distillery, Frankfort, KY"
    assert extracted.government_warning is not None
