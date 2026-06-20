from fastapi.testclient import TestClient

from app.core.constants import GOVERNMENT_WARNING_TEXT
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_review_endpoint_accepts_text_fixture_upload() -> None:
    label_text = f"""
    OLD TOM DISTILLERY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol. (90 Proof)
    750 mL
    Bottled by Old Tom Distillery, Frankfort, KY.
    {GOVERNMENT_WARNING_TEXT}
    """
    application_data = {
        "brand_name": "Old Tom Distillery",
        "class_type": "Kentucky Straight Bourbon Whiskey",
        "abv": "45% Alc./Vol.",
        "net_contents": "750ml",
        "producer": "Bottled by Old Tom Distillery, Frankfort, KY",
        "government_warning": GOVERNMENT_WARNING_TEXT,
    }

    response = client.post(
        "/review",
        files={"label_file": ("label.txt", label_text, "text/plain")},
        data={"application_data": __import__("json").dumps(application_data)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "label.txt"
    assert payload["fields"][0]["status"] == "match"


def test_review_endpoint_rejects_invalid_json() -> None:
    response = client.post(
        "/review",
        files={"label_file": ("label.txt", "sample", "text/plain")},
        data={"application_data": "{not-json}"},
    )

    assert response.status_code == 422
