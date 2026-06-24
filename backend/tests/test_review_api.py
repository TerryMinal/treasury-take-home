from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_review_endpoint_accepts_image_only_text_fixture_upload() -> None:
    label_text = """
    OLD TOM DISTILLERY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol. (90 Proof)
    750 mL
    Bottled by Old Tom Distillery, Frankfort, KY.
    GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during
    pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability
    to drive a car or operate machinery, and may cause health problems.
    """

    response = client.post(
        "/review",
        files={"label_file": ("label.txt", label_text, "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "label.txt"
    assert payload["checklist_items"]
    assert payload["overall_status"] == "review"
    assert payload["review_reasons"]


def test_review_endpoint_rejects_empty_file() -> None:
    response = client.post(
        "/review",
        files={"label_file": ("label.txt", "", "text/plain")},
    )

    assert response.status_code == 400
