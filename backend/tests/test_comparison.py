from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.services.comparison import dedupe_review_reasons, normalize_abv, normalize_net_contents, normalize_text, warning_matches_exactly


def test_normalize_text_handles_punctuation_and_case() -> None:
    assert normalize_text("Stone's Throw") == normalize_text("STONE’S THROW")


def test_normalize_abv_handles_proof_equivalent() -> None:
    assert normalize_abv("45% Alc./Vol.") == normalize_abv("90 Proof")


def test_normalize_net_contents_handles_spacing() -> None:
    assert normalize_net_contents("750 mL") == normalize_net_contents("750ml")


def test_warning_match_requires_exact_text() -> None:
    assert warning_matches_exactly(GOVERNMENT_WARNING_TEXT) is True
    assert warning_matches_exactly(GOVERNMENT_WARNING_TEXT.replace("GOVERNMENT WARNING:", "Government Warning:")) is False


def test_dedupe_review_reasons_preserves_order() -> None:
    assert dedupe_review_reasons(["a", "b", "a", "", "c"]) == ["a", "b", "c"]
