from app.models.schemas import ReviewField, ReviewStatus
from app.services.comparison import compare_field, normalize_abv, normalize_net_contents, normalize_text


def test_normalize_text_handles_punctuation_and_case() -> None:
    assert normalize_text("Stone's Throw") == normalize_text("STONE’S THROW")


def test_normalize_abv_handles_proof_equivalent() -> None:
    assert normalize_abv("45% Alc./Vol.") == normalize_abv("90 Proof")


def test_normalize_net_contents_handles_spacing() -> None:
    assert normalize_net_contents("750 mL") == normalize_net_contents("750ml")


def test_compare_field_marks_tolerant_match() -> None:
    review = compare_field(ReviewField.BRAND_NAME, "Stone's Throw", "STONE’S THROW")

    assert review.status == ReviewStatus.MATCH


def test_compare_field_marks_mismatch() -> None:
    review = compare_field(ReviewField.CLASS_TYPE, "Bourbon Whiskey", "Vodka")

    assert review.status == ReviewStatus.MISMATCH
