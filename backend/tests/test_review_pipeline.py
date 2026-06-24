import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ReviewStatus
from app.services.review import review_label

client = TestClient(app)
FIXTURE_DIR = Path("backend/tests/fixtures/labels")


def _load_expected(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


def _upload_fixture(name: str) -> dict:
    path = FIXTURE_DIR / name
    content_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    response = client.post(
        "/review",
        files={"label_file": (path.name, path.read_bytes(), content_type)},
    )

    assert response.status_code == 200
    return response.json()


def test_pipeline_aggregates_item_review_reasons_without_duplicates() -> None:
    label_text = """
    UNKNOWN RESERVE
    Craft beverage
    750 mL
    Government Warning: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.
    """

    result = review_label("unclear.txt", "text/plain", label_text.encode("utf-8"))

    assert result.overall_status == ReviewStatus.REVIEW
    assert result.review_reasons
    assert len(result.review_reasons) == len(set(result.review_reasons))


def test_imported_malt_beverage_requires_importer_specific_statement() -> None:
    label_text = """
    HARBOR GOLD
    Lager
    Product of Germany
    500 mL
    Bottled by Harbor Gold Brewing Co., Milwaukee, WI.
    GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during
    pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability
    to drive a car or operate machinery, and may cause health problems.
    """

    result = review_label("imported-beer.txt", "text/plain", label_text.encode("utf-8"))

    importer_item = next(item for item in result.checklist_items if item.id == "importer_name_and_address")
    assert importer_item.status == ReviewStatus.REVIEW
    assert importer_item.evidence_text is not None
    assert importer_item.evidence_text.startswith("Bottled by Harbor Gold Brewing Co")


def test_review_endpoint_runs_full_png_pipeline_for_clean_fixture() -> None:
    expected = _load_expected("clean-readable-label.expected.json")
    payload = _upload_fixture("clean-readable-label.png")

    assert payload["filename"] == "clean-readable-label.png"
    assert payload["beverage_type"] == "distilled_spirits"
    assert payload["ocr"]["provider"] == "tesseract"
    assert payload["checklist_items"]
    assert payload["summary_counts"]["total"] == len(payload["checklist_items"])

    for anchor in expected["ocr_anchor_text"]:
        assert anchor in payload["ocr"]["text"]

    assert payload["extracted"]["brand_name"] == expected["expected_extracted_fields"]["brand_name"]
    assert payload["extracted"]["designation"] == expected["expected_extracted_fields"]["class_type"]
    assert payload["extracted"]["alcohol_content"] == expected["expected_extracted_fields"]["abv"]
    assert payload["extracted"]["net_contents"] == expected["expected_extracted_fields"]["net_contents"]
    assert payload["extracted"]["name_and_address"] == expected["expected_extracted_fields"]["producer"]
    assert "This rule depends on label layout and needs human confirmation" in payload["review_reasons"]


def test_review_endpoint_runs_full_png_pipeline_for_warning_fixture() -> None:
    expected = _load_expected("warning-capitalization-mismatch.expected.json")
    payload = _upload_fixture("warning-capitalization-mismatch.png")

    assert payload["filename"] == "warning-capitalization-mismatch.png"
    assert payload["ocr"]["provider"] == "tesseract"
    for anchor in expected["ocr_anchor_text"]:
        assert anchor in payload["ocr"]["text"]

    warning_item = next(item for item in payload["checklist_items"] if item["id"] == "government_warning")
    assert warning_item["status"] == "review"
    assert "Government warning text did not match the required wording exactly" in warning_item["review_reasons"]


def test_review_endpoint_runs_full_png_pipeline_for_low_quality_fixture() -> None:
    expected = _load_expected("low-quality-label.expected.json")
    payload = _upload_fixture("low-quality-label.png")

    assert payload["filename"] == "low-quality-label.png"
    assert payload["ocr"]["provider"] == "tesseract"
    assert payload["overall_status"] == "review"
    assert payload["review_reasons"]
    assert payload["ocr"]["preprocessing_steps"]
    assert len(payload["ocr"]["text"]) > 0
    for anchor in expected["ocr_anchor_text"]:
        assert anchor in payload["ocr"]["text"]


def test_review_endpoint_runs_full_jpeg_pipeline_for_real_fixture() -> None:
    payload = _upload_fixture("real_label_2_angle_view.jpeg")

    assert payload["filename"] == "real_label_2_angle_view.jpeg"
    assert payload["ocr"]["provider"] == "tesseract"
    assert payload["overall_status"] == "review"
    assert payload["review_reasons"]
    assert payload["checklist_items"]


def test_batch_endpoint_runs_full_pipeline_for_multiple_uploaded_images() -> None:
    files = []
    for name in ["clean-readable-label.png", "warning-capitalization-mismatch.png"]:
        path = FIXTURE_DIR / name
        files.append(("label_files", (name, path.read_bytes(), "image/png")))

    response = client.post("/batch", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 2
    assert payload["processed_count"] == 2
    assert len(payload["results"]) == 2
    assert all(item["status"] == "completed" for item in payload["results"])
    assert all(item["result"]["ocr"]["provider"] == "tesseract" for item in payload["results"])
