from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_batch_endpoint_processes_multiple_files_without_json_payload() -> None:
    response = client.post(
        "/batch",
        files=[
            ("label_files", ("one.txt", "SONOMA VINEYARDS\nChardonnay\nCalifornia\n750 mL", "text/plain")),
            ("label_files", ("two.txt", "OLD TOM DISTILLERY\nBourbon Whiskey\n750 mL", "text/plain")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 2
    assert len(payload["results"]) == 2


def test_batch_status_returns_not_found_for_unknown_job() -> None:
    response = client.get("/batch/does-not-exist")

    assert response.status_code == 404
