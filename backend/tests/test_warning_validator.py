from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.models.schemas import BeverageType, ReviewStatus
from app.services.review import review_label


def test_review_marks_exact_warning_as_pass() -> None:
    label_text = f"""
    NAPA CELLARS
    Chardonnay
    California
    12.5% Alc. by Vol.
    750 mL
    Bottled by Napa Cellars, Napa, CA.
    {GOVERNMENT_WARNING_TEXT}
    """

    result = review_label("wine.txt", "text/plain", label_text.encode("utf-8"))

    warning_item = next(item for item in result.checklist_items if item.id == "government_warning")
    assert result.beverage_type == BeverageType.WINE
    assert warning_item.status == ReviewStatus.PASS


def test_review_marks_non_exact_warning_for_human_review() -> None:
    label_text = f"""
    NAPA CELLARS
    Chardonnay
    California
    12.5% Alc. by Vol.
    750 mL
    Bottled by Napa Cellars, Napa, CA.
    {GOVERNMENT_WARNING_TEXT.replace("GOVERNMENT WARNING:", "Government Warning:")}
    """

    result = review_label("wine.txt", "text/plain", label_text.encode("utf-8"))

    warning_item = next(item for item in result.checklist_items if item.id == "government_warning")
    assert warning_item.status == ReviewStatus.REVIEW
    assert "Government warning text did not match the required wording exactly" in warning_item.review_reasons
