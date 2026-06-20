from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.models.schemas import ReviewField, ReviewStatus
from app.services.comparison import compare_field


def test_warning_matches_exact_text() -> None:
    review = compare_field(
        ReviewField.GOVERNMENT_WARNING,
        GOVERNMENT_WARNING_TEXT,
        GOVERNMENT_WARNING_TEXT,
    )

    assert review.status == ReviewStatus.MATCH


def test_warning_rejects_capitalization_change() -> None:
    review = compare_field(
        ReviewField.GOVERNMENT_WARNING,
        GOVERNMENT_WARNING_TEXT,
        GOVERNMENT_WARNING_TEXT.replace("GOVERNMENT WARNING:", "Government Warning:"),
    )

    assert review.status == ReviewStatus.MISMATCH
