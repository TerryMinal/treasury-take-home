import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_batch_endpoint_processes_multiple_files() -> None:
    response = client.post(
        "/batch",
        files=[
            ("label_files", ("one.txt", "OLD TOM DISTILLERY\n750 mL", "text/plain")),
            ("label_files", ("two.txt", "STONE'S THROW\n750 mL", "text/plain")),
        ],
        data={"application_data": json.dumps([{"brand_name": "OLD TOM DISTILLERY"}, {"brand_name": "STONE'S THROW"}])},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 2
    assert len(payload["results"]) == 2


def test_batch_status_returns_not_found_for_unknown_job() -> None:
    response = client.get("/batch/does-not-exist")

    assert response.status_code == 404
